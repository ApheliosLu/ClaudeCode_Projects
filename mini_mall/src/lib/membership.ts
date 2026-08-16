// 会员规则：升级阈值与折扣的单一事实源
// 规则：按累计实付金额升级（只升不降，新订单生效）
//   心悦1：累计 ≥ 8000 元（800000 分）→ 9.8 折（98%）
//   心悦2：累计 ≥ 80000 元（8000000 分）→ 9.5 折（95%）
//   心悦3：累计 ≥ 800000 元（80000000 分）→ 9 折（90%）

export type MembershipTier = {
  level: number; // 0 普通 / 1 心悦1 / 2 心悦2 / 3 心悦3
  name: string;
  thresholdCents: number; // 升级所需累计实付（分）
  discountPercent: number; // 折扣：100 = 无折扣，98 = 9.8 折
};

export const MEMBERSHIP_TIERS: MembershipTier[] = [
  { level: 0, name: "普通会员", thresholdCents: 0, discountPercent: 100 },
  { level: 1, name: "心悦1级", thresholdCents: 800_000, discountPercent: 98 },
  { level: 2, name: "心悦2级", thresholdCents: 8_000_000, discountPercent: 95 },
  { level: 3, name: "心悦3级", thresholdCents: 80_000_000, discountPercent: 90 },
];

export function getTier(level: number): MembershipTier {
  return MEMBERSHIP_TIERS.find((t) => t.level === level) ?? MEMBERSHIP_TIERS[0];
}

/** 按累计实付金额计算应达到的最高等级（只升不降由调用方保证） */
export function getUpgradedLevel(accumulatedSpentCents: number): number {
  let level = 0;
  for (const tier of MEMBERSHIP_TIERS) {
    if (accumulatedSpentCents >= tier.thresholdCents) {
      level = tier.level;
    }
  }
  return level;
}

/** 折扣后金额（分），整数运算避免浮点误差 */
export function applyDiscount(cents: number, discountPercent: number): number {
  return Math.round((cents * discountPercent) / 100);
}

/** 下一等级信息（用于会员中心展示"距下一级还差多少"）；已满级返回 null */
export function getNextTier(level: number): MembershipTier | null {
  return MEMBERSHIP_TIERS[level + 1] ?? null;
}
