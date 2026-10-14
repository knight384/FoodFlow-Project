"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, apiPost, describeApiError } from "@/lib/api";
import type { Forecast, Location, MealType, Paginated } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { TrendingUp, Plus } from "lucide-react";

const PAGE_SIZE = 20;

export default function ForecastsPage() {
  const { token } = useAuth();
  const [forecasts, setForecasts] = useState<Forecast[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<Forecast>["pagination"] | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [forecastDate, setForecastDate] = useState("");
  const [locationId, setLocationId] = useState("");
  const [mealTypeId, setMealTypeId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);

  function load() {
    if (!token) return;
    setLoading(true);
    Promise.all([
      apiGet<Paginated<Forecast>>("/forecasts", token, { page, pageSize: PAGE_SIZE }),
      apiGet<Paginated<Location>>("/locations", token, { pageSize: 100 }),
      apiGet<Paginated<MealType>>("/meal-types", token, { pageSize: 100 }),
    ])
      .then(([fc, locs, meals]) => {
        setForecasts(fc.data);
        setPagination(fc.pagination);
        setLocations(locs.data);
        setMealTypes(meals.data);
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, [token, page]);

  const locationName = (id: string) => locations.find((l) => l.id === id)?.name ?? id;
  const mealTypeName = (id: string) => mealTypes.find((m) => m.id === id)?.name ?? id;

  async function handleGenerate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setGenerating(true);
    try {
      await apiPost("/forecasts", token, { forecastDate, locationId, mealTypeId });
      setPage(1);
      load();
    } catch (err) {
      setError(describeApiError(err));
    } finally {
      setGenerating(false);
    }
  }

  const columns = [
    { header: "Date", accessor: (f: Forecast) => f.forecastDate },
    { header: "Location", accessor: (f: Forecast) => locationName(f.locationId) },
    { header: "Meal Type", accessor: (f: Forecast) => mealTypeName(f.mealTypeId) },
    { header: "Forecasted Demand", accessor: (f: Forecast) => <div className="text-right font-medium">{f.forecastedDemand}</div> },
    { header: "Generated", accessor: (f: Forecast) => <span className="text-textSecondary text-xs">{new Date(f.generatedAt).toLocaleString()}</span> },
  ];

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">Forecasts</h1>
        <p className="text-sm text-textSecondary mt-1">
          Generate and review demand forecasts using historical data models.
        </p>
      </div>

      <div className="card p-4 sm:p-6 mb-6">
        <h2 className="text-sm font-medium text-textPrimary mb-4 flex items-center gap-2">
          <Plus size={16} className="text-accent" />
          Generate New Forecast
        </h2>
        <form onSubmit={handleGenerate} className="flex flex-col sm:flex-row sm:items-end gap-4">
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="forecastDate">
              Target Date
            </label>
            <input
              id="forecastDate"
              type="date"
              required
              value={forecastDate}
              onChange={(e) => setForecastDate(e.target.value)}
              className="input-field"
            />
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="forecastLocation">
              Location
            </label>
            <select
              id="forecastLocation"
              required
              value={locationId}
              onChange={(e) => setLocationId(e.target.value)}
              className="input-field"
            >
              <option value="">Select location…</option>
              {locations.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="forecastMealType">
              Meal Type
            </label>
            <select
              id="forecastMealType"
              required
              value={mealTypeId}
              onChange={(e) => setMealTypeId(e.target.value)}
              className="input-field"
            >
              <option value="">Select meal type…</option>
              {mealTypes.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>
          <button
            type="submit"
            disabled={generating}
            className="btn-primary w-full sm:w-auto mt-4 sm:mt-0"
          >
            {generating ? "Generating…" : "Generate Forecast"}
          </button>
        </form>
      </div>

      <div>
        <ErrorBanner message={error} />
        {loading ? (
          <LoadingState text="Loading forecasts..." className="py-12" />
        ) : (
          <div className="space-y-4">
            <DataTable
              columns={columns}
              data={forecasts}
              keyExtractor={(f) => f.id}
              emptyState={
                <EmptyState
                  title="No forecasts found"
                  description="Generate a forecast using the form above."
                  icon={<TrendingUp size={32} />}
                  className="py-12"
                />
              }
            />
            {pagination && forecasts.length > 0 && (
              <Pagination meta={pagination} onPageChange={setPage} />
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
