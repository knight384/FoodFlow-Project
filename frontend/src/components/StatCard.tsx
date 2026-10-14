import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string | number;
  unit?: string;
  description?: string;
  icon?: ReactNode;
  className?: string;
}

export function StatCard({ label, value, unit, description, icon, className }: StatCardProps) {
  return (
    <div className={cn("card relative overflow-hidden group p-5", className)}>
      {/* Subtle hover gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-surfaceHighlight/50 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold tracking-wide text-textSecondary uppercase">{label}</h3>
          {icon && (
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-surfaceHighlight text-textSecondary transition-colors group-hover:text-textPrimary group-hover:bg-accent/20">
              {icon}
            </div>
          )}
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-3xl font-bold tracking-tight text-textPrimary">{value}</span>
          {unit && <span className="text-sm font-medium text-textSecondary">{unit}</span>}
        </div>
        {description && (
          <p className="mt-2 text-xs font-medium text-textSecondary/80">{description}</p>
        )}
      </div>
    </div>
  );
}
