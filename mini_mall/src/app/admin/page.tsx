// 管理端仪表盘：订单/销售额/用户统计 + 最近订单
import Link from "next/link";
import { requireAdmin } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { formatCents, ORDER_STATUS_NAMES } from "@/lib/utils";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { OrderStatus } from "@/generated/prisma/enums";

export default async function AdminDashboardPage() {
  await requireAdmin();

  const [orderCounts, salesAgg, productCount, userCount, recentOrders] =
    await Promise.all([
      prisma.order.groupBy({ by: ["status"], _count: { _all: true } }),
      prisma.order.aggregate({
        where: { status: { in: ["PAID", "SHIPPED", "DELIVERED"] } },
        _sum: { totalCents: true },
      }),
      prisma.product.count(),
      prisma.user.count(),
      prisma.order.findMany({
        include: { user: { select: { name: true } } },
        orderBy: { createdAt: "desc" },
        take: 10,
      }),
    ]);

  const statusMap = Object.fromEntries(
    orderCounts.map((o) => [o.status, o._count._all])
  ) as Record<OrderStatus, number>;
  const totalOrders = orderCounts.reduce((s, o) => s + o._count._all, 0);
  const totalSales = salesAgg._sum.totalCents ?? 0;

  const stats = [
    { label: "订单总数", value: String(totalOrders) },
    { label: "销售总额", value: formatCents(totalSales) },
    { label: "商品数", value: String(productCount) },
    { label: "用户数", value: String(userCount) },
  ];

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold">仪表盘</h1>

      <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
        {stats.map((s) => (
          <Card key={s.label}>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">{s.label}</p>
              <p className="mt-1 text-2xl font-bold">{s.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="mb-6 grid gap-3 sm:grid-cols-3">
        {Object.entries(ORDER_STATUS_NAMES).map(([status, label]) => (
          <Card key={status}>
            <CardContent className="flex items-center justify-between p-4">
              <span className="text-sm">{label}</span>
              <span className="text-lg font-semibold">
                {statusMap[status as OrderStatus] ?? 0}
              </span>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">最近 10 笔订单</CardTitle>
        </CardHeader>
        <CardContent>
          {recentOrders.length === 0 ? (
            <p className="py-4 text-center text-sm text-muted-foreground">暂无订单</p>
          ) : (
            <div className="space-y-2">
              {recentOrders.map((order) => (
                <Link
                  key={order.id}
                  href={`/admin/orders`}
                  className="flex items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-muted"
                >
                  <span className="font-mono text-xs">{order.orderNo}</span>
                  <span className="text-muted-foreground">{order.user.name}</span>
                  <span className="tabular-nums">{formatCents(order.totalCents)}</span>
                  <OrderStatusBadge status={order.status} />
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
