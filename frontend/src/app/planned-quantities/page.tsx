"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, apiPatch, apiPost, describeApiError } from "@/lib/api";
import type { Location, MealType, Paginated, PlannedQuantity } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { ClipboardList, Plus, Pencil, X, Check } from "lucide-react";

const PAGE_SIZE = 20;

export default function PlannedQuantitiesPage() {
  const { token } = useAuth();
  const [entries, setEntries] = useState<PlannedQuantity[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<PlannedQuantity>["pagination"] | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [planDate, setPlanDate] = useState("");
  const [locationId, setLocationId] = useState("");
  const [mealTypeId, setMealTypeId] = useState("");
  const [quantity, setQuantity] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingQuantity, setEditingQuantity] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    if (!token) return;
    setLoading(true);
    setError(null);
    Promise.all([
      apiGet<Paginated<PlannedQuantity>>("/planned-quantities", token, { page, pageSize: PAGE_SIZE }),
      apiGet<Paginated<Location>>("/locations", token, { pageSize: 100 }),
      apiGet<Paginated<MealType>>("/meal-types", token, { pageSize: 100 }),
    ])
      .then(([pq, locs, meals]) => {
        setEntries(pq.data);
        setPagination(pq.pagination);
        setLocations(locs.data);
        setMealTypes(meals.data);
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, [token, page]);

  const locationName = (id: string) => locations.find((l) => l.id === id)?.name ?? id;
  const mealTypeName = (id: string) => mealTypes.find((m) => m.id === id)?.name ?? id;

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiPost("/planned-quantities", token, {
        planDate,
        locationId,
        mealTypeId,
        quantity: Number(quantity),
      });
      setPlanDate("");
      setQuantity("");
      setPage(1);
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  async function handleUpdate(id: string) {
    setError(null);
    try {
      await apiPatch(`/planned-quantities/${id}`, token, { quantity: Number(editingQuantity) });
      setEditingId(null);
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  const columns = [
    { header: "Date", accessor: (r: PlannedQuantity) => r.planDate },
    { header: "Location", accessor: (r: PlannedQuantity) => locationName(r.locationId) },
    { header: "Meal Type", accessor: (r: PlannedQuantity) => mealTypeName(r.mealTypeId) },
    {
      header: "Quantity",
      accessor: (r: PlannedQuantity) => (
        <div className="text-right">
          {editingId === r.id ? (
            <input
              type="number"
              min={0}
              value={editingQuantity}
              onChange={(e) => setEditingQuantity(e.target.value)}
              className="input-field w-24 py-1 text-right"
              autoFocus
            />
          ) : (
            <span className="font-medium">{r.quantity}</span>
          )}
        </div>
      ),
    },
    {
      header: "Actions",
      accessor: (r: PlannedQuantity) => (
        <div className="flex justify-end gap-2">
          {editingId === r.id ? (
            <>
              <button onClick={() => handleUpdate(r.id)} className="text-accent hover:text-accentHover" title="Save">
                <Check size={16} />
              </button>
              <button onClick={() => setEditingId(null)} className="text-textSecondary hover:text-textPrimary" title="Cancel">
                <X size={16} />
              </button>
            </>
          ) : (
            <button
              onClick={() => {
                setEditingId(r.id);
                setEditingQuantity(String(r.quantity));
              }}
              className="text-textSecondary hover:text-textPrimary"
              title="Edit"
            >
              <Pencil size={16} />
            </button>
          )}
        </div>
      ),
    },
  ];

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">Planned Quantities</h1>
        <p className="text-sm text-textSecondary mt-1">
          Record and adjust the number of meals planned for preparation.
        </p>
      </div>

      <div className="card p-4 sm:p-6 mb-6">
        <h2 className="text-sm font-medium text-textPrimary mb-4 flex items-center gap-2">
          <Plus size={16} className="text-accent" />
          Add Planned Quantity
        </h2>
        <form onSubmit={handleCreate} className="flex flex-col sm:flex-row sm:items-end gap-4">
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="pqDate">
              Date
            </label>
            <input
              id="pqDate"
              type="date"
              required
              value={planDate}
              onChange={(e) => setPlanDate(e.target.value)}
              className="input-field"
            />
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="pqLocation">
              Location
            </label>
            <select
              id="pqLocation"
              required
              value={locationId}
              onChange={(e) => setLocationId(e.target.value)}
              className="input-field"
            >
              <option value="">Select…</option>
              {locations.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="pqMealType">
              Meal Type
            </label>
            <select
              id="pqMealType"
              required
              value={mealTypeId}
              onChange={(e) => setMealTypeId(e.target.value)}
              className="input-field"
            >
              <option value="">Select…</option>
              {mealTypes.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>
          <div className="sm:w-32 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="pqQuantity">
              Quantity
            </label>
            <input
              id="pqQuantity"
              type="number"
              min={0}
              required
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="input-field"
            />
          </div>
          <button
            type="submit"
            className="btn-primary w-full sm:w-auto mt-4 sm:mt-0"
          >
            Save
          </button>
        </form>
      </div>

      <div>
        <ErrorBanner message={error} />
        {loading ? (
          <LoadingState text="Loading planned quantities..." className="py-12" />
        ) : (
          <div className="space-y-4">
            <DataTable
              columns={columns}
              data={entries}
              keyExtractor={(r) => r.id}
              emptyState={
                <EmptyState
                  title="No planned quantities"
                  description="There are currently no records. Create one above."
                  icon={<ClipboardList size={32} />}
                  className="py-12"
                />
              }
            />
            {pagination && entries.length > 0 && (
              <Pagination meta={pagination} onPageChange={setPage} />
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
