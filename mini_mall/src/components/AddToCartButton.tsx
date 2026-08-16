"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useCartStore } from "@/stores/cart";
import { Button } from "@/components/ui/button";
import { ShoppingCart } from "lucide-react";

type AddToCartProps = {
  productId: string;
  slug: string;
  name: string;
  priceCents: number;
  image: string;
  stock: number;
};

export function AddToCartButton({
  productId,
  slug,
  name,
  priceCents,
  image,
  stock,
}: AddToCartProps) {
  const add = useCartStore((s) => s.add);
  const [qty, setQty] = useState(1);
  const outOfStock = stock <= 0;

  function handleAdd() {
    add({ productId, slug, name, priceCents, image }, qty);
    toast.success(`已加入购物车：${name} ×${qty}`);
  }

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center rounded-md border">
        <button
          type="button"
          onClick={() => setQty((q) => Math.max(1, q - 1))}
          className="px-3 py-2 text-lg hover:bg-muted disabled:opacity-40"
          disabled={outOfStock}
          aria-label="减少数量"
        >
          −
        </button>
        <span className="w-10 text-center tabular-nums">{qty}</span>
        <button
          type="button"
          onClick={() => setQty((q) => Math.min(stock, q + 1))}
          className="px-3 py-2 text-lg hover:bg-muted disabled:opacity-40"
          disabled={outOfStock}
          aria-label="增加数量"
        >
          +
        </button>
      </div>
      <Button onClick={handleAdd} disabled={outOfStock} size="lg">
        <ShoppingCart className="mr-2 h-4 w-4" />
        {outOfStock ? "暂时缺货" : "加入购物车"}
      </Button>
    </div>
  );
}
