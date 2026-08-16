// 会员中心：等级徽章 / 折扣 / 累计金额 / 距下一级差额
import { requireAuth } from "@/lib/guards";
import { prisma } from "@/lib/prisma";
import { MEMBERSHIP_TIERS, getTier, getNextTier } from "@/lib/membership";
import { formatCents } from "@/lib/utils";
import { MembershipBadge } from "@/components/MembershipBadge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function MembershipPage() {
  const session = await requireAuth();
  const user = await prisma.user.findUnique({ where: { id: session.user.id } });
  if (!user) return null;

  const current = getTier(user.membershipLevel);
  const next = getNextTier(user.membershipLevel);
  const gapCents = next ? Math.max(0, next.thresholdCents - user.accumulatedSpentCents) : 0;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-xl font-semibold">会员中心</h1>

      {/* 当前等级卡片 */}
      <Card className="mb-6 bg-gradient-to-r from-amber-50 to-orange-50">
        <CardContent className="flex items-center justify-between p-6">
          <div>
            <p className="text-sm text-muted-foreground">当前等级</p>
            <MembershipBadge level={user.membershipLevel} className="mt-2 text-lg" />
            <p className="mt-3 text-3xl font-bold">
              {formatCents(user.accumulatedSpentCents)}
            </p>
            <p className="text-xs text-muted-foreground">累计实付金额</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">当前折扣</p>
            <p className="mt-1 text-3xl font-bold text-red-600">
              {current.discountPercent / 10} 折
            </p>
            {next ? (
              <p className="mt-3 text-xs text-muted-foreground">
                再消费 {formatCents(gapCents)} 升级 {next.name}
              </p>
            ) : (
              <p className="mt-3 text-xs font-medium text-amber-600">
                已达成最高等级，尊享 9 折
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 升级规则 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">升级规则（只升不降，新订单生效）</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-hidden rounded-lg border">
            <table className="w-full text-sm">
              <thead className="bg-muted/60">
                <tr>
                  <th className="px-4 py-2 text-left font-medium">等级</th>
                  <th className="px-4 py-2 text-left font-medium">累计实付达标</th>
                  <th className="px-4 py-2 text-left font-medium">后续折扣</th>
                  <th className="px-4 py-2 text-left font-medium">状态</th>
                </tr>
              </thead>
              <tbody>
                {MEMBERSHIP_TIERS.filter((t) => t.level > 0).map((tier) => (
                  <tr key={tier.level} className="border-t">
                    <td className="px-4 py-2">
                      <MembershipBadge level={tier.level} />
                    </td>
                    <td className="px-4 py-2">{formatCents(tier.thresholdCents)}</td>
                    <td className="px-4 py-2">{tier.discountPercent / 10} 折</td>
                    <td className="px-4 py-2">
                      {user.membershipLevel >= tier.level ? (
                        <span className="text-green-600">已达成</span>
                      ) : user.membershipLevel === tier.level - 1 ? (
                        <span className="text-amber-600">升级中</span>
                      ) : (
                        <span className="text-muted-foreground">未达成</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
