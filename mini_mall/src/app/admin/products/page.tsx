"use client";

// 商品管理列表：fetch GET /api/admin/products（表格 + 搜索 + 下架）
import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { formatCents } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Search } from "lucide-react";

type ProductRow = {
  id: string;
  name: string;
  slug: string;
  priceCents: number;
  stock: number;
  isActive: boolean;
  featured: boolean;
  images: { url: string }[];
  category: { name: string };
};

export default function AdminProductsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<ProductRow[] | null>(null);
  const [q, setQ] = useState("");
  const [all, setAll] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState<string | null>(null);

  const load = useCallback(async () => {
    setError(null);
    const url = `/api/admin/products?all=${all ? "1" : "0"}${
      q ? `&q=${encodeURIComponent(q)}` : ""
    }`;
    const res = await fetch(url);
    const json = await res.json();
    if (!res.ok || !json.success) {
      setError(json.error ?? "加载失败");
      setProducts([]);
      return;
    }
    setProducts(json.data);
  }, [q, all]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDelete(id: string) {
    if (!confirm("确定下架该商品？买家将无法购买（可在编辑中恢复上架）")) return;
    setDeleting(id);
    const res = await fetch(`/api/admin/products/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (!res.ok || !json.success) {
      alert(json.error ?? "操作失败");
      setDeleting(null);
      return;
    }
    setDeleting(null);
    load();
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold">商品管理</h1>
        <Button render={<Link href="/admin/products/new" />}>
          <Plus className="mr-1 h-4 w-4" />
          新增商品
        </Button>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <form
          action=""
          onSubmit={(e) => {
            e.preventDefault();
            load();
          }}
          className="flex max-w-sm flex-1 gap-2"
        >
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="搜索商品名称..."
          />
          <Button type="submit" variant="outline" size="icon">
            <Search className="h-4 w-4" />
          </Button>
        </form>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={all}
            onChange={(e) => setAll(e.target.checked)}
          />
          显示已下架
        </label>
      </div>

      {error && (
        <p className="mb-4 rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      )}

      <div className="overflow-x-auto rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/60">
            <tr>
              <th className="px-3 py-2 text-left font-medium">商品</th>
              <th className="px-3 py-2 text-left font-medium">分类</th>
              <th className="px-3 py-2 text-left font-medium">价格</th>
              <th className="px-3 py-2 text-left font-medium">库存</th>
              <th className="px-3 py-2 text-left font-medium">状态</th>
              <th className="px-3 py-2 text-right font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {products === null ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-t">
                  <td colSpan={6} className="px-3 py-2">
                    <Skeleton className="h-6 w-full" />
                  </td>
                </tr>
              ))
            ) : products.length === 0 ? (
              <tr className="border-t">
                <td colSpan={6} className="px-3 py-8 text-center text-muted-foreground">
                  暂无商品
                </td>
              </tr>
            ) : (
              products.map((p) => (
                <tr key={p.id} className="border-t">
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={p.images[0]?.url ?? ""}
                        alt={p.name}
                        className="h-9 w-9 shrink-0 rounded object-cover"
                      />
                      <div className="min-w-0">
                        <p className="line-clamp-1 font-medium">{p.name}</p>
                        <p className="font-mono text-xs text-muted-foreground">{p.slug}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-3 py-2">{p.category.name}</td>
                  <td className="px-3 py-2 tabular-nums">
                    {formatCents(p.priceCents)}
                    {p.featured && (
                      <Badge className="ml-1 bg-red-600 text-[10px]">精选</Badge>
                    )}
                  </td>
                  <td className="px-3 py-2 tabular-nums">{p.stock}</td>
                  <td className="px-3 py-2">
                    {p.isActive ? (
                      <Badge className="bg-green-100 text-green-800">在售</Badge>
                    ) : (
                      <Badge variant="secondary">已下架</Badge>
                    )}
                  </td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        size="sm"
                        variant="outline"
                        render={
                          <Link href={`/admin/products/${p.slug}/edit`} />
                        }
                      >
                        编辑
                      </Button>
                      {p.isActive && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-destructive"
                          onClick={() => handleDelete(p.id)}
                          disabled={deleting === p.id}
                        >
                          下架
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
