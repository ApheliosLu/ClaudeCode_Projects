// 商品管理 API：GET 列表 + POST 创建（仅 ADMIN）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { productSchema } from "@/lib/validators";
import { toCents } from "@/lib/utils";

/** GET /api/admin/products?q=&all=1 — 列表（默认仅上架，all=1 含下架） */
export async function GET(request: NextRequest) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const q = request.nextUrl.searchParams.get("q")?.trim() ?? "";
  const all = request.nextUrl.searchParams.get("all") === "1";

  const products = await prisma.product.findMany({
    where: {
      ...(all ? {} : { isActive: true }),
      ...(q ? { name: { contains: q } } : {}),
    },
    include: { images: { orderBy: { sortOrder: "asc" } }, category: true },
    orderBy: { createdAt: "desc" },
    take: 200,
  });

  return NextResponse.json({ success: true, data: products });
}

/** POST /api/admin/products — 创建商品（价格元字符串 → 分；图片逗号分隔 → 多条） */
export async function POST(request: NextRequest) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const body = await request.json().catch(() => null);
  const parsed = productSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { success: false, error: parsed.error.issues[0]?.message ?? "参数错误" },
      { status: 400 }
    );
  }
  const { name, slug, description, priceYuan, stock, categoryId, images, featured } =
    parsed.data;

  const priceCents = toCents(priceYuan);
  if (priceCents === null) {
    return NextResponse.json({ success: false, error: "价格格式不正确" }, { status: 400 });
  }

  // 分类存在性校验
  const category = await prisma.category.findUnique({ where: { id: categoryId } });
  if (!category) {
    return NextResponse.json({ success: false, error: "分类不存在" }, { status: 400 });
  }

  // slug 唯一校验（唯一索引冲突捕获）
  const slugExists = await prisma.product.findUnique({ where: { slug } });
  if (slugExists) {
    return NextResponse.json({ success: false, error: "slug 已存在" }, { status: 400 });
  }

  const imageUrls = images
    .split(",")
    .map((u) => u.trim())
    .filter(Boolean);

  const product = await prisma.product.create({
    data: {
      name,
      slug,
      description,
      priceCents,
      stock,
      featured: featured ?? false,
      categoryId,
      images: imageUrls.length
        ? { create: imageUrls.map((url, i) => ({ url, sortOrder: i })) }
        : undefined,
    },
    include: { images: true },
  });

  return NextResponse.json({ success: true, data: product }, { status: 201 });
}
