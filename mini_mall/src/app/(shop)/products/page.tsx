// 商品列表：搜索 q / 分类 category / 排序 sort（searchParams 驱动，GET form + Link）
import Link from "next/link";
import { prisma } from "@/lib/prisma";
import { ProductCard } from "@/components/ProductCard";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

type SearchParams = Promise<{ q?: string; category?: string; sort?: string }>;

const sortOptions = [
  { value: "newest", label: "最新上架" },
  { value: "price-asc", label: "价格从低到高" },
  { value: "price-desc", label: "价格从高到低" },
];

export default async function ProductsPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const params = await searchParams;
  const q = params.q?.trim() ?? "";
  const categorySlug = params.category ?? "";
  const sort = params.sort ?? "newest";

  const where = {
    isActive: true,
    ...(q ? { name: { contains: q } } : {}),
    ...(categorySlug ? { category: { slug: categorySlug } } : {}),
  };

  const orderBy =
    sort === "price-asc"
      ? { priceCents: "asc" as const }
      : sort === "price-desc"
        ? { priceCents: "desc" as const }
        : { createdAt: "desc" as const };

  const [products, categories, currentCategory] = await Promise.all([
    prisma.product.findMany({
      where,
      include: { images: { orderBy: { sortOrder: "asc" } } },
      orderBy,
    }),
    prisma.category.findMany({ orderBy: { createdAt: "asc" } }),
    categorySlug
      ? prisma.category.findUnique({ where: { slug: categorySlug } })
      : null,
  ]);

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8">
      <h1 className="mb-4 text-xl font-semibold">
        {currentCategory ? currentCategory.name : "全部商品"}
      </h1>

      {/* 搜索框（GET 提交保持可分享 URL） */}
      <form action="/products" className="mb-4 flex max-w-md gap-2">
        <Input
          name="q"
          placeholder="搜索商品名称..."
          defaultValue={q}
          className="flex-1"
        />
        <Button type="submit" variant="outline">
          <Search className="mr-1 h-4 w-4" />
          搜索
        </Button>
      </form>

      {/* 分类筛选 */}
      <div className="mb-4 flex flex-wrap gap-2">
        <Link
          href={`/products${q ? `?q=${encodeURIComponent(q)}` : ""}`}
          className={`rounded-full border px-3 py-1 text-sm transition-colors ${
            !categorySlug ? "bg-primary text-primary-foreground" : "hover:bg-muted"
          }`}
        >
          全部
        </Link>
        {categories.map((c) => (
          <Link
            key={c.id}
            href={`/products?${new URLSearchParams({
              ...(q ? { q } : {}),
              category: c.slug,
            })}`}
            className={`rounded-full border px-3 py-1 text-sm transition-colors ${
              categorySlug === c.slug
                ? "bg-primary text-primary-foreground"
                : "hover:bg-muted"
            }`}
          >
            {c.name}
          </Link>
        ))}
      </div>

      {/* 排序 */}
      <div className="mb-6 flex gap-2 text-sm">
        <span className="py-1 text-muted-foreground">排序：</span>
        {sortOptions.map((opt) => (
          <Link
            key={opt.value}
            href={`/products?${new URLSearchParams({
              ...(q ? { q } : {}),
              ...(categorySlug ? { category: categorySlug } : {}),
              sort: opt.value,
            })}`}
            className={`rounded-md px-3 py-1 transition-colors ${
              sort === opt.value
                ? "bg-muted font-medium"
                : "text-muted-foreground hover:bg-muted"
            }`}
          >
            {opt.label}
          </Link>
        ))}
      </div>

      {products.length === 0 ? (
        <p className="py-16 text-center text-muted-foreground">
          没有找到匹配的商品，换个关键词试试？
        </p>
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}
