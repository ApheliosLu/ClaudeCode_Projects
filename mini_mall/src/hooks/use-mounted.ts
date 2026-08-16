"use client";

// 客户端挂载标志：用于 Zustand persist 等"仅客户端有数据"的 hydration 防闪烁
// 这是故意的 hydration 惯例：persist 数据只在客户端存在，服务端渲染必须先用空态，
// 挂载后再切真实状态（React 19 规则对此惯例误报）
/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState } from "react";

export function useMounted(): boolean {
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  return mounted;
}
