import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  title: string;
  description: string;
  icon?: ReactNode;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ title, description, icon, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center rounded-lg border border-border border-dashed bg-surface/50 p-8 text-center", className)}>
      {icon && <div className="mb-4 text-textSecondary">{icon}</div>}
      <h3 className="text-sm font-medium text-textPrimary">{title}</h3>
      <p className="mt-1 text-sm text-textSecondary">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
