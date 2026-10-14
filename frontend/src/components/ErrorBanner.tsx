/**
 * Standard error display (Section 17: "Error: show a useful recoverable
 * message"). role="alert" ensures assistive technology announces it
 * (Section 21: accessibility fundamentals).
 */
import { AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

export function ErrorBanner({ message, className }: { message: string | null; className?: string }) {
  if (!message) return null;

  return (
    <div className={cn("mb-4 flex items-start gap-3 rounded-md border border-statusShortage/20 bg-statusShortage/10 p-4 text-sm text-statusShortage", className)}>
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <div>{message}</div>
    </div>
  );
}
