// 服务端鉴权辅助：Server Component / Server Action 内真实校验（最终防线）
import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { auth } from "@/lib/auth";

export async function getSession() {
  const h = await headers();
  return auth.api.getSession({ headers: h });
}

/** 需登录：未登录重定向到登录页（带回调地址） */
export async function requireAuth() {
  const session = await getSession();
  if (!session) {
    redirect("/login");
  }
  return session;
}

/** 仅管理员：非 ADMIN 一律重定向首页（管理端 Server Action 必须调用） */
export async function requireAdmin() {
  const session = await requireAuth();
  if (session.user.role !== "ADMIN") {
    redirect("/");
  }
  return session;
}
