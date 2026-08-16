// 会员等级徽章
import { Badge } from "@/components/ui/badge";
import { getTier } from "@/lib/membership";
import { cn } from "@/lib/utils";

const styles: Record<number, string> = {
  0: "bg-gray-200 text-gray-700",
  1: "bg-amber-100 text-amber-800",
  2: "bg-orange-200 text-orange-900",
  3: "bg-gradient-to-r from-amber-400 to-yellow-300 text-black",
};

export function MembershipBadge({ level, className }: { level: number; className?: string }) {
  const tier = getTier(level);
  return (
    <Badge className={cn(styles[level] ?? "", className)}>{tier.name}</Badge>
  );
}
