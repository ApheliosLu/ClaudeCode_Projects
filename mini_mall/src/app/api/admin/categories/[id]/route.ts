// 分类管理 API：DELETE（仅 ADMIN；有商品引用的分类拒绝删除）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";

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
