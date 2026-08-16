// 订单详情：归属校验 + 商品快照 + 金额明细（PENDING 显示去支付入口）
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireAuth } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { formatCents } from "@/lib/utils";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default async function OrderDetailPage({
  params,
}: {
  params: Promise<{ orderNo: string }>;
}) {
  const { orderNo } = await params;
  const session = await requireAuth();

  const order = await prisma.order.findUnique({
    where: { orderNo },
    include: { items: true },
  });

  // 归属校验：只能看自己的订单
  if (!order || order.userId !== session.user.id) {
    notFound();
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">订单详情</h1>
          <p className="mt-1 font-mono text-sm text-muted-foreground">{order.orderNo}</p>
        </div>
        <OrderStatusBadge status={order.status} />
      </div>

      {order.status === "PENDING" && (
        <div className="mb-6 flex items-center justify-between rounded-lg bg-amber-50 p-4">
          <p className="text-sm text-amber-800">订单待支付，支付成功后开始发货流程</p>
          <Button size="sm" render={<Link href={`/pay/${order.orderNo}`} />}>
            去支付
          </Button>
        </div>
      )}

      <div className="flex flex-col gap-6">
        {/* 商品清单 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">商品清单</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {order.items.map((item) => (
              <div key={item.id} className="flex items-center justify-between text-sm">
                <div>
                  <p>{item.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {formatCents(item.priceCents)} × {item.quantity}
                  </p>
                </div>
                <span className="tabular-nums">
                  {formatCents(item.subtotalCents)}
                </span>
              </div>
            ))}
            <div className="border-t pt-3 text-sm">
              {order.discountPercent < 100 && (
                <div className="flex justify-between text-muted-foreground">
                  <span>会员折扣（{order.discountPercent / 10} 折）</span>
                  <span>已含于单价</span>
                </div>
              )}
              <div className="mt-1 flex justify-between font-semibold">
                <span>实付金额</span>
                <span className="text-red-600">{formatCents(order.totalCents)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 收货信息 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">收货信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <p>
              {order.recipientName} · {order.recipientPhone}
            </p>
            <p className="text-muted-foreground">{order.shippingAddress}</p>
            <p className="pt-2 text-xs text-muted-foreground">
              下单时间：{order.createdAt.toLocaleString("zh-CN")}
              {order.paidAt && ` · 支付时间：${order.paidAt.toLocaleString("zh-CN")}`}
              {order.paymentChannel && ` · 支付渠道：${order.paymentChannel}`}
              {order.cancelReason && ` · 取消原因：${order.cancelReason}`}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
