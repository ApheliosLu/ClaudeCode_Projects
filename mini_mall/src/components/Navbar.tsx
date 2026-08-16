// 顶部导航：Server Component 读 session 渲染用户区
import Link from "next/link";
import { getSession } from "@/lib/guards";
import { LogoutButton } from "@/components/LogoutButton";
import { CartBadge } from "@/components/CartBadge";
import { Button } from "@/components/ui/button";
import { Store } from "lucide-react";

export async function Navbar() {
  const session = await getSession();
  const isAdmin = session?.user.role === "ADMIN";

  return (
    <header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-6xl items-center gap-4 px-4">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg">
          <Store className="h-5 w-5 text-red-600" />
          mini_mall
        </Link>

        <nav className="flex flex-1 items-center gap-1">
          <Link
            href="/products"
            className="rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
          >
            全部商品
          </Link>
          {isAdmin && (
            <Link
              href="/admin"
              className="rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              管理后台
            </Link>
          )}
        </nav>

        <CartBadge />

        {session ? (
          <div className="flex items-center gap-2">
            <Link
              href="/orders"
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {session.user.name}
            </Link>
            <LogoutButton />
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" render={<Link href="/login" />}>
              登录
            </Button>
            <Button size="sm" render={<Link href="/register" />}>
              注册
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
