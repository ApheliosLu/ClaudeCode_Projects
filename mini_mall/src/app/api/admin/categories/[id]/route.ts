// 分类管理 API：PUT 更新 + DELETE（仅 ADMIN；有商品引用的分类拒绝删除）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { categorySchema } from "@/lib/validators";

/** PUT /api/admin/categories/[id] — 更新分类 */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const { id } = await params;
  const existing = await prisma.category.findUnique({ where: { id } });
  if (!existing) {
    return NextResponse.json({ success: false, error: "分类不存在" }, { status: 404 });
  }

  const body = await request.json().catch(() => null);
  const parsed = categorySchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { success: false, error: parsed.error.issues[0]?.message ?? "参数错误" },
      { status: 400 }
    );
  }
  const { name, slug, description } = parsed.data;

  const slugExists = await prisma.category.findUnique({ where: { slug } });
  if (slugExists && slugExists.id !== id) {
    return NextResponse.json({ success: false, error: "slug 已存在" }, { status: 400 });
  }

  const category = await prisma.category.update({
    where: { id },
    data: { name, slug, description: description || null },
  });

  return NextResponse.json({ success: true, data: category });
}

/** DELETE /api/admin/categories/[id] — 删除分类（校验无商品引用） */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const { id } = await params;
  const category = await prisma.category.findUnique({
    where: { id },
    include: { _count: { select: { products: true } } },
  });
  if (!category) {
    return NextResponse.json({ success: false, error: "分类不存在" }, { status: 404 });
  }
  if (category._count.products > 0) {
    return NextResponse.json(
      {
        success: false,
        error: `该分类下还有 ${category._count.products} 个商品，请先移除商品`,
      },
      { status: 400 }
    );
  }

  await prisma.category.delete({ where: { id } });
  return NextResponse.json({ success: true, data: { id } });
}
