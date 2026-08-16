// 管理端：服务端角色校验（ADMIN）+ 侧边栏
import Link from "next/link";
import { requireAdmin } from "@/lib/guards";

const navItems = [
  { href: "/admin", label: "仪表盘" },
  { href: "/admin/products", label: "商品管理" },
  { href: "/admin/orders", label: "订单管理" },
  { href: "/admin/categories", label: "分类管理" },
];

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await requireAdmin();
  return (
    <div className="mx-auto flex min-h-[80vh] w-full max-w-6xl">
      <aside className="w-48 shrink-0 border-r p-4">
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="min-w-0 flex-1 p-6">{children}</main>
    </div>
  );
}
