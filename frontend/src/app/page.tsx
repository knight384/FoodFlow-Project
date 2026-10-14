"use client";

/**
 * Root entry point — redirects to /dashboard if authenticated, /login
 * otherwise. The original Phase 1 foundation-check page (pinging
 * /health and /health/db) now lives at /system-status.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function RootPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;
    router.replace(user ? "/dashboard" : "/login");
  }, [isLoading, user, router]);

  return (
    <main className="flex min-h-screen items-center justify-center text-sm text-gray-500">
      Loading…
    </main>
  );
}
