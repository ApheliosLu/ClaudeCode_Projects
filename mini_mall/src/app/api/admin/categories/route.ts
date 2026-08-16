// 分类管理 API：GET 列表 + POST 创建（仅 ADMIN）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { categorySchema } from "@/lib/validators";

/** GET /api/admin/categories — 分类列表（含商品数） */
export async function GET() {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const categories = await prisma.category.findMany({
    include: { _count: { select: { products: true } } },
    orderBy: { createdAt: "asc" },
  });

  return NextResponse.json({ success: true, data: categories });
}

/** POST /api/admin/categories — 创建分类 */
export async function POST(request: NextRequest) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
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
  if (slugExists) {
    return NextResponse.json({ success: false, error: "slug 已存在" }, { status: 400 });
  }

  const category = await prisma.category.create({
    data: { name, slug, description: description || null },
  });

  return NextResponse.json({ success: true, data: category }, { status: 201 });
}
