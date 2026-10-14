import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Inbox } from "lucide-react";

interface Column<T> {
  header: string;
  accessor: (row: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T, index: number) => string;
  className?: string;
  emptyState?: ReactNode;
  emptyStateMessage?: string;
}

export function DataTable<T>({ columns, data, keyExtractor, className, emptyState, emptyStateMessage = "No data available." }: DataTableProps<T>) {
  if (data.length === 0) {
    if (emptyState) return <>{emptyState}</>;
    
    return (
      <div className={cn("flex flex-col items-center justify-center rounded-xl border border-dashed border-border bg-surface/50 py-16 px-6 text-center", className)}>
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surfaceHighlight text-textSecondary mb-4 shadow-sm">
          <Inbox size={20} />
        </div>
        <h3 className="text-sm font-semibold text-textPrimary">No data</h3>
        <p className="mt-1 text-sm text-textSecondary max-w-sm">{emptyStateMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn("overflow-x-auto rounded-xl border border-border bg-surface shadow-sm custom-scrollbar relative", className)}>
      <table className="min-w-full text-sm">
        <thead className="bg-surfaceHighlight text-left font-medium text-textSecondary sticky top-0 z-10 shadow-sm border-b border-border">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className={cn("px-5 py-3.5 whitespace-nowrap uppercase tracking-wider text-[11px]", col.className)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {data.map((row, idx) => (
            <tr 
              key={keyExtractor(row, idx)} 
              className="hover:bg-surfaceHighlight/50 transition-colors duration-150 group"
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx} className={cn("px-5 py-4", col.className)}>
                  {col.accessor(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
