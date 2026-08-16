// 订单状态徽章
import { Badge } from "@/components/ui/badge";
import { ORDER_STATUS_NAMES } from "@/lib/utils";
import type { OrderStatus } from "@/generated/prisma/enums";

const styles: Record<OrderStatus, string> = {
  PENDING: "bg-amber-100 text-amber-800 hover:bg-amber-100",
  PAID: "bg-blue-100 text-blue-800 hover:bg-blue-100",
  SHIPPED: "bg-purple-100 text-purple-800 hover:bg-purple-100",
  DELIVERED: "bg-green-100 text-green-800 hover:bg-green-100",
  CANCELLED: "bg-gray-200 text-gray-600 hover:bg-gray-200",
};

export function OrderStatusBadge({ status }: { status: OrderStatus }) {
  return (
    <Badge className={styles[status] ?? ""}>{ORDER_STATUS_NAMES[status] ?? status}</Badge>
  );
}
