import type { Pagination as PaginationMeta } from "@/lib/types";

/**
 * Reusable pagination control, driven entirely by the backend's own
 * pagination metadata (API Specification v1.0 Section 7/22) — never
 * assumes a newly created record appears on page 1, and never fetches
 * an unbounded page size to sidestep real pagination.
 */
export function Pagination({
  meta,
  onPageChange,
}: {
  meta: PaginationMeta;
  onPageChange: (page: number) => void;
}) {
  if (meta.totalPages <= 1) return null;

  return (
    <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
      <span>
        Page {meta.page} of {meta.totalPages} ({meta.totalItems} total)
      </span>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => onPageChange(meta.page - 1)}
          disabled={meta.page <= 1}
          className="rounded border border-gray-300 px-2 py-1 disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-gray-400"
          aria-label="Previous page"
        >
          Previous
        </button>
        <button
          type="button"
          onClick={() => onPageChange(meta.page + 1)}
          disabled={meta.page >= meta.totalPages}
          className="rounded border border-gray-300 px-2 py-1 disabled:opacity-40 focus:outline-none focus:ring-2 focus:ring-gray-400"
          aria-label="Next page"
        >
          Next
        </button>
      </div>
    </div>
  );
}
