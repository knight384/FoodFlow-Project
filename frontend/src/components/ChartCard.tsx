import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export function ChartCard({ title, description, children, className }: ChartCardProps) {
  return (
    <div className={cn("card flex flex-col p-5 sm:p-6", className)}>
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold text-textPrimary tracking-tight">{title}</h3>
          {description && <p className="text-xs font-medium text-textSecondary mt-1.5">{description}</p>}
        </div>
      </div>
      {/* We add a min-h-[300px] and let the chart take full responsive height */}
      <div className="flex-1 w-full min-h-[300px] relative">
        {children}
      </div>
    </div>
  );
}
