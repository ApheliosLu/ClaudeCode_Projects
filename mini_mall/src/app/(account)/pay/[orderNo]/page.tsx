// 模拟支付页：服务端预校验（登录 + 归属 + PENDING）
import Link from "next/link";
import { notFound } from "next/navigation";
import { requireAuth } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { formatCents } from "@/lib/utils";
import { PayForm } from "@/components/PayForm";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default async function PayPage({
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
  if (!order || order.userId !== session.user.id) {
    notFound();
  }

  // 非待支付状态：显示结果页
  if (order.status !== "PENDING") {
    const isPaid = order.status === "PAID" || order.status === "SHIPPED" || order.status === "DELIVERED";
    return (
      <div className="mx-auto w-full max-w-lg px-4 py-16 text-center">
        <h1 className="text-xl font-semibold">
          {isPaid ? "订单已支付" : "订单已关闭"}
        </h1>
        <div className="mt-4 flex justify-center">
          <OrderStatusBadge status={order.status} />
        </div>
        <Button className="mt-8" render={<Link href={`/orders/${orderNo}`} />}>
          查看订单详情
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-lg px-4 py-8">
      <h1 className="mb-6 text-xl font-semibold">收银台</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="text-base">订单 {order.orderNo}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {order.items.map((item) => (
            <div key={item.id} className="flex justify-between">
              <span className="line-clamp-1">
                {item.name} ×{item.quantity}
              </span>
              <span className="tabular-nums">{formatCents(item.subtotalCents)}</span>
            </div>
          ))}
          {order.discountPercent < 100 && (
            <div className="text-muted-foreground">
              会员折扣 {order.discountPercent / 10} 折已应用
            </div>
          )}
          <div className="flex justify-between border-t pt-3 font-semibold">
            <span>应付金额</span>
            <span className="text-2xl text-red-600">{formatCents(order.totalCents)}</span>
          </div>
        </CardContent>
      </Card>

      <PayForm orderNo={order.orderNo} totalCents={order.totalCents} />
    </div>
  );
}
