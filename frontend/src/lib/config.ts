/**
 * Frontend runtime configuration.
 *
 * Phase 1 scope only: the backend base URL, used solely by the
 * foundation health-check page (src/app/page.tsx). No business API
 * client exists yet — that is introduced in a later implementation
 * phase, following the endpoint contracts in API Specification v1.0.
 */

export const API_BASE_URL: string =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
