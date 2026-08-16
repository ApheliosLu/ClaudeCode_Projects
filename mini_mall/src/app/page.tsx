// 首页：精选商品 + 分类入口
import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { ProductCard } from "@/components/ProductCard";
import { Button } from "@/components/ui/button";

export default async function HomePage() {
  const [featured, categories] = await Promise.all([
    prisma.product.findMany({
      where: { isActive: true, featured: true },
      include: { images: { orderBy: { sortOrder: "asc" } } },
      take: 8,
    }),
    prisma.category.findMany({ orderBy: { createdAt: "asc" } }),
  ]);

  return (
    <div className="mx-auto w-full max-w-6xl px-4">
      {/* Hero */}
      <section className="my-8 rounded-xl bg-gradient-to-r from-red-600 to-orange-500 p-10 text-white">
        <h1 className="text-3xl font-bold">mini_mall 微型电商</h1>
        <p className="mt-2 text-white/90">
          精选好物，会员享折上折。注册即逛，模拟支付，完整购物体验。
        </p>
        <Button variant="secondary" className="mt-4" render={<Link href="/products" />}>
          逛逛全部商品
        </Button>
      </section>

      {/* 分类入口 */}
      <section className="mb-8">
        <h2 className="mb-4 text-lg font-semibold">商品分类</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {categories.map((c) => (
            <Link
              key={c.id}
              href={`/products?category=${c.slug}`}
              className="rounded-lg border p-4 text-center transition-colors hover:bg-muted"
            >
              <div className="font-medium">{c.name}</div>
              <div className="mt-1 line-clamp-1 text-xs text-muted-foreground">
                {c.description}
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 精选商品 */}
      <section className="mb-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">精选商品</h2>
          <Link
            href="/products"
            className="text-sm text-primary hover:underline"
          >
            查看全部 →
          </Link>
        </div>
        {featured.length === 0 ? (
          <p className="py-8 text-center text-muted-foreground">暂无商品</p>
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {featured.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
