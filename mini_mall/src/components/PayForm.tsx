"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { mockPay } from "@/lib/actions/order";
import { formatCents } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CreditCard, MessageSquareText, Landmark } from "lucide-react";

const channels = [
  { value: "alipay", label: "支付宝", icon: CreditCard },
  { value: "wechat", label: "微信支付", icon: MessageSquareText },
  { value: "unionpay", label: "银联支付", icon: Landmark },
] as const;

export function PayForm({ orderNo, totalCents }: { orderNo: string; totalCents: number }) {
  const router = useRouter();
  const [channel, setChannel] = useState<(typeof channels)[number]["value"]>("alipay");
  const [paying, setPaying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handlePay() {
    setError(null);
    setPaying(true);
    const res = await mockPay({ orderNo, channel });
    if ("error" in res) {
      setError(res.error);
      setPaying(false);
      return;
    }
    router.push(`/orders/${orderNo}?paid=1`);
    router.refresh();
  }

  return (
    <div>
      <Card className="mb-4">
        <CardContent className="space-y-3 p-4">
          {channels.map((c) => {
            const Icon = c.icon;
            const selected = channel === c.value;
            return (
              <button
                key={c.value}
                type="button"
                onClick={() => setChannel(c.value)}
                className={`flex w-full items-center gap-3 rounded-lg border p-3 text-left transition-colors ${
                  selected
                    ? "border-primary bg-primary/5 ring-1 ring-primary"
                    : "hover:bg-muted"
                }`}
              >
                <Icon className={`h-5 w-5 ${selected ? "text-primary" : "text-muted-foreground"}`} />
                <span className="flex-1 font-medium">{c.label}</span>
                <span
                  className={`h-4 w-4 rounded-full border ${
                    selected ? "border-primary bg-primary" : "border-input"
                  }`}
                />
              </button>
            );
          })}
        </CardContent>
      </Card>

      {error && (
        <p className="mb-4 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      <Button className="w-full" size="lg" onClick={handlePay} disabled={paying}>
        {paying ? "支付中（模拟网关延迟）..." : `确认支付 ${formatCents(totalCents)}`}
      </Button>
      <p className="mt-3 text-center text-xs text-muted-foreground">
        模拟支付，不产生真实交易
      </p>
    </div>
  );
}
