"use client";

// 全局错误边界
import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-md flex-col items-center justify-center px-4 text-center">
      <p className="text-6xl font-bold text-muted-foreground">出错了</p>
      <h1 className="mt-4 text-xl font-semibold">页面加载失败</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        请稍后重试，或返回首页继续浏览
      </p>
      <div className="mt-6 flex gap-2">
        <Button onClick={reset} variant="outline">
          重试
        </Button>
        <Button onClick={() => (window.location.href = "/")}>返回首页</Button>
      </div>
    </div>
  );
}
