"use client";

import Link from "next/link";
import { ShoppingCart } from "lucide-react";
import { useCartStore } from "@/stores/cart";
import { useMounted } from "@/hooks/use-mounted";

// 购物车图标 + 数量徽标（mounted 标志防水合闪烁：persist 数据仅在客户端存在）
export function CartBadge() {
  const count = useCartStore((s) => s.count());
  const mounted = useMounted();

  return (
    <Link
      href="/cart"
      className="relative rounded-md p-2 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
      aria-label="购物车"
    >
      <ShoppingCart className="h-5 w-5" />
      {mounted && count > 0 && (
        <span className="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-xs font-semibold text-white">
          {count}
        </span>
      )}
    </Link>
  );
}
