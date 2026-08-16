// 订单相关 Server Actions
// 统一约定：成功返回数据对象；失败返回 { error: string }
"use server";

import { revalidatePath } from "next/cache";
import { prisma } from "@/lib/prisma";
import { requireAuth } from "@/lib/guards";
import { createOrderSchema, mockPaySchema } from "@/lib/validators";
import { getTier, applyDiscount, getUpgradedLevel } from "@/lib/membership";
import { canTransition } from "@/lib/order-machine";
import { genOrderNo } from "@/lib/utils";
import type { OrderStatus } from "@/generated/prisma/enums";

export type ActionResult = { error: string } | { orderNo: string };

/** 下单：服务端按 DB 重算单价/库存 → 应用会员折扣 → 原子扣库存 → 事务建订单+快照 */
export async function createOrder(input: unknown): Promise<ActionResult> {
  const session = await requireAuth();

  const parsed = createOrderSchema.safeParse(input);
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "参数错误" };
  }
  const { items, recipientName, recipientPhone, shippingAddress } = parsed.data;

  // 会员折扣（按当前等级，订单快照 discountPercent）
  const user = await prisma.user.findUnique({ where: { id: session.user.id } });
  if (!user) return { error: "用户不存在" };
  const discountPercent = getTier(user.membershipLevel).discountPercent;

  try {
    // 服务端重算：只取在售商品
    const productIds = [...new Set(items.map((i) => i.productId))];
    const products = await prisma.product.findMany({
      where: { id: { in: productIds }, isActive: true },
    });
    const productMap = new Map(products.map((p) => [p.id, p]));

    const orderItems = items.map((item) => {
      const p = productMap.get(item.productId);
      if (!p) throw new Error("商品不存在或已下架");
      if (p.stock < item.qty) {
        throw new Error(`「${p.name}」库存不足（仅剩 ${p.stock} 件）`);
      }
      const unitCents = applyDiscount(p.priceCents, discountPercent);
      return {
        productId: p.id,
        name: p.name, // 快照
        priceCents: unitCents, // 折扣后单价快照
        quantity: item.qty,
        subtotalCents: unitCents * item.qty,
      };
    });

    const totalCents = orderItems.reduce((s, i) => s + i.subtotalCents, 0);
    const orderNo = genOrderNo();

    await prisma.$transaction(async (tx) => {
      // 逐项原子扣库存（stock >= qty 条件保证不超卖，count=0 表示并发下被抢光）
      for (const item of items) {
        const result = await tx.product.updateMany({
          where: { id: item.productId, stock: { gte: item.qty } },
          data: { stock: { decrement: item.qty } },
        });
        if (result.count === 0) {
          const p = productMap.get(item.productId);
          throw new Error(`「${p?.name ?? "商品"}」库存不足`);
        }
      }

      await tx.order.create({
        data: {
          orderNo,
          userId: user.id,
          status: "PENDING",
          totalCents,
          discountPercent,
          recipientName,
          recipientPhone,
          shippingAddress,
          items: { create: orderItems },
        },
      });
    });

    revalidatePath("/products", "layout"); // 刷新列表/详情库存
    return { orderNo };
  } catch (e) {
    // 事务已回滚（库存自动还原）
    return { error: e instanceof Error ? e.message : "下单失败，请稍后重试" };
  }
}

/** 模拟支付：PENDING → PAID，事务内累加会员累计金额并升级（只升不降） */
export async function mockPay(input: unknown): Promise<ActionResult> {
  const session = await requireAuth();

  const parsed = mockPaySchema.safeParse(input);
  if (!parsed.success) {
    return { error: parsed.error.issues[0]?.message ?? "参数错误" };
  }
  const { orderNo, channel } = parsed.data;

  // 归属校验（复用支付页同样的校验）
  const order = await prisma.order.findUnique({ where: { orderNo } });
  if (!order || order.userId !== session.user.id) {
    return { error: "订单不存在" };
  }

  try {
    // 模拟支付网关延迟
    await new Promise((r) => setTimeout(r, 1200));

    await prisma.$transaction(async (tx) => {
      // 状态机校验（事务内重查，防并发）
      const fresh = await tx.order.findUnique({ where: { orderNo } });
      if (!fresh) throw new Error("订单不存在");
      if (!canTransition(fresh.status as OrderStatus, "PAID")) {
        throw new Error("当前订单状态不允许支付");
      }

      await tx.order.update({
        where: { orderNo },
        data: { status: "PAID", paidAt: new Date(), paymentChannel: channel },
      });

      // 会员：累计实付累加 + 按阈值升级（只升不降）
      const user = await tx.user.findUnique({ where: { id: session.user.id } });
      if (!user) throw new Error("用户不存在");
      const newAccumulated = user.accumulatedSpentCents + fresh.totalCents;
      const newLevel = getUpgradedLevel(newAccumulated);
      await tx.user.update({
        where: { id: user.id },
        data: {
          accumulatedSpentCents: newAccumulated,
          ...(newLevel > user.membershipLevel ? { membershipLevel: newLevel } : {}),
        },
      });
    });
  } catch (e) {
    return { error: e instanceof Error ? e.message : "支付失败，请稍后重试" };
  }

  revalidatePath(`/orders/${orderNo}`);
  revalidatePath("/membership");
  return { orderNo };
}

/** 买家取消订单：仅 PENDING 可取消，事务内归还库存（累计金额不回退） */
export async function cancelOrder(orderNo: string): Promise<ActionResult> {
  const session = await requireAuth();

  const order = await prisma.order.findUnique({
    where: { orderNo },
    include: { items: true },
  });
  if (!order || order.userId !== session.user.id) {
    return { error: "订单不存在" };
  }

  try {
    await prisma.$transaction(async (tx) => {
      const fresh = await tx.order.findUnique({ where: { orderNo } });
      if (!fresh) throw new Error("订单不存在");
      if (!canTransition(fresh.status as OrderStatus, "CANCELLED")) {
        throw new Error("当前订单状态不允许取消");
      }

      await tx.order.update({
        where: { orderNo },
        data: { status: "CANCELLED", cancelledAt: new Date() },
      });

      // 归还库存（按快照数量）
      for (const item of order.items) {
        await tx.product.update({
          where: { id: item.productId },
          data: { stock: { increment: item.quantity } },
        });
      }
    });
  } catch (e) {
    return { error: e instanceof Error ? e.message : "取消失败，请稍后重试" };
  }

  revalidatePath(`/orders/${orderNo}`);
  revalidatePath("/products", "layout");
  return { orderNo };
}
