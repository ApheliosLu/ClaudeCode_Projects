"use client";

// 商品新增/编辑共享表单（POST /api/admin/products 或 PUT /api/admin/products/[id]）
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type CategoryOption = { id: string; name: string };

type ProductFormProps = {
  categories: CategoryOption[];
  initial?: {
    id: string;
    slug: string;
    name: string;
    description: string;
    priceCents: number;
    stock: number;
    categoryId: string;
    featured: boolean;
    isActive: boolean;
    images: { url: string }[];
  };
};

export function ProductForm({ categories, initial }: ProductFormProps) {
  const router = useRouter();
  const [name, setName] = useState(initial?.name ?? "");
  const [slug, setSlug] = useState(initial?.slug ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [price, setPrice] = useState(
    initial ? (initial.priceCents / 100).toString() : ""
  );
  const [stock, setStock] = useState(initial?.stock.toString() ?? "0");
  const [categoryId, setCategoryId] = useState(initial?.categoryId ?? "");
  const [images, setImages] = useState(
    initial ? initial.images.map((i) => i.url).join(", ") : ""
  );
  const [featured, setFeatured] = useState(initial?.featured ?? false);
  const [isActive, setIsActive] = useState(initial?.isActive ?? true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const payload = {
      name,
      slug,
      description,
      priceYuan: price,
      stock: Number(stock),
      categoryId,
      images,
      featured,
      isActive,
    };

    const url = initial ? `/api/admin/products/${initial.slug}` : "/api/admin/products";
    const res = await fetch(url, {
      method: initial ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const json = await res.json().catch(() => null);

    if (!res.ok || !json?.success) {
      setError(json?.error ?? "保存失败，请稍后重试");
      setSubmitting(false);
      return;
    }
    router.push("/admin/products");
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit}>
      <Card>
        <CardContent className="space-y-4 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">商品名称 *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                maxLength={100}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="slug">slug（URL 标识）*</Label>
              <Input
                id="slug"
                value={slug}
                onChange={(e) => setSlug(e.target.value)}
                required
                pattern="[a-z0-9-]+"
                title="只能包含小写字母、数字和连字符"
                maxLength={100}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="price">价格（元）*</Label>
              <Input
                id="price"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
                pattern="\d+(\.\d{1,2})?"
                inputMode="decimal"
                placeholder="99.00"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="stock">库存 *</Label>
              <Input
                id="stock"
                type="number"
                min={0}
                value={stock}
                onChange={(e) => setStock(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="category">分类 *</Label>
              <select
                id="category"
                value={categoryId}
                onChange={(e) => setCategoryId(e.target.value)}
                required
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="">请选择分类</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="description">商品描述</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                maxLength={2000}
                placeholder="商品特性、材质、规格等"
              />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="images">图片 URL（逗号分隔）</Label>
              <Input
                id="images"
                value={images}
                onChange={(e) => setImages(e.target.value)}
                placeholder="https://picsum.photos/seed/xxx/600/600, https://..."
              />
              <p className="text-xs text-muted-foreground">第一张作为封面图</p>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={featured}
                onChange={(e) => setFeatured(e.target.checked)}
              />
              精选（首页展示）
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
              />
              上架（取消勾选则下架）
            </label>
          </div>

          {error && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
        </CardContent>
        <CardFooter className="justify-end gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/admin/products")}
          >
            取消
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? "保存中..." : "保存"}
          </Button>
        </CardFooter>
      </Card>
    </form>
  );
}
