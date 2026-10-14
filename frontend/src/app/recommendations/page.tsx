"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, describeApiError } from "@/lib/api";
import type { Recommendation, Location, MealType, Paginated } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { Lightbulb } from "lucide-react";

const PAGE_SIZE = 20;

export default function RecommendationsPage() {
  const { token } = useAuth();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<Recommendation>["pagination"] | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    if (!token) return;
    setLoading(true);
    Promise.all([
      apiGet<Paginated<Recommendation>>("/recommendations", token, { page, pageSize: PAGE_SIZE }),
      apiGet<Paginated<Location>>("/locations", token, { pageSize: 100 }),
      apiGet<Paginated<MealType>>("/meal-types", token, { pageSize: 100 }),
    ])
      .then(([recs, locs, meals]) => {
        setRecommendations(recs.data);
        setPagination(recs.pagination);
        setLocations(locs.data);
        setMealTypes(meals.data);
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, [token, page]);

  const locationName = (id: string) => locations.find((l) => l.id === id)?.name ?? id;
  const mealTypeName = (id: string) => mealTypes.find((m) => m.id === id)?.name ?? id;

  const columns = [
    { 
      header: "ID", 
      accessor: (r: Recommendation) => (
        <span className="text-textSecondary text-xs truncate max-w-[80px] inline-block" title={r.id}>
          {r.id.split('-')[0]}…
        </span>
      )
    },
    { header: "Date", accessor: (r: Recommendation) => r.periodDate },
    { header: "Location", accessor: (r: Recommendation) => locationName(r.locationId) },
    { header: "Meal Type", accessor: (r: Recommendation) => mealTypeName(r.mealTypeId) },
    { 
      header: "Surplus Qty", 
      accessor: (r: Recommendation) => (
        <div className="text-right font-medium text-statusSurplus">
          {r.estimatedSurplusQuantity}
        </div>
      ) 
    },
    { 
      header: "Recommendation", 
      accessor: (r: Recommendation) => (
        <div className="flex flex-col gap-1 items-start">
          <span className="text-textPrimary">{r.recommendationText}</span>
          {r.isAdvisory && (
            <span className="inline-flex items-center rounded border border-statusAdvisory/20 bg-statusAdvisory/10 px-1.5 py-0.5 text-xs font-medium text-statusAdvisory">
              Advisory Only
            </span>
          )}
        </div>
      )
    },
  ];

  return (
    <AppShell>
      <div className="mb-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textPrimary">Recommendations</h1>
          <p className="text-sm font-medium text-textSecondary mt-2">
            AI-driven suggestions for redistributing food surplus across locations.
          </p>
        </div>
      </div>

      <ErrorBanner message={error} />
      
      {loading ? (
        <LoadingState text="Loading recommendations..." className="py-12" />
      ) : (
        <div className="space-y-4">
          <DataTable
            columns={columns}
            data={recommendations}
            keyExtractor={(r) => r.id}
            emptyState={
              <EmptyState
                title="No recommendations found"
                description="There are currently no active surplus recommendations."
                icon={<Lightbulb size={32} />}
                className="py-12"
              />
            }
          />
          {pagination && recommendations.length > 0 && (
            <Pagination meta={pagination} onPageChange={setPage} />
          )}
        </div>
      )}
    </AppShell>
  );
}
