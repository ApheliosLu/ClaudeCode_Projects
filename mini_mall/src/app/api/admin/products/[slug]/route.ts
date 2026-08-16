// 商品管理 API：GET 详情 + PUT 更新 + DELETE 软删除（仅 ADMIN；以 slug 定位商品）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { productSchema } from "@/lib/validators";
import { toCents } from "@/lib/utils";

/** GET /api/admin/products/[slug] — 商品详情（含下架商品，供编辑页） */
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const { slug } = await params;
  const product = await prisma.product.findUnique({
    where: { slug },
    include: { images: { orderBy: { sortOrder: "asc" } }, category: true },
  });
  if (!product) {
    return NextResponse.json({ success: false, error: "商品不存在" }, { status: 404 });
  }

  return NextResponse.json({ success: true, data: product });
}

/** PUT /api/admin/products/[slug] — 更新商品（图片全量重建） */
export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const { slug: urlSlug } = await params;
  const existing = await prisma.product.findUnique({ where: { slug: urlSlug } });
  if (!existing) {
    return NextResponse.json({ success: false, error: "商品不存在" }, { status: 404 });
  }

  const body = await request.json().catch(() => null);
  const parsed = productSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json(
      { success: false, error: parsed.error.issues[0]?.message ?? "参数错误" },
      { status: 400 }
    );
  }
  const {
    name,
    slug: newSlug,
    description,
    priceYuan,
    stock,
    categoryId,
    images,
    featured,
    isActive,
  } = parsed.data;

  const priceCents = toCents(priceYuan);
  if (priceCents === null) {
    return NextResponse.json({ success: false, error: "价格格式不正确" }, { status: 400 });
  }

  const category = await prisma.category.findUnique({ where: { id: categoryId } });
  if (!category) {
    return NextResponse.json({ success: false, error: "分类不存在" }, { status: 400 });
  }

  const slugExists = await prisma.product.findUnique({ where: { slug: newSlug } });
  if (slugExists && slugExists.id !== existing.id) {
    return NextResponse.json({ success: false, error: "slug 已存在" }, { status: 400 });
  }

  const imageUrls = images
    .split(",")
    .map((u) => u.trim())
    .filter(Boolean);

  const product = await prisma.$transaction(async (tx) => {
    await tx.productImage.deleteMany({ where: { productId: existing.id } });
    return tx.product.update({
      where: { id: existing.id },
      data: {
        name,
        slug: newSlug,
        description,
        priceCents,
        stock,
        featured: featured ?? false,
        isActive: isActive ?? true,
        categoryId,
        images: imageUrls.length
          ? { create: imageUrls.map((url, i) => ({ url, sortOrder: i })) }
          : undefined,
      },
      include: { images: true },
    });
  });

  return NextResponse.json({ success: true, data: product });
}

/** DELETE /api/admin/products/[slug] — 软删除（isActive=false，保外键） */
export async function DELETE(
  _request: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const { slug } = await params;
  const existing = await prisma.product.findUnique({ where: { slug } });
  if (!existing) {
    return NextResponse.json({ success: false, error: "商品不存在" }, { status: 404 });
  }

  const product = await prisma.product.update({
    where: { id: existing.id },
    data: { isActive: false },
  });

  return NextResponse.json({ success: true, data: { id: product.id, isActive: false } });
}
