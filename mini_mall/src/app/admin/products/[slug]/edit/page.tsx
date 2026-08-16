// 编辑商品：加载现有数据填充表单（以 slug 定位）
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ProductForm } from "@/components/admin/ProductForm";
import { Skeleton } from "@/components/ui/skeleton";

type EditPayload = {
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

export default function EditProductPage() {
  const params = useParams<{ slug: string }>();
  const [product, setProduct] = useState<EditPayload | null>(null);
  const [categories, setCategories] = useState<{ id: string; name: string }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([
      fetch(`/api/admin/products/${params.slug}`),
      fetch("/api/admin/categories"),
    ])
      .then(async ([pRes, cRes]) => {
        const pJson = await pRes.json();
        const cJson = await cRes.json();
        if (cancelled) return;
        if (!pRes.ok || !pJson.success) {
          setError(pJson.error ?? "商品不存在");
          return;
        }
        setProduct(pJson.data);
        if (cJson.success) setCategories(cJson.data);
      })
      .catch(() => !cancelled && setError("加载失败"));
    return () => {
      cancelled = true;
    };
  }, [params.slug]);

  if (error) {
    return <p className="text-destructive">{error}</p>;
  }

  if (!product) {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-4 text-lg font-semibold">编辑商品：{product.name}</h1>
      <ProductForm categories={categories} initial={product} />
    </div>
  );
}
