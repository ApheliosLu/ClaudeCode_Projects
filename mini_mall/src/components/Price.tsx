// 金额展示：分 → ¥xx.xx；可选原价划线（会员折扣对比）
import { formatCents } from "@/lib/utils";

export function Price({
  cents,
  originalCents,
  className,
}: {
  cents: number;
  originalCents?: number;
  className?: string;
}) {
  return (
    <span className={className}>
      <span className="font-semibold text-red-600">{formatCents(cents)}</span>
      {originalCents !== undefined && originalCents > cents && (
        <span className="ml-2 text-sm text-muted-foreground line-through">
          {formatCents(originalCents)}
        </span>
      )}
    </span>
  );
}
