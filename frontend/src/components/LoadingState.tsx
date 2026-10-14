import { cn } from "@/lib/utils";

interface LoadingStateProps {
  text?: string;
  className?: string;
}

export function LoadingState({ text = "Loading...", className }: LoadingStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-8 text-textSecondary", className)}>
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-border border-t-accent" />
      {text && <p className="mt-4 text-sm">{text}</p>}
    </div>
  );
}
