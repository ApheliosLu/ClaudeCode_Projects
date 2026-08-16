// 买家受保护区域：服务端登录校验（proxy 之外的第二层防线）
import { requireAuth } from "@/lib/guards";

export default async function AccountLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await requireAuth();
  return <>{children}</>;
}
