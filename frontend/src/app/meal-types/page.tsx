"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiDelete, apiGet, apiPatch, apiPost, describeApiError } from "@/lib/api";
import type { MealType, Paginated } from "@/lib/types";
import { AppShell } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { Utensils, Plus, Pencil, Archive, Check, X } from "lucide-react";

const PAGE_SIZE = 20;

export default function MealTypesPage() {
  const { token } = useAuth();
  const [mealTypes, setMealTypes] = useState<MealType[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<MealType>["pagination"] | null>(null);
  const [newName, setNewName] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    if (!token) return;
    setLoading(true);
    setError(null);
    apiGet<Paginated<MealType>>("/meal-types", token, { page, pageSize: PAGE_SIZE, includeInactive: true })
      .then((res) => {
        setMealTypes(res.data);
        setPagination(res.pagination);
      })
      .catch((err) => setError(describeApiError(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, [token, page]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await apiPost("/meal-types", token, { name: newName });
      setNewName("");
      setPage(1);
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  async function handleUpdate(id: string) {
    setError(null);
    try {
      await apiPatch(`/meal-types/${id}`, token, { name: editingName });
      setEditingId(null);
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  async function handleArchive(id: string) {
    setError(null);
    try {
      await apiDelete(`/meal-types/${id}`, token);
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  const columns = [
    { 
      header: "Name", 
      accessor: (m: MealType) => (
        editingId === m.id ? (
          <input
            autoFocus
            value={editingName}
            onChange={(e) => setEditingName(e.target.value)}
            className="input-field py-1 text-sm max-w-[200px]"
          />
        ) : (
          <span className="font-medium">{m.name}</span>
        )
      )
    },
    { 
      header: "Status", 
      accessor: (m: MealType) => (
        <span
          className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${
            m.isActive 
              ? "bg-statusSurplus/10 text-statusSurplus border-statusSurplus/20" 
              : "bg-statusUnavailable/10 text-statusUnavailable border-statusUnavailable/20"
          }`}
        >
          {m.isActive ? "Active" : "Archived"}
        </span>
      )
    },
    { 
      header: "Actions", 
      accessor: (m: MealType) => (
        <div className="flex justify-end gap-3">
          {editingId === m.id ? (
            <>
              <button onClick={() => handleUpdate(m.id)} className="text-accent hover:text-accentHover" title="Save">
                <Check size={16} />
              </button>
              <button onClick={() => setEditingId(null)} className="text-textSecondary hover:text-textPrimary" title="Cancel">
                <X size={16} />
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => {
                  setEditingId(m.id);
                  setEditingName(m.name);
                }}
                className="text-textSecondary hover:text-textPrimary"
                title="Edit"
              >
                <Pencil size={16} />
              </button>
              {m.isActive && (
                <button 
                  onClick={() => handleArchive(m.id)} 
                  className="text-statusShortage hover:text-red-500"
                  title="Archive"
                >
                  <Archive size={16} />
                </button>
              )}
            </>
          )}
        </div>
      )
    },
  ];

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">Meal Types</h1>
        <p className="text-sm text-textSecondary mt-1">
          Manage meal classifications and categories.
        </p>
      </div>

      <div className="card p-4 sm:p-6 mb-6">
        <form onSubmit={handleCreate} className="flex flex-col sm:flex-row sm:items-end gap-4 max-w-xl">
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="newMealTypeName">
              New Meal Type Name
            </label>
            <input
              id="newMealTypeName"
              type="text"
              required
              placeholder="e.g., Standard Lunch"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="input-field"
            />
          </div>
          <button
            type="submit"
            className="btn-primary w-full sm:w-auto mt-4 sm:mt-0 gap-2"
          >
            <Plus size={16} />
            Add Meal Type
          </button>
        </form>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <LoadingState text="Loading meal types..." className="py-12" />
      ) : (
        <div className="space-y-4">
          <DataTable
            columns={columns}
            data={mealTypes}
            keyExtractor={(m) => m.id}
            emptyState={
              <EmptyState
                title="No meal types"
                description="Add a meal type to begin categorizing food plans."
                icon={<Utensils size={32} />}
                className="py-12"
              />
            }
          />
          {pagination && mealTypes.length > 0 && <Pagination meta={pagination} onPageChange={setPage} />}
        </div>
      )}
    </AppShell>
  );
}
