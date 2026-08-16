"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { cancelOrder } from "@/lib/actions/order";
import { Button } from "@/components/ui/button";

export function CancelOrderButton({ orderNo }: { orderNo: string }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  async function handleCancel() {
    setError(null);
    setCancelling(true);
    const res = await cancelOrder(orderNo);
    if ("error" in res) {
      setError(res.error);
      setCancelling(false);
      return;
    }
    router.refresh();
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <Button
        variant="outline"
        size="sm"
        onClick={handleCancel}
        disabled={cancelling}
      >
        {cancelling ? "取消中..." : "取消订单"}
      </Button>
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  );
}
