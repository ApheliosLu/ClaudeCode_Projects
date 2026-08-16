// 404 页面
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-md flex-col items-center justify-center px-4 text-center">
      <p className="text-6xl font-bold text-muted-foreground">404</p>
      <h1 className="mt-4 text-xl font-semibold">页面不存在</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        你访问的页面可能已被移除或地址有误
      </p>
      <Button className="mt-6" render={<Link href="/" />}>
        返回首页
      </Button>
    </div>
  );
}
