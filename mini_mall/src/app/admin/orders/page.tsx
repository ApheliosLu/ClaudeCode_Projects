"use client";

// 订单管理：fetch GET /api/admin/orders（表格 + 状态筛选 + 流转按钮）
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { formatCents, ORDER_STATUS_NAMES } from "@/lib/utils";
import { OrderStatusBadge } from "@/components/OrderStatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const STATUS_FILTERS = ["", "PENDING", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"];

type OrderRow = {
  id: string;
  orderNo: string;
  status: string;
  totalCents: number;
  discountPercent: number;
  createdAt: string;
  recipientName: string;
  user: { name: string; email: string; membershipLevel: number };
  items: { id: string; name: string; quantity: number }[];
};

export default function AdminOrdersPage() {
  const router = useRouter();
  const [orders, setOrders] = useState<OrderRow[] | null>(null);
  const [statusFilter, setStatusFilter] = useState("");
  const [q, setQ] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    const url = `/api/admin/orders?${new URLSearchParams({
      ...(statusFilter ? { status: statusFilter } : {}),
      ...(q ? { q } : {}),
    })}`;
    const res = await fetch(url);
    const json = await res.json();
    if (!res.ok || !json.success) {
      setError(json.error ?? "加载失败");
      setOrders([]);
      return;
    }
    setOrders(json.data);
  }, [statusFilter, q]);

  useEffect(() => {
    load();
  }, [load]);

  /** 按状态机计算当前订单可执行的流转操作 */
  function availableActions(status: string) {
    switch (status) {
      case "PENDING":
        return [{ to: "CANCELLED", label: "取消订单", needsReason: true }];
      case "PAID":
        return [
          { to: "SHIPPED", label: "发货", needsReason: false },
          { to: "CANCELLED", label: "取消", needsReason: true },
        ];
      case "SHIPPED":
        return [
          { to: "DELIVERED", label: "完成", needsReason: false },
          { to: "CANCELLED", label: "取消", needsReason: true },
        ];
      default:
        return [];
    }
  }

  async function handleTransition(order: OrderRow, to: string, needsReason: boolean) {
    let cancelReason: string | null = null;
    if (needsReason) {
      cancelReason = prompt(`取消订单 ${order.orderNo} 的原因：`);
      if (cancelReason === null) return; // 用户点了取消
      if (!cancelReason.trim()) {
        alert("请填写取消原因");
        return;
      }
    }

    setBusyId(order.id);
    const res = await fetch(`/api/admin/orders/${order.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: to, cancelReason }),
    });
    const json = await res.json();
    setBusyId(null);
    if (!res.ok || !json.success) {
      alert(json.error ?? "操作失败");
      return;
    }
    load();
    router.refresh();
  }

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold">订单管理</h1>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatusFilter(s)}
            className={`rounded-full border px-3 py-1 text-sm transition-colors ${
              statusFilter === s
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
          >
            {s ? ORDER_STATUS_NAMES[s] ?? s : "全部"}
          </button>
        ))}
        <form
          action=""
          onSubmit={(e) => {
            e.preventDefault();
            load();
          }}
          className="ml-auto flex max-w-xs gap-2"
        >
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="订单号搜索"
          />
          <Button type="submit" variant="outline" size="sm">
            搜索
          </Button>
        </form>
      </div>

      {error && (
        <p className="mb-4 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      )}

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/60">
            <tr>
              <th className="px-3 py-2 text-left font-medium">订单号</th>
              <th className="px-3 py-2 text-left font-medium">买家</th>
              <th className="px-3 py-2 text-left font-medium">金额</th>
              <th className="px-3 py-2 text-left font-medium">状态</th>
              <th className="px-3 py-2 text-left font-medium">下单时间</th>
              <th className="px-3 py-2 text-right font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {orders === null ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-t">
                  <td colSpan={6} className="px-3 py-2">
                    <Skeleton className="h-6 w-full" />
                  </td>
                </tr>
              ))
            ) : orders.length === 0 ? (
              <tr className="border-t">
                <td colSpan={6} className="px-3 py-8 text-center text-muted-foreground">
                  暂无订单
                </td>
              </tr>
            ) : (
              orders.map((order) => (
                <tr key={order.id} className="border-t">
                  <td className="px-3 py-2 font-mono text-xs">{order.orderNo}</td>
                  <td className="px-3 py-2">
                    <p>{order.user.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {order.user.email}
                      {order.user.membershipLevel > 0 && (
                        <Badge className="ml-1 bg-amber-100 text-amber-800">
                          心悦{order.user.membershipLevel}
                        </Badge>
                      )}
                    </p>
                  </td>
                  <td className="px-3 py-2 tabular-nums">
                    {formatCents(order.totalCents)}
                    {order.discountPercent < 100 && (
                      <span className="ml-1 text-xs text-muted-foreground">
                        {order.discountPercent / 10}折
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-2">
                    <OrderStatusBadge status={order.status as never} />
                  </td>
                  <td className="px-3 py-2 text-xs text-muted-foreground">
                    {new Date(order.createdAt).toLocaleString("zh-CN")}
                  </td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex justify-end gap-1">
                      {availableActions(order.status).map((action) => (
                        <Button
                          key={action.to}
                          size="sm"
                          variant={action.to === "CANCELLED" ? "outline" : "default"}
                          className={
                            action.to === "CANCELLED" ? "text-destructive" : undefined
                          }
                          onClick={() =>
                            handleTransition(order, action.to, action.needsReason)
                          }
                          disabled={busyId === order.id}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
