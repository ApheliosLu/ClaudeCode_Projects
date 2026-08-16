import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ---------- 金额（统一整数分） ----------

/** 分 → "¥1,234.56" */
export function formatCents(cents: number): string {
  return `¥${(cents / 100).toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

/** 元字符串（如 "12.34" 或 "12"）→ 分；非法输入返回 null */
export function toCents(yuanInput: string): number | null {
  const s = yuanInput.trim();
  if (!/^\d+(\.\d{1,2})?$/.test(s)) return null;
  const [int, dec = ""] = s.split(".");
  return Number(int) * 100 + Number(dec.padEnd(2, "0"));
}

// ---------- 订单号 ----------

/** 订单号：MM + yyyyMMddHHmmss + 4 位随机数（约 18 位） */
export function genOrderNo(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  const ts = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}${pad(
    now.getHours()
  )}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  const rand = Math.floor(1000 + Math.random() * 9000);
  return `MM${ts}${rand}`;
}

// ---------- 会员 ----------

/** 会员等级名称与说明 */
export const MEMBERSHIP_NAMES = ["普通会员", "心悦1级", "心悦2级", "心悦3级"] as const;

/** 订单状态中文名 */
export const ORDER_STATUS_NAMES: Record<string, string> = {
  PENDING: "待支付",
  PAID: "已支付",
  SHIPPED: "已发货",
  DELIVERED: "已完成",
  CANCELLED: "已取消",
};
