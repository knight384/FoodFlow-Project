"use client";

import { useState, type FormEvent, useEffect, useMemo } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, describeApiError } from "@/lib/api";
import type { ReportRow, Paginated, Location, MealType } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { StatusBadge } from "@/components/StatusBadge";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { StatCard } from "@/components/StatCard";
import { FileBarChart, Search, ArrowUpRight, ArrowDownRight, Scale } from "lucide-react";

const PAGE_SIZE = 20;

export default function ReportsPage() {
  const { token } = useAuth();
  const [reports, setReports] = useState<ReportRow[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<ReportRow>["pagination"] | null>(null);
  
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  
  const [locations, setLocations] = useState<Location[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  useEffect(() => {
    if (!token) return;
    Promise.all([
      apiGet<Paginated<Location>>("/locations", token, { pageSize: 100 }),
      apiGet<Paginated<MealType>>("/meal-types", token, { pageSize: 100 }),
    ])
      .then(([locs, meals]) => {
        setLocations(locs.data);
        setMealTypes(meals.data);
      })
      .catch((err) => setError(describeApiError(err)));
  }, [token]);

  useEffect(() => {
    if (hasSearched) {
      loadReports(page);
    }
  }, [page]); // eslint-disable-line react-hooks/exhaustive-deps

  const locationName = (id: string) => locations.find((l) => l.id === id)?.name ?? id;
  const mealTypeName = (id: string) => mealTypes.find((m) => m.id === id)?.name ?? id;

  function loadReports(targetPage: number) {
    if (!token) return;
    setLoading(true);
    setError(null);
    
    apiGet<Paginated<ReportRow>>("/reports", token, { 
      page: targetPage, 
      pageSize: PAGE_SIZE,
      dateFrom,
      dateTo
    })
      .then((res) => {
        setReports(res.data);
        setPagination(res.pagination);
        setHasSearched(true);
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }

  function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (!dateFrom || !dateTo) {
      setError("Please select both a start and end date.");
      return;
    }
    if (new Date(dateFrom) > new Date(dateTo)) {
      setError("Start date cannot be after end date.");
      return;
    }
    
    setPage(1);
    loadReports(1);
  }

  // Summary Metrics
  const summary = useMemo(() => {
    if (!reports.length) return null;
    let totalSurplus = 0;
    let totalShortage = 0;
    let surplusCount = 0;
    let shortageCount = 0;
    let balancedCount = 0;

    reports.forEach(r => {
      if (r.status === "surplus") {
        surplusCount++;
        totalSurplus += (r.potentialSurplus || 0);
      } else if (r.status === "shortage") {
        shortageCount++;
        totalShortage += (r.potentialShortage || 0);
      } else if (r.status === "balanced") {
        balancedCount++;
      }
    });

    return { totalSurplus, totalShortage, surplusCount, shortageCount, balancedCount };
  }, [reports]);

  const columns = [
    { header: "Date", accessor: (r: ReportRow) => r.date },
    { header: "Location", accessor: (r: ReportRow) => locationName(r.locationId) },
    { header: "Meal Type", accessor: (r: ReportRow) => mealTypeName(r.mealTypeId) },
    { header: "Forecast", accessor: (r: ReportRow) => <div className="text-right text-textSecondary">{r.forecastedDemand ?? "—"}</div> },
    { header: "Planned", accessor: (r: ReportRow) => <div className="text-right text-textSecondary">{r.plannedQuantity ?? "—"}</div> },
    { header: "Variance", accessor: (r: ReportRow) => <div className="text-right text-textSecondary">{r.variancePercentage !== null ? `${r.variancePercentage}%` : "—"}</div> },
    { header: "Surplus", accessor: (r: ReportRow) => <div className="text-right font-medium text-statusSurplus">{r.potentialSurplus && r.potentialSurplus > 0 ? r.potentialSurplus : "—"}</div> },
    { header: "Shortage", accessor: (r: ReportRow) => <div className="text-right font-medium text-statusShortage">{r.potentialShortage && r.potentialShortage > 0 ? r.potentialShortage : "—"}</div> },
    { header: "Status", accessor: (r: ReportRow) => <StatusBadge status={r.status} /> },
  ];

  return (
    <AppShell>
      <div className="mb-8 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-textPrimary">Reports</h1>
          <p className="text-sm font-medium text-textSecondary mt-2">
            Generate and view operational reports for historical demand and planning accuracy.
          </p>
        </div>
      </div>

      <div className="card p-6 mb-8 shadow-sm">
        <form onSubmit={handleSearch} className="flex flex-col sm:flex-row sm:items-end gap-4">
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="dateFrom">
              From Date
            </label>
            <input
              id="dateFrom"
              type="date"
              required
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              className="input-field"
            />
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="dateTo">
              To Date
            </label>
            <input
              id="dateTo"
              type="date"
              required
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              className="input-field"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full sm:w-auto mt-4 sm:mt-0 gap-2"
          >
            <Search size={16} />
            {loading ? "Searching…" : "Search"}
          </button>
        </form>
      </div>

      <ErrorBanner message={error} />
      
      {!hasSearched && !loading && !error && (
        <EmptyState
          title="No date range selected"
          description="Select a date range and click Search to view reports."
          icon={<FileBarChart size={32} />}
          className="py-16"
        />
      )}

      {loading && !reports.length && (
        <LoadingState text="Loading reports..." className="py-12" />
      )}

      {hasSearched && reports.length === 0 && !loading && !error && (
        <EmptyState
          title="No reports found"
          description={`No data available for the period ${dateFrom} to ${dateTo}.`}
          icon={<Search size={32} />}
          className="py-16"
        />
      )}

      {hasSearched && reports.length > 0 && summary && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <StatCard
              label="Total Surplus"
              value={summary.totalSurplus.toLocaleString()}
              description={`${summary.surplusCount} records`}
              icon={<ArrowUpRight size={16} className="text-statusSurplus" />}
            />
            <StatCard
              label="Total Shortage"
              value={summary.totalShortage.toLocaleString()}
              description={`${summary.shortageCount} records`}
              icon={<ArrowDownRight size={16} className="text-statusShortage" />}
            />
            <StatCard
              label="Balanced Operations"
              value={summary.balancedCount.toLocaleString()}
              description="Records without variance"
              icon={<Scale size={16} className="text-statusBalanced" />}
            />
          </div>
          
          <div className="space-y-4">
            <DataTable
              columns={columns}
              data={reports}
              keyExtractor={(r, i) => `${r.date}-${r.locationId}-${r.mealTypeId}-${i}`}
            />
            {pagination && (
              <Pagination meta={pagination} onPageChange={setPage} />
            )}
          </div>
        </div>
      )}
    </AppShell>
  );
}
