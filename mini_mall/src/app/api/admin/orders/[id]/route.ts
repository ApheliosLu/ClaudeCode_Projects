// 订单管理 API：PUT 状态流转（仅 ADMIN，白名单状态机）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { canTransition } from "@/lib/order-machine";
import type { OrderStatus } from "@/generated/prisma/enums";

const ALLOWED_STATUSES = ["SHIPPED", "DELIVERED", "CANCELLED"] as const;

/** PUT /api/admin/orders/[id] — 状态流转 { status, cancelReason? } */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const { id } = await params;
  const body = await request.json().catch(() => null);
  const status = body?.status as string;
  const cancelReason = (body?.cancelReason as string | undefined)?.trim() || null;

  if (!ALLOWED_STATUSES.includes(status as (typeof ALLOWED_STATUSES)[number])) {
    return NextResponse.json({ success: false, error: "无效的目标状态" }, { status: 400 });
  }
  if (status === "CANCELLED" && cancelReason === null) {
    return NextResponse.json(
      { success: false, error: "取消订单必须填写原因" },
      { status: 400 }
    );
  }

  const order = await prisma.order.findUnique({
    where: { id },
    include: { items: true },
  });
  if (!order) {
    return NextResponse.json({ success: false, error: "订单不存在" }, { status: 404 });
  }

  try {
    await prisma.$transaction(async (tx) => {
      const fresh = await tx.order.findUnique({ where: { id } });
      if (!fresh) throw new Error("订单不存在");
      if (!canTransition(fresh.status as OrderStatus, status as OrderStatus)) {
        throw new Error(`订单状态不允许从「${fresh.status}」流转到「${status}」`);
      }

      const now = new Date();
      const data: Record<string, unknown> = { status };
      if (status === "SHIPPED") data.shippedAt = now;
      if (status === "DELIVERED") data.deliveredAt = now;
      if (status === "CANCELLED") {
        data.cancelledAt = now;
        data.cancelReason = cancelReason;
        // 取消归还库存（按快照数量）
        for (const item of order.items) {
          await tx.product.update({
            where: { id: item.productId },
            data: { stock: { increment: item.quantity } },
          });
        }
      }

      // CAS 条件更新：where 带读到的原状态，并发流转时 count=0 回滚（防竞态）
      const updated = await tx.order.updateMany({
        where: { id, status: fresh.status },
        data,
      });
      if (updated.count !== 1) {
        throw new Error("订单状态已变化，请刷新后重试");
      }
    });
  } catch (e) {
    return NextResponse.json(
      { success: false, error: e instanceof Error ? e.message : "操作失败" },
      { status: 400 }
    );
  }

  return NextResponse.json({ success: true, data: { id } });
}
