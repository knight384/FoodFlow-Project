import { ClassificationStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

const BADGE_STYLES: Record<ClassificationStatus, string> = {
  surplus: "bg-statusSurplus/10 text-statusSurplus border-statusSurplus/20",
  shortage: "bg-statusShortage/10 text-statusShortage border-statusShortage/20",
  balanced: "bg-statusBalanced/10 text-statusBalanced border-statusBalanced/20",
  unavailable: "bg-statusUnavailable/10 text-statusUnavailable border-statusUnavailable/20",
};

export function StatusBadge({ status }: { status: ClassificationStatus }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        BADGE_STYLES[status] || BADGE_STYLES.unavailable
      )}
    >
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  );
}
