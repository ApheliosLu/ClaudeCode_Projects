// 新建商品：分类下拉数据来自 /api/admin/categories
"use client";

import { useEffect, useState } from "react";
import { ProductForm } from "@/components/admin/ProductForm";

export default function NewProductPage() {
  const [categories, setCategories] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    fetch("/api/admin/categories")
      .then((r) => r.json())
      .then((json) => {
        if (json.success) setCategories(json.data);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-4 text-lg font-semibold">新增商品</h1>
      <ProductForm categories={categories} />
    </div>
  );
}
