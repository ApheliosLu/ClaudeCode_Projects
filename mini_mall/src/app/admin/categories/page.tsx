"use client";

// 分类管理：列表（含商品数）+ 新增表单（fetch GET/POST/DELETE /api/admin/categories）
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Plus, Trash2 } from "lucide-react";
import { useMounted } from "@/hooks/use-mounted";

type CategoryRow = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  _count: { products: number };
};

export default function AdminCategoriesPage() {
  const router = useRouter();
  const [categories, setCategories] = useState<CategoryRow[] | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    const res = await fetch("/api/admin/categories");
    const json = await res.json();
    if (json.success) setCategories(json.data);
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- 数据获取模式：fetch 后 setState 是标准用法
    load();
  }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const url = editingId
      ? `/api/admin/categories/${editingId}`
      : "/api/admin/categories";
    const res = await fetch(url, {
      method: editingId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, slug, description }),
    });
    const json = await res.json();
    setSubmitting(false);
    if (!res.ok || !json.success) {
      setError(json.error ?? (editingId ? "保存失败" : "创建失败"));
      return;
    }
    setName("");
    setSlug("");
    setDescription("");
    setEditingId(null);
    load();
    router.refresh();
  }

  /** 点击编辑：把分类数据填入表单（表单进入编辑模式） */
  function startEdit(c: CategoryRow) {
    setEditingId(c.id);
    setName(c.name);
    setSlug(c.slug);
    setDescription(c.description ?? "");
    setError(null);
  }

  async function handleDelete(id: string, productCount: number) {
    if (productCount > 0) {
      alert(`该分类下还有 ${productCount} 个商品，请先移除商品`);
      return;
    }
    if (!confirm("确定删除该分类？")) return;
    setDeletingId(id);
    const res = await fetch(`/api/admin/categories/${id}`, { method: "DELETE" });
    const json = await res.json();
    setDeletingId(null);
    if (!res.ok || !json.success) {
      alert(json.error ?? "删除失败");
      return;
    }
    load();
    router.refresh();
  }

  return (
    <div>
      <h1 className="mb-4 text-lg font-semibold">分类管理</h1>

      {/* 新增/编辑表单 */}
      <form
        onSubmit={handleSubmit}
        className="mb-6 rounded-lg border p-4"
      >
        <p className="mb-3 text-sm font-medium">
          {editingId ? "编辑分类" : "新增分类"}
          {editingId && (
            <button
              type="button"
              onClick={() => {
                setEditingId(null);
                setName("");
                setSlug("");
                setDescription("");
              }}
              className="ml-2 text-xs text-muted-foreground hover:underline"
            >
              取消编辑
            </button>
          )}
        </p>
        <div className="grid gap-3 sm:grid-cols-3">
          <div className="space-y-1.5">
            <Label htmlFor="cat-name">分类名 *</Label>
            <Input
              id="cat-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              maxLength={50}
              placeholder="如：数码电子"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="cat-slug">slug *</Label>
            <Input
              id="cat-slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              required
              pattern="[a-z0-9-]+"
              title="只能包含小写字母、数字和连字符"
              maxLength={50}
              placeholder="如：digital"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="cat-desc">描述</Label>
            <Input
              id="cat-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              maxLength={200}
              placeholder="可选"
            />
          </div>
        </div>
        {error && (
          <p className="mt-3 text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        <Button type="submit" className="mt-3" disabled={submitting}>
          <Plus className="mr-1 h-4 w-4" />
          {submitting
            ? "保存中..."
            : editingId
              ? "保存修改"
              : "创建分类"}
        </Button>
      </form>

      {/* 分类列表 */}
      <div className="overflow-hidden rounded-lg border">
        <table className="w-full text-sm">
          <thead className="bg-muted/60">
            <tr>
              <th className="px-3 py-2 text-left font-medium">分类名</th>
              <th className="px-3 py-2 text-left font-medium">slug</th>
              <th className="px-3 py-2 text-left font-medium">描述</th>
              <th className="px-3 py-2 text-left font-medium">商品数</th>
              <th className="px-3 py-2 text-right font-medium">操作</th>
            </tr>
          </thead>
          <tbody>
            {categories === null ? (
              Array.from({ length: 3 }).map((_, i) => (
                <tr key={i} className="border-t">
                  <td colSpan={5} className="px-3 py-2">
                    <Skeleton className="h-6 w-full" />
                  </td>
                </tr>
              ))
            ) : categories.length === 0 ? (
              <tr className="border-t">
                <td colSpan={5} className="px-3 py-8 text-center text-muted-foreground">
                  暂无分类
                </td>
              </tr>
            ) : (
              categories.map((c) => (
                <tr key={c.id} className="border-t">
                  <td className="px-3 py-2 font-medium">{c.name}</td>
                  <td className="px-3 py-2 font-mono text-xs">{c.slug}</td>
                  <td className="px-3 py-2 text-muted-foreground">
                    {c.description ?? "—"}
                  </td>
                  <td className="px-3 py-2 tabular-nums">{c._count.products}</td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex justify-end gap-1">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => startEdit(c)}
                      >
                        编辑
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-destructive"
                        onClick={() => handleDelete(c.id, c._count.products)}
                        disabled={deletingId === c.id}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                        删除
                      </Button>
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
