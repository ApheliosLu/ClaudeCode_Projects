// Next.js 16 proxy（middleware 更名）— 认证 UX 层，仅做跳转
// 真实鉴权在 Server Component / Server Action 内（guards.ts），本文件可被绕过
// 注意：本文件运行于 Node runtime，可直接查询数据库
import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";

export async function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  // 管理端：需登录且 ADMIN
  if (pathname.startsWith("/admin")) {
    const session = await auth.api.getSession({ headers: request.headers });
    if (!session) {
      return redirectToLogin(request, pathname + search);
    }
    if (session.user.role !== "ADMIN") {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  // 买家受保护区：需登录
  const protectedPrefixes = ["/cart", "/checkout", "/orders", "/membership", "/pay"];
  if (protectedPrefixes.some((p) => pathname.startsWith(p))) {
    const session = await auth.api.getSession({ headers: request.headers });
    if (!session) {
      return redirectToLogin(request, pathname + search);
    }
    return NextResponse.next();
  }

  return NextResponse.next();
}

function redirectToLogin(request: NextRequest, callbackPath: string) {
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("callbackURL", callbackPath);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: [
    "/cart/:path*",
    "/checkout/:path*",
    "/orders/:path*",
    "/membership/:path*",
    "/pay/:path*",
    "/admin/:path*",
  ],
};
