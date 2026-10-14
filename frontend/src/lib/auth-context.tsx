"use client";

/**
 * Authentication context.
 *
 * Persists the JWT token in localStorage and resolves the current
 * user's identity/role via GET /auth/me on load (AUTH-003) rather than
 * trusting a stale decoded token — the backend remains the
 * authoritative source (TRD v1.0 Section 15).
 *
 * Also listens for SESSION_EXPIRED_EVENT (dispatched by api.ts on any
 * 401 response, not just the initial /auth/me call) so a token that
 * expires mid-session is cleared centrally, and every protected page's
 * AppShell redirect-to-/login effect fires consistently.
 */

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { apiGet, apiPost, SESSION_EXPIRED_EVENT } from "@/lib/api";
import type { CurrentUser } from "@/lib/types";

const TOKEN_STORAGE_KEY = "foodflow_token";

interface LoginResponse {
  token: string;
  user: CurrentUser;
}

interface AuthContextValue {
  token: string | null;
  user: CurrentUser | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem(TOKEN_STORAGE_KEY) : null;
    if (!stored) {
      setIsLoading(false);
      return;
    }
    apiGet<CurrentUser>("/auth/me", stored)
      .then((current) => {
        setToken(stored);
        setUser(current);
      })
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
      })
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    function handleSessionExpired() {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setToken(null);
      setUser(null);
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired);
  }, []);

  async function login(username: string, password: string) {
    const result = await apiPost<LoginResponse>("/auth/login", null, { username, password });
    localStorage.setItem(TOKEN_STORAGE_KEY, result.token);
    setToken(result.token);
    setUser(result.user);
  }

  function logout() {
    const currentToken = token;
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setToken(null);
    setUser(null);
    if (currentToken) {
      // Best-effort per app/core/security.py's documented trade-off:
      // stateless JWTs can't be forcibly invalidated server-side.
      apiPost("/auth/logout", currentToken).catch(() => {
        /* logout is a client-side discard regardless of this call's outcome */
      });
    }
  }

  return (
    <AuthContext.Provider value={{ token, user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
