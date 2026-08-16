"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useCartStore } from "@/stores/cart";
import { createOrder } from "@/lib/actions/order";
import { formatCents } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useMounted } from "@/hooks/use-mounted";

export default function CheckoutPage() {
  const router = useRouter();
  const { items, clear, totalCents } = useCartStore();
  const mounted = useMounted();
  const [recipientName, setRecipientName] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("");
  const [shippingAddress, setShippingAddress] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!mounted) {
    return <div className="mx-auto w-full max-w-3xl px-4 py-8">加载中...</div>;
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto w-full max-w-3xl px-4 py-16 text-center text-muted-foreground">
        购物车是空的，无法结算
      </div>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const res = await createOrder({
      items: items.map((i) => ({ productId: i.productId, qty: i.qty })),
      recipientName,
      recipientPhone,
      shippingAddress,
    });

    if ("error" in res) {
      setError(res.error);
      setSubmitting(false);
      return;
    }
    clear();
    router.push(`/pay/${res.orderNo}`);
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-xl font-semibold">确认订单</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-6">
        {/* 收货信息 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">收货信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">收货人姓名</Label>
                <Input
                  id="name"
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                  placeholder="张三"
                  required
                  maxLength={50}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="phone">手机号</Label>
                <Input
                  id="phone"
                  type="tel"
                  value={recipientPhone}
                  onChange={(e) => setRecipientPhone(e.target.value)}
                  placeholder="13800138000"
                  required
                  maxLength={11}
                  pattern="1\d{10}"
                  title="请输入 11 位手机号"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="address">详细地址</Label>
              <Input
                id="address"
                value={shippingAddress}
                onChange={(e) => setShippingAddress(e.target.value)}
                placeholder="省 / 市 / 区 + 街道门牌号"
                required
                minLength={5}
                maxLength={200}
              />
            </div>
          </CardContent>
        </Card>

        {/* 商品清单 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">商品清单（{items.length} 种）</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {items.map((item) => (
              <div key={item.productId} className="flex items-center justify-between text-sm">
                <span className="line-clamp-1 flex-1">
                  {item.name} ×{item.qty}
                </span>
                <span className="ml-4 tabular-nums">
                  {formatCents(item.priceCents * item.qty)}
                </span>
              </div>
            ))}
            <div className="mt-3 border-t pt-3 text-sm text-muted-foreground">
              会员折扣将在下单时按等级自动应用
            </div>
          </CardContent>
        </Card>

        {error && (
          <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive" role="alert">
            {error}
          </p>
        )}

        <div className="flex items-center justify-end gap-4">
          <div className="text-right">
            <p className="text-sm text-muted-foreground">应付金额（折扣后以订单为准）</p>
            <p className="text-2xl font-bold text-red-600">{formatCents(totalCents())}</p>
          </div>
          <Button type="submit" size="lg" disabled={submitting}>
            {submitting ? "提交中..." : "提交订单"}
          </Button>
        </div>
      </form>
    </div>
  );
}
