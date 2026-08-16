// 我的订单列表
import Link from "next/link";
import { requireAuth } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { formatCents } from "@/lib/utils";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default async function OrdersPage() {
  const session = await requireAuth();
  const orders = await prisma.order.findMany({
    where: { userId: session.user.id },
    include: { items: true },
    orderBy: { createdAt: "desc" },
    take: 50,
  });

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8">
      <h1 className="mb-6 text-xl font-semibold">我的订单</h1>

      {orders.length === 0 ? (
        <div className="py-16 text-center">
          <p className="text-muted-foreground">还没有订单</p>
          <Button className="mt-4" render={<Link href="/products" />}>
            去逛逛
          </Button>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {orders.map((order) => (
            <Link key={order.id} href={`/orders/${order.orderNo}`}>
              <Card className="flex items-center justify-between gap-4 p-4 transition-shadow hover:shadow-md">
                <div className="min-w-0">
                  <p className="font-mono text-sm">{order.orderNo}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {order.createdAt.toLocaleString("zh-CN")} · {order.items.length} 种商品
                    {order.discountPercent < 100 && (
                      <span className="ml-2 text-red-600">
                        （会员 {order.discountPercent / 10} 折）
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-4">
                  <span className="font-semibold text-red-600">
                    {formatCents(order.totalCents)}
                  </span>
                  <OrderStatusBadge status={order.status} />
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
