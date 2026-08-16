// 商品卡片（首页/列表页通用）
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Price } from "@/components/Price";
// 自有 DTO 类型：不依赖 Prisma 生成类型（include 后的 relation 结构更可控）
type CardProduct = {
  id: string;
  name: string;
  slug: string;
  priceCents: number;
  stock: number;
  featured: boolean;
  images: { url: string }[];
};

export function ProductCard({ product }: { product: CardProduct }) {
  const cover = product.images[0]?.url;
  return (
    <Link href={`/products/${product.slug}`}>
      <Card className="group h-full overflow-hidden transition-shadow hover:shadow-md">
        <div className="relative aspect-square overflow-hidden bg-muted">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={cover ?? "/placeholder.svg"}
            alt={product.name}
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
          {product.featured && (
            <Badge className="absolute left-2 top-2 bg-red-600">精选</Badge>
          )}
          {product.stock === 0 && (
            <Badge variant="secondary" className="absolute right-2 top-2">
              缺货
            </Badge>
          )}
        </div>
        <CardContent className="p-3">
          <h3 className="line-clamp-2 text-sm font-medium leading-snug">
            {product.name}
          </h3>
        </CardContent>
        <CardFooter className="p-3 pt-0">
          <Price cents={product.priceCents} />
        </CardFooter>
      </Card>
    </Link>
  );
}
