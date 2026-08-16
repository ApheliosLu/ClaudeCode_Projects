"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCartStore } from "@/stores/cart";
import { formatCents } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Trash2 } from "lucide-react";
import { useMounted } from "@/hooks/use-mounted";

export default function CartPage() {
  const router = useRouter();
  const { items, setQty, remove, clear, totalCents } = useCartStore();
  const mounted = useMounted();

  // 未挂载时渲染空壳，避免 persist 水合闪烁
  if (!mounted) {
    return <div className="mx-auto w-full max-w-4xl px-4 py-8">加载中...</div>;
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto w-full max-w-4xl px-4 py-16 text-center">
        <h1 className="text-xl font-semibold">购物车是空的</h1>
        <p className="mt-2 text-muted-foreground">快去挑选心仪的商品吧</p>
        <Button className="mt-6" render={<Link href="/products" />}>
          去逛逛
        </Button>
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-xl font-semibold">购物车（{items.length} 种商品）</h1>
        <button
          type="button"
          onClick={clear}
          className="text-sm text-muted-foreground hover:text-destructive"
        >
          清空购物车
        </button>
      </div>

      <div className="flex flex-col gap-3">
        {items.map((item) => (
          <Card key={item.productId} className="flex items-center gap-4 p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={item.image}
              alt={item.name}
              className="h-20 w-20 shrink-0 rounded-md object-cover"
            />
            <div className="min-w-0 flex-1">
              <Link
                href={`/products/${item.slug}`}
                className="line-clamp-1 font-medium hover:underline"
              >
                {item.name}
              </Link>
              <p className="mt-1 text-sm text-red-600">
                {formatCents(item.priceCents)}
              </p>
            </div>

            <div className="flex items-center rounded-md border">
              <button
                type="button"
                onClick={() => setQty(item.productId, item.qty - 1)}
                className="px-2.5 py-1.5 text-base hover:bg-muted"
                aria-label="减少"
              >
                −
              </button>
              <span className="w-10 text-center tabular-nums">{item.qty}</span>
              <button
                type="button"
                onClick={() => setQty(item.productId, item.qty + 1)}
                className="px-2.5 py-1.5 text-base hover:bg-muted"
                aria-label="增加"
              >
                +
              </button>
            </div>

            <button
              type="button"
              onClick={() => remove(item.productId)}
              className="p-2 text-muted-foreground transition-colors hover:text-destructive"
              aria-label={`删除 ${item.name}`}
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </Card>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-between rounded-lg bg-muted/60 p-4">
        <div>
          <p className="text-sm text-muted-foreground">合计（会员折扣结算时生效）</p>
          <p className="text-2xl font-bold text-red-600">
            {formatCents(totalCents())}
          </p>
        </div>
        <Button size="lg" onClick={() => router.push("/checkout")}>
          去结算
        </Button>
      </div>
    </div>
  );
}
