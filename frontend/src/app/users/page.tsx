"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth-context";
import { apiGet, apiPatch, apiPost, describeApiError } from "@/lib/api";
import type { Paginated, Role, User } from "@/lib/types";
import { AppShell, roleLabel } from "@/components/AppShell";
import { ErrorBanner } from "@/components/ErrorBanner";
import { Pagination } from "@/components/Pagination";
import { DataTable } from "@/components/DataTable";
import { LoadingState } from "@/components/LoadingState";
import { EmptyState } from "@/components/EmptyState";
import { Users, Plus, Shield, ShieldAlert, ShieldCheck } from "lucide-react";

const PAGE_SIZE = 20;
const ROLES: Role[] = ["administrator", "manager", "operations_staff"];

export default function UsersPage() {
  const { token } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState<Paginated<User>["pagination"] | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("operations_staff");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    if (!token) return;
    if (users.length === 0) setLoading(true);
    setError(null);
    apiGet<Paginated<User>>("/users", token, { page, pageSize: PAGE_SIZE })
      .then((res) => {
        setUsers(res.data);
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
      await apiPost("/users", token, { username, password, role });
      setUsername("");
      setPassword("");
      if (page === 1) {
        load();
      } else {
        setPage(1);
      }
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  async function handleDeactivate(id: string) {
    setError(null);
    try {
      await apiPost(`/users/${id}/deactivate`, token);
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  async function handleRoleChange(id: string, newRole: Role) {
    setError(null);
    try {
      await apiPatch(`/users/${id}`, token, { role: newRole });
      load();
    } catch (err) {
      setError(describeApiError(err));
    }
  }

  const columns = [
    { 
      header: "Username", 
      accessor: (u: User) => (
        <span className="font-medium text-textPrimary">{u.username}</span>
      )
    },
    { 
      header: "Role", 
      accessor: (u: User) => (
        <select
          value={u.role}
          onChange={(e) => handleRoleChange(u.id, e.target.value as Role)}
          className="input-field py-1 text-xs max-w-[160px]"
        >
          {ROLES.map((r) => (
            <option key={r} value={r}>
              {roleLabel(r)}
            </option>
          ))}
        </select>
      )
    },
    { 
      header: "Status", 
      accessor: (u: User) => (
        <span
          className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${
            u.isActive 
              ? "bg-statusSurplus/10 text-statusSurplus border-statusSurplus/20" 
              : "bg-statusUnavailable/10 text-statusUnavailable border-statusUnavailable/20"
          }`}
        >
          {u.isActive ? "Active" : "Deactivated"}
        </span>
      )
    },
    { 
      header: "Actions", 
      accessor: (u: User) => (
        <div className="flex justify-end gap-3">
          {u.isActive ? (
            <button 
              onClick={() => handleDeactivate(u.id)} 
              className="text-statusShortage hover:text-red-500 text-xs font-medium"
            >
              Deactivate
            </button>
          ) : (
            <span className="text-textSecondary text-xs">Deactivated</span>
          )}
        </div>
      )
    },
  ];

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-textPrimary">Users</h1>
        <p className="text-sm text-textSecondary mt-1">
          Manage system access and assign roles to team members.
        </p>
      </div>

      <div className="card p-4 sm:p-6 mb-6">
        <h2 className="text-sm font-medium text-textPrimary mb-4 flex items-center gap-2">
          <Plus size={16} className="text-accent" />
          Create New User
        </h2>
        
        <form onSubmit={handleCreate} className="flex flex-col sm:flex-row sm:items-end gap-4">
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="newUsername">
              Username
            </label>
            <input
              id="newUsername"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              placeholder="e.g., jsmith"
            />
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="newPassword">
              Password
            </label>
            <input
              id="newPassword"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="Min. 8 characters"
            />
          </div>
          <div className="flex-1 space-y-1">
            <label className="block text-xs font-medium text-textSecondary" htmlFor="newRole">
              Role
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                {role === "administrator" ? (
                  <ShieldAlert size={14} className="text-statusShortage" />
                ) : role === "manager" ? (
                  <ShieldCheck size={14} className="text-statusSurplus" />
                ) : (
                  <Shield size={14} className="text-textSecondary" />
                )}
              </div>
              <select
                id="newRole"
                value={role}
                onChange={(e) => setRole(e.target.value as Role)}
                className="input-field pl-9"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {roleLabel(r)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <button
            type="submit"
            className="btn-primary w-full sm:w-auto mt-4 sm:mt-0"
          >
            Create User
          </button>
        </form>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <LoadingState text="Loading users..." className="py-12" />
      ) : (
        <div className="space-y-4">
          <DataTable
            columns={columns}
            data={users}
            keyExtractor={(u) => u.id}
            emptyState={
              <EmptyState
                title="No users"
                description="No users exist in the system yet."
                icon={<Users size={32} />}
                className="py-12"
              />
            }
          />
          {pagination && users.length > 0 && <Pagination meta={pagination} onPageChange={setPage} />}
        </div>
      )}
    </AppShell>
  );
}
