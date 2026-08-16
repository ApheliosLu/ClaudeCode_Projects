// 订单管理 API：GET 列表（仅 ADMIN）
import { NextRequest, NextResponse } from "next/server";
import { getAdminSession } from "@/lib/guards";
import { prisma } from "@/lib/prisma";

/** GET /api/admin/orders?status=&q= — 所有订单（含买家信息，可按状态筛选/订单号搜索） */
export async function GET(request: NextRequest) {
  const session = await getAdminSession();
  if (!session) {
    return NextResponse.json({ success: false, error: "未授权" }, { status: 401 });
  }

  const status = request.nextUrl.searchParams.get("status") ?? "";
  const q = request.nextUrl.searchParams.get("q")?.trim() ?? "";

  const orders = await prisma.order.findMany({
    where: {
      ...(status ? { status: status as never } : {}),
      ...(q ? { orderNo: { contains: q } } : {}),
    },
    include: {
      user: { select: { name: true, email: true, membershipLevel: true } },
      items: true,
    },
    orderBy: { createdAt: "desc" },
    take: 200,
  });

  return NextResponse.json({ success: true, data: orders });
}
