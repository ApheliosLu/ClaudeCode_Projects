// 商品详情页
import Link from "next/link";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import { ImageGallery } from "@/components/ImageGallery";
import { AddToCartButton } from "@/components/AddToCartButton";
import { Price } from "@/components/Price";
import { Badge } from "@/components/ui/badge";
import { ChevronRight } from "lucide-react";

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const product = await prisma.product.findUnique({
    where: { slug },
    include: {
      images: { orderBy: { sortOrder: "asc" } },
      category: true,
    },
  });

  if (!product || !product.isActive) {
    notFound();
  }

  const imageUrls = product.images.map((i) => i.url);

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8">
      {/* 面包屑 */}
      <nav className="mb-6 flex items-center gap-1 text-sm text-muted-foreground">
        <Link href="/" className="hover:text-foreground">
          首页
        </Link>
        <ChevronRight className="h-4 w-4" />
        <Link
          href={`/products?category=${product.category.slug}`}
          className="hover:text-foreground"
        >
          {product.category.name}
        </Link>
        <ChevronRight className="h-4 w-4" />
        <span className="text-foreground">{product.name}</span>
      </nav>

      <div className="grid gap-8 md:grid-cols-2">
        <ImageGallery images={imageUrls} name={product.name} />

        <div>
          <div className="mb-2 flex items-center gap-2">
            {product.featured && <Badge className="bg-red-600">精选</Badge>}
            {product.stock > 0 && product.stock <= 10 && (
              <Badge variant="secondary">仅剩 {product.stock} 件</Badge>
            )}
          </div>
          <h1 className="text-2xl font-bold">{product.name}</h1>

          <div className="mt-4">
            <Price cents={product.priceCents} className="text-2xl" />
            <p className="mt-1 text-sm text-muted-foreground">
              库存 {product.stock} 件
            </p>
          </div>

          <p className="mt-6 whitespace-pre-line text-sm leading-relaxed text-muted-foreground">
            {product.description}
          </p>

          <div className="mt-8">
            <AddToCartButton
              productId={product.id}
              slug={product.slug}
              name={product.name}
              priceCents={product.priceCents}
              image={imageUrls[0] ?? ""}
              stock={product.stock}
            />
          </div>

          <div className="mt-8 rounded-lg bg-muted/60 p-4 text-sm text-muted-foreground">
            <p className="font-medium text-foreground">会员权益</p>
            <ul className="mt-2 list-inside list-disc space-y-1">
              <li>心悦1级（累计 ¥8,000）：下单 9.8 折</li>
              <li>心悦2级（累计 ¥80,000）：下单 9.5 折</li>
              <li>心悦3级（累计 ¥800,000）：下单 9 折</li>
            </ul>
            <p className="mt-2 text-xs">
              当前展示为原价，结算时按会员等级自动折扣。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
