/**
 * Backend API client.
 *
 * A thin wrapper around fetch() that:
 * - prefixes every call with the backend's /api/v1 base (API
 *   Specification v1.0 Section 4),
 * - attaches the Bearer token where present,
 * - parses the standard error envelope (API Specification v1.0
 *   Section 8: { error: { category, message, details? } }) into a
 *   typed ApiError,
 * - dispatches a session-expired event on 401 so AuthContext can clear
 *   state centrally (Section 17: "Session expired: Return the user to
 *   authentication cleanly"), without every page needing its own
 *   401-handling logic.
 *
 * Never invents endpoints or fields beyond what API Specification v1.0
 * documents.
 */

import { API_BASE_URL } from "@/lib/config";

const API_V1 = `${API_BASE_URL}/api/v1`;

export const SESSION_EXPIRED_EVENT = "foodflow:session-expired";

export class ApiError extends Error {
  category: string;
  details?: { field: string; issue: string }[];
  status: number;

  constructor(status: number, category: string, message: string, details?: { field: string; issue: string }[]) {
    super(message);
    this.status = status;
    this.category = category;
    this.details = details;
  }
}

type QueryParams = Record<string, string | number | boolean | undefined | null>;

function buildQuery(params?: QueryParams): string {
  if (!params) return "";
  const usable = Object.entries(params).filter(([, v]) => v !== undefined && v !== null);
  if (usable.length === 0) return "";
  const search = new URLSearchParams();
  for (const [key, value] of usable) {
    search.set(key, String(value));
  }
  return `?${search.toString()}`;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const err = body?.error ?? {};
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent(SESSION_EXPIRED_EVENT));
    }
    throw new ApiError(
      response.status,
      err.category ?? "UNKNOWN_ERROR",
      err.message ?? "An error occurred.",
      err.details,
    );
  }
  return body as T;
}

function authHeaders(token: string | null): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiGet<T>(path: string, token: string | null, params?: QueryParams): Promise<T> {
  const response = await fetch(`${API_V1}${path}${buildQuery(params)}`, {
    method: "GET",
    headers: { ...authHeaders(token) },
  });
  return handleResponse<T>(response);
}

export async function apiPost<T>(path: string, token: string | null, body?: unknown): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  return handleResponse<T>(response);
}

export async function apiPatch<T>(path: string, token: string | null, body: unknown): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    body: JSON.stringify(body),
  });
  return handleResponse<T>(response);
}

export async function apiDelete<T>(path: string, token: string | null): Promise<T> {
  const response = await fetch(`${API_V1}${path}`, {
    method: "DELETE",
    headers: { ...authHeaders(token) },
  });
  return handleResponse<T>(response);
}

/** For POST /historical-data/imports — the one multipart/form-data endpoint (API Spec Section 14). */
export async function apiUploadFile<T>(path: string, token: string | null, file: File): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_V1}${path}`, {
    method: "POST",
    headers: { ...authHeaders(token) }, // no Content-Type — the browser sets the multipart boundary
    body: formData,
  });
  return handleResponse<T>(response);
}

/**
 * Maps an error to a user-facing message (API Specification v1.0
 * Section 8/28). The backend's own `message` field is already
 * human-readable for every category (verified throughout the backend
 * phases) and is used as-is in most cases.
 *
 * Deliberately does NOT special-case AUTHENTICATION_ERROR with a fixed
 * "session expired" message: that category also covers a plain failed
 * LOGIN attempt (wrong password), where the user never had a session
 * to expire — overriding the backend's accurate
 * "Invalid username or password." text with "session expired" wording
 * there would be actively misleading. The real session-expiry UX flow
 * is handled separately, via SESSION_EXPIRED_EVENT above.
 */
export function describeApiError(err: unknown): string {
  if (!(err instanceof ApiError)) {
    return "Something went wrong. Please try again.";
  }
  switch (err.category) {
    case "FORBIDDEN":
      return "You don't have permission to do that.";
    default:
      return err.message;
  }
}
