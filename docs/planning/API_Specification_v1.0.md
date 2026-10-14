# API Specification v1.0
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality

---

## 1. Document Control

- **Document title:** API Specification
- **Project name:** Food-Service Demand Forecasting and Surplus Redistribution System (working title: FoodFlow — placeholder, to be confirmed)
- **Version:** 1.0
- **Status:** Draft, pending review
- **Purpose:** Define the complete frontend ↔ FastAPI backend API contract needed to implement the approved MVP, sufficient for later implementation with minimal ambiguity.
- **Source documents:** Project Foundation & Scope Definition v1.1; PRD v1.0; SRS v1.0; TRD v1.0; Database Specification v1.0 — all approved and locked.
- **Intended audience:** Project/Product Mentor, Frontend Developers, Backend Developers, Technical Reviewers.

*(No author names or approval dates are stated, as none have been provided.)*

---

## 2. API Objectives and Scope

**Purpose:** This API is the sole contract between the Next.js frontend and the FastAPI backend. It exposes exactly the approved MVP capabilities and no more.

**Frontend/backend boundary:** The frontend never accesses PostgreSQL directly; all data reads and writes occur through this API, which is backed by the backend's authoritative business logic (TRD Sections 3, 8).

**Supported MVP modules:** Authentication, Users, Locations, Meal Types, Historical Data, Forecasts, Planned Quantities, Comparisons, Classification, Recommendations, Dashboard, Reports.

**Authentication requirement:** Every endpoint except login requires an authenticated session/token (Section 5).

**Database relationship:** All endpoint contracts are consistent with the locked Database Specification v1.0 (Section 25 maps endpoints to tables).

**Out of scope for this API:** Actual Prepared Quantity capture, forward-looking Actual Consumed Quantity capture, forecast accuracy tracking, PDF/CSV export, email/SMS notifications, external donation/logistics integrations, route optimization, donor matching, multi-location comparative analytics, and any capability listed as Optional/Future or Out of Scope in Foundation v1.1/PRD v1.0. **This API serves the approved MVP only.**

---

## 3. API Architecture Overview

```text
Next.js Frontend
      ↓
HTTPS / REST (JSON, except file upload)
      ↓
FastAPI Backend (this API)
      ↓
Business Logic Modules (auth, users, locations, meal-types,
   historical-data, forecasting, planned-quantities,
   comparison, classification, recommendations,
   dashboard, reports)
      ↓
PostgreSQL (per Database Specification v1.0)
```

- The frontend interacts **only** with this API — it never queries PostgreSQL directly.
- The backend's business logic modules (TRD Section 8) are authoritative: variance calculation, classification, and recommendation generation all happen server-side; the API exposes their *results*, not raw computation inputs for the frontend to compute itself.
- Forecasting is accessed exclusively through the backend's `forecasting` module, which in turn calls the internal Forecasting/ML module (TRD Section 12) — the API never exposes ML internals (algorithm, training, model artifacts).
- Recommendation logic remains inside backend business logic (`recommendations` module) — the API only exposes the resulting recommendation records, never a mechanism to manually construct one from the frontend.

No implementation code is included in this document.

---

## 4. Base URL and Versioning

**Proposed convention (from TRD v1.0, Section 16):**

```text
https://<host>/api/v1
```

- `<host>` is a placeholder — no actual production domain is defined here, consistent with the deployment target remaining an open decision (TRD Section 29).
- The `v1` path segment allows future breaking changes to be introduced as `/api/v2` without disrupting the initial frontend integration.
- This is a **proposed technical decision**, not a company-confirmed requirement — no source document mandates a specific versioning scheme.

All endpoint paths in this document are shown relative to this base, e.g., `/auth/login` means `https://<host>/api/v1/auth/login`.

---

## 5. Authentication and Authorization

### Login
- **Endpoint:** `POST /auth/login`
- Accepts a username and password; on success, issues a session/token; on failure, returns a generic authentication error (no indication of whether the username or password was wrong), per SRS-FR-001.

### Logout
- **Endpoint:** `POST /auth/logout`
- Terminates the current session/token. Subsequent requests using the same credential must be rejected as unauthenticated.

### Current User
- **Endpoint:** `GET /auth/me`
- **Justification:** The frontend needs to know the authenticated user's role to drive role-aware navigation and UI (TRD Section 7 — "authentication state"), without re-parsing a token client-side. This is a minimal, justified addition, not an invented feature — it directly supports SRS-FR-003's frontend-visibility layer.

### Authorization
Every protected endpoint enforces role-based access at the backend (authoritative, per TRD Section 15). The baseline permission matrix, carried forward **unchanged** from SRS v1.0/PRD v1.0, applies:

| Capability | Admin | Manager | Operations Staff |
|---|---|---|---|
| Login | ✓ | ✓ | ✓ |
| Manage Users | ✓ | — | — |
| Manage Locations | ✓ | View | View |
| Manage Meal Types | ✓ | View | View |
| Upload Historical Data | ✓ | — | — |
| View Forecasted Demand | ✓ | ✓ | **Pending permission confirmation** |
| Enter Planned Quantity | **Pending permission confirmation** | **Pending permission confirmation** | ✓ |
| View Surplus/Shortage Alerts | ✓ | ✓ | **Pending permission confirmation** |
| View Redistribution Recommendations | ✓ | ✓ | **Pending permission confirmation** |
| View Reports | ✓ | ✓ | **Pending permission confirmation (Limited, per PRD)** |

**These cells are not resolved in this API Specification.** Per-endpoint authorization notes throughout this document explicitly flag "Pending permission confirmation" wherever the matrix leaves the answer open, rather than assuming an answer. The backend's authorization layer is designed (TRD Section 15) to be configuration-driven per role/capability, so resolving these later is a configuration change, not an API contract change.

---

## 6. Common API Conventions

### HTTP methods
- `GET` — retrieve a resource or collection.
- `POST` — create a resource, or perform an action without a natural REST verb (e.g., login, deactivate).
- `PATCH` — partial update of an existing resource (preferred over `PUT` throughout, since most updates in this domain are partial, e.g., editing a Planned Quantity).
- `DELETE` — remove/archive a resource, subject to the deletion-safety caveats in Sections 12–13.

### Content types
- `application/json` for all requests/responses **except** the historical-data upload endpoint, which uses `multipart/form-data` to accept a file.

### Naming convention
**Proposed: camelCase for all JSON field names in requests and responses** (e.g., `locationId`, `forecastedDemand`, `plannedQuantity`). Reasoning: this is a JSON API consumed by a TypeScript/JavaScript frontend (Next.js, TRD Section 6), where camelCase is the idiomatic convention; the backend's internal Python/database layer may use snake_case (Database Specification v1.0), but the API boundary translates to camelCase for frontend consistency. This is applied consistently throughout this document.

### Date format
**ISO 8601 calendar date** (`YYYY-MM-DD`), e.g., `2026-09-01`, used for all date-only fields (`recordDate`, `forecastDate`, `planDate`, `periodDate`, and date-range filter parameters).

### Timestamp format
**ISO 8601 date-time with UTC offset** (`YYYY-MM-DDTHH:MM:SSZ`), e.g., `2026-08-16T10:30:00Z`, used for all timestamp fields (`generatedAt`, `uploadedAt`, `createdAt`, `updatedAt`). All timestamps are stored and transmitted in UTC; any local-timezone display is a frontend concern, not part of this API contract.

### Numeric values
Meal quantities (`forecastedDemand`, `plannedQuantity`, `actualConsumedQuantity`, `estimatedSurplusQuantity`) are represented as **non-negative numbers** (JSON number type). No business unit beyond "meal quantity" (a count) is defined, consistent with the source documents — no currency, weight, or volume units are introduced.

---

## 7. Standard Response Envelope

**Options considered:**
- **Option A — raw resource responses:** Simpler, less boilerplate, fewer wrapper objects for a small frontend team to unwrap.
- **Option B — standard response envelope:** More consistent for cross-cutting concerns (metadata, pagination) but adds a layer of nesting to every response.

**Recommendation: a lightweight envelope for collections (to carry pagination metadata), and raw resource responses for single-resource endpoints.** This keeps single-resource responses simple (matching the "prefer the simpler approach" guidance) while still giving list endpoints a consistent place for pagination info (Section 22), avoiding the need for a second, inconsistent convention later.

**Single resource example:**
```json
{
  "id": "loc_1a2b3c",
  "name": "Main Cafeteria",
  "isActive": true,
  "createdAt": "2026-01-10T09:00:00Z",
  "updatedAt": "2026-01-10T09:00:00Z"
}
```

**Collection example:**
```json
{
  "data": [
    { "id": "loc_1a2b3c", "name": "Main Cafeteria", "isActive": true }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 3,
    "totalPages": 1
  }
}
```

This convention is applied consistently throughout the endpoint definitions below.

---

## 8. Standard Error Model

**Consistent error structure for all endpoints:**

```json
{
  "error": {
    "category": "VALIDATION_ERROR",
    "message": "Quantity must be a non-negative number.",
    "details": [
      { "field": "quantity", "issue": "must be >= 0" }
    ]
  }
}
```

**Fields:**
- `category` — a fixed error-category string (see Section 28 for the catalogue).
- `message` — a human-readable, safe-to-display message.
- `details` — optional array of field-level issues (present for validation errors; omitted otherwise).

**No correlation/request identifier is included by default** — not justified by any source requirement at MVP scale; may be added later without breaking this contract (it would simply be an additional, optional field).

**Never exposed:** stack traces, database error details (table/column names, constraint names), password/hash values, internal secrets, or any implementation detail beyond the safe `message` text.

HTTP status conventions are defined practically in Section 28 — not exhaustively enumerated per endpoint beyond what's needed for clarity.

---

## 9. Endpoint Inventory

| ID | Method | Path | Purpose | Actor/Role | Auth Required | Authorization | SRS Requirement(s) |
|---|---|---|---|---|---|---|---|
| AUTH-001 | POST | `/auth/login` | Authenticate a user | All | No | N/A | SRS-FR-001 |
| AUTH-002 | POST | `/auth/logout` | End a session | All | Yes | Any authenticated user | SRS-FR-002 |
| AUTH-003 | GET | `/auth/me` | Get current user identity/role | All | Yes | Any authenticated user | SRS-FR-003 |
| USR-001 | GET | `/users` | List users | Admin | Yes | Admin only | SRS-FR-004 |
| USR-002 | POST | `/users` | Create a user | Admin | Yes | Admin only | SRS-FR-004 |
| USR-003 | GET | `/users/{userId}` | Retrieve a user | Admin | Yes | Admin only | SRS-FR-004 |
| USR-004 | PATCH | `/users/{userId}` | Update a user | Admin | Yes | Admin only | SRS-FR-004 |
| USR-005 | POST | `/users/{userId}/deactivate` | Deactivate a user | Admin | Yes | Admin only | SRS-FR-004 |
| LOC-001 | GET | `/locations` | List locations | All | Yes | All roles (view) | SRS-FR-005 |
| LOC-002 | POST | `/locations` | Create a location | Admin | Yes | Admin only | SRS-FR-005 |
| LOC-003 | GET | `/locations/{locationId}` | Retrieve a location | All | Yes | All roles (view) | SRS-FR-005 |
| LOC-004 | PATCH | `/locations/{locationId}` | Update a location | Admin | Yes | Admin only | SRS-FR-005 |
| LOC-005 | DELETE | `/locations/{locationId}` | Remove/archive a location | Admin | Yes | Admin only | SRS-FR-005 |
| MEAL-001 | GET | `/meal-types` | List meal types | All | Yes | All roles (view) | SRS-FR-006 |
| MEAL-002 | POST | `/meal-types` | Create a meal type | Admin | Yes | Admin only | SRS-FR-006 |
| MEAL-003 | GET | `/meal-types/{mealTypeId}` | Retrieve a meal type | All | Yes | All roles (view) | SRS-FR-006 |
| MEAL-004 | PATCH | `/meal-types/{mealTypeId}` | Update a meal type | Admin | Yes | Admin only | SRS-FR-006 |
| MEAL-005 | DELETE | `/meal-types/{mealTypeId}` | Remove/archive a meal type | Admin | Yes | Admin only | SRS-FR-006 |
| HIST-001 | POST | `/historical-data/imports` | Upload historical data | Admin | Yes | Admin only | SRS-FR-007, 008, 009 |
| HIST-002 | GET | `/historical-data/imports` | List import jobs | Admin | Yes | Admin only | SRS-FR-010 |
| HIST-003 | GET | `/historical-data/imports/{importId}` | Retrieve import status/detail | Admin | Yes | Admin only | SRS-FR-010 |
| FC-001 | POST | `/forecasts` | Trigger/request forecast generation for a period | Manager | Yes | Manager, Admin | SRS-FR-011, 012 |
| FC-002 | GET | `/forecasts` | List/filter forecasts | Manager | Yes | Manager, Admin, Operations Staff (**pending confirmation**) | SRS-FR-011, 012 |
| FC-003 | GET | `/forecasts/{forecastId}` | Retrieve a single forecast | Manager | Yes | Same as FC-002 | SRS-FR-011, 013 |
| PQ-001 | POST | `/planned-quantities` | Create a Planned Quantity entry | Operations Staff | Yes | Operations Staff (Admin/Manager **pending confirmation**) | SRS-FR-014, 017 |
| PQ-002 | GET | `/planned-quantities` | List/filter Planned Quantity entries | All | Yes | All roles (view) | SRS-FR-016 |
| PQ-003 | GET | `/planned-quantities/{id}` | Retrieve a Planned Quantity entry | All | Yes | All roles (view) | SRS-FR-016 |
| PQ-004 | PATCH | `/planned-quantities/{id}` | Edit a Planned Quantity entry | Operations Staff | Yes | Operations Staff (Admin/Manager **pending confirmation**) | SRS-FR-015, 017 |
| CMP-001 | GET | `/comparisons` | Dynamically computed Forecasted Demand vs Planned Quantity comparison | Manager | Yes | Manager, Admin | SRS-FR-018, 019, 020 |
| CLS-001 | GET | `/classifications` | Dynamically computed Surplus/Shortage/Balanced status | Manager | Yes | Manager, Admin | SRS-FR-021, 022, 023 |
| REC-001 | GET | `/recommendations` | List/filter recommendations | Manager | Yes | Manager, Admin | SRS-FR-024, 025, 026 |
| REC-002 | GET | `/recommendations/{recommendationId}` | Retrieve a single recommendation | Manager | Yes | Manager, Admin | SRS-FR-024–027 |
| DASH-001 | GET | `/dashboard` | Aggregated dashboard summary | Manager | Yes | Manager, Admin | SRS-FR-028, 029 |
| RPT-001 | GET | `/reports` | Filterable historical report | Manager | Yes | Manager, Admin (Operations Staff limited, **pending confirmation**) | SRS-FR-030, 031 |

No endpoint exists outside an approved MVP capability. No `POST /recommendations` endpoint is included — see Section 19 for reasoning.

---

## 10. Authentication API

### AUTH-001 — Login
- **Endpoint:** `POST /auth/login`
- **Purpose:** Authenticate a user and establish a session.
- **Actor:** Any registered user (Admin, Manager, Operations Staff).
- **Authentication requirement:** None (this is the entry point).
- **Request body:**
  ```json
  { "username": "jane.manager", "password": "••••••••" }
  ```
- **Validation:** `username` and `password` both required, non-empty.
- **Success response (200):**
  ```json
  {
    "token": "•••••• (opaque session/token value)",
    "user": { "id": "usr_9f8e7d", "username": "jane.manager", "role": "manager" }
  }
  ```
  *(Exact token mechanism — server-side session vs. stateless token — is a TRD/implementation detail, TRD Section 14; this contract is compatible with either.)*
- **Failure response (401):**
  ```json
  { "error": { "category": "AUTHENTICATION_ERROR", "message": "Invalid username or password." } }
  ```
  No indication of which credential was wrong (SRS-FR-001).
- **SRS traceability:** SRS-FR-001.

### AUTH-002 — Logout
- **Endpoint:** `POST /auth/logout`
- **Purpose:** Terminate the current session.
- **Actor:** Any authenticated user.
- **Authentication requirement:** Required.
- **Request body:** None.
- **Success response (204):** No content.
- **Failure response:** 401 if not authenticated.
- **SRS traceability:** SRS-FR-002.

### AUTH-003 — Current User
- **Endpoint:** `GET /auth/me`
- **Purpose:** Return the authenticated user's identity and role, for frontend role-aware rendering.
- **Actor:** Any authenticated user.
- **Authentication requirement:** Required.
- **Success response (200):**
  ```json
  { "id": "usr_9f8e7d", "username": "jane.manager", "role": "manager" }
  ```
- **Failure response:** 401 if not authenticated.
- **SRS traceability:** SRS-FR-003 (supports the frontend visibility layer described there).

No other authentication endpoints (password reset, MFA, social login, email verification) are defined, as none are required by the source documents.

---

## 11. User Management API

Supports SRS-FR-004. All endpoints require Admin authorization.

- **`GET /users`** — List users. Query params: `page`, `pageSize` (Section 22). Response: collection of `{ id, username, role, isActive, createdAt, updatedAt }`. **Password hashes are never included in any response.**
- **`POST /users`** — Create a user.
  - Request: `{ "username": "new.staff", "password": "••••••••", "role": "operations_staff" }`
  - Validation: `username` required, non-empty; `password` required (minimum handling deferred to implementation, not specified by source documents); `role` must be one of the three approved roles.
  - Response (201): the created user object (no password hash).
  - **Duplicate username:** Rejected with a `409 CONFLICT` (`DUPLICATE_RESOURCE` category) if the username already exists. The Database Specification recommends a `UNIQUE` constraint on `username` (Database Spec Section 17); however, the exact **user-facing UX** of a duplicate attempt beyond this generic conflict response remains an application-level detail not further specified by the source documents (Database Spec Section 29, item 4) — this API defines only the conflict *behavior*, not any additional UX refinement.
- **`GET /users/{userId}`** — Retrieve a single user (no password hash).
- **`PATCH /users/{userId}`** — Update user details (e.g., role reassignment). Request: any subset of `{ "role": "...", "username": "..." }`.
- **`POST /users/{userId}/deactivate`** — Deactivate a user (sets `isActive = false`, per Database Specification Section 18's soft-deactivation recommendation). Response (200): the updated user object. **No hard-delete endpoint is provided for users**, consistent with the Database Specification's recommendation to preserve historical auditability (Planned Quantity and Import Job references would otherwise be orphaned).

**Explicitly not created:** password reset, MFA, social login, or email verification endpoints — none required by the source documents.

---

## 12. Location Management API

Supports SRS-FR-005. Create/Update/Delete require Admin authorization; List/Retrieve are available to all roles (view).

- **`GET /locations`** — List locations. Query params: `page`, `pageSize`, optional `includeInactive` (boolean, default `false`) to support viewing archived locations if the soft-delete/archive approach is confirmed (Section 8, Database Spec).
- **`POST /locations`** — Create a location. Request: `{ "name": "Main Cafeteria" }`. Validation: `name` required, non-empty, unique.
- **`GET /locations/{locationId}`** — Retrieve a location.
- **`PATCH /locations/{locationId}`** — Update a location. Request: `{ "name": "..." }`.
- **`DELETE /locations/{locationId}`** — Remove/archive a location.

**Proposed API behavior pending deletion-safety confirmation:** This endpoint's exact effect is **not finalized**, mirroring the Database Specification's unresolved deletion strategy (Database Spec Section 8/18). The API contract is defined so it remains valid under either eventual outcome:
- If the confirmed policy is **soft delete/archive** (the Database Specification's recommendation): `DELETE /locations/{locationId}` sets `isActive = false` and returns `200` with the updated (now-archived) resource. The location remains selectable in historical filters (via `includeInactive`) but is excluded from create-flow location pickers going forward.
- If the confirmed policy is **restricted delete** (block if referenced): `DELETE /locations/{locationId}` attempts a hard removal and returns `409 CONFLICT` (`BUSINESS_RULE_VIOLATION`) if any historical/forecast/planned/recommendation record references it, or `204` if unreferenced.

Either outcome uses the same endpoint signature (`DELETE /locations/{locationId}` → success or conflict), so **no API contract change is required once the policy is confirmed** — only the internal implementation logic changes. This ensures existing historical references cannot be accidentally broken through API behavior regardless of which policy is ultimately chosen.

---

## 13. Meal-Type Management API

Supports SRS-FR-006. Identical pattern to Location Management (Section 12).

- **`GET /meal-types`** — List meal types. Same `page`/`pageSize`/`includeInactive` query params.
- **`POST /meal-types`** — Create a meal type. Request: `{ "name": "Lunch" }`. Validation: `name` required, non-empty, unique.
- **`GET /meal-types/{mealTypeId}`** — Retrieve a meal type.
- **`PATCH /meal-types/{mealTypeId}`** — Update a meal type.
- **`DELETE /meal-types/{mealTypeId}`** — Remove/archive a meal type. **Same "proposed API behavior pending deletion-safety confirmation" caveat as Section 12 applies identically here.**

---

## 14. Historical Data API

Supports SRS-FR-007–010. Admin authorization required for all endpoints in this module.

### Upload
- **Endpoint:** `POST /historical-data/imports`
- **Content type:** `multipart/form-data` (file upload).
- **Accepted input concept:** A file containing rows with, at minimum: date, meal type (name or reference), location (name or reference), and Actual Consumed Quantity. Exact accepted file format (e.g., CSV structure) is an implementation detail not further specified here, consistent with the source documents not mandating a specific file format.
- **Required fields (per row):** date, meal type, location, Actual Consumed Quantity (Database Spec Section 6.5, SRS Section 10).
- **Authorization:** Admin only.
- **Response (202 — processing accepted, or 201 if processed synchronously):**
  ```json
  {
    "importId": "imp_5c6d7e",
    "status": "processing",
    "uploadedAt": "2026-08-16T10:30:00Z"
  }
  ```
  *(Whether validation/import runs synchronously or asynchronously is a TRD/implementation decision — Database Spec Section 6.6 notes `status` values including `processing`; this contract supports either by allowing `status` to reflect the current state.)*

### Import Status
- **Endpoint:** `GET /historical-data/imports/{importId}`
- **Purpose:** View the outcome of an import job (SRS-FR-010).
- **Response (200):**
  ```json
  {
    "importId": "imp_5c6d7e",
    "uploadedByUserId": "usr_2a3b4c",
    "uploadedAt": "2026-08-16T10:30:00Z",
    "status": "completed",
    "totalRecords": 500,
    "validRecords": 486,
    "invalidRecords": 14,
    "errors": [
      { "rowReference": 37, "failureReason": "Negative quantity value." },
      { "rowReference": 102, "failureReason": "Unrecognized meal type." }
    ]
  }
  ```
  This maps directly to the `import_job` and `import_record_error` tables (Database Spec Sections 6.6–6.7).

### Import History
- **Endpoint:** `GET /historical-data/imports`
- **Justification:** Directly supports SRS-FR-010's requirement that the Administrator can view import status/history, not just the single most recent job.
- **Query params:** `page`, `pageSize`.
- **Response:** Collection envelope (Section 7) of import job summaries (without full per-record error detail — use `GET /historical-data/imports/{importId}` for that).

**Duplicate-record handling:** Not resolved by this API. Whatever eventual policy is confirmed (reject/merge/overwrite — Database Spec Section 29, item 1), the response shape above (`errors` array with `failureReason` per row) already accommodates a "reject and report" outcome; a "merge" or "overwrite" outcome would simply not produce an error entry for that row. **No API contract change is anticipated either way**, but this is not guaranteed until the policy is confirmed.

No endpoints exist for external data sources — only direct file upload is supported, consistent with the approved scope.

---

## 15. Forecast API

Supports SRS-FR-011–013. Retrieval available to Manager and Admin; Operations Staff visibility is **pending permission confirmation**.

### Generate Forecast
- **Endpoint:** `POST /forecasts`
- **Purpose:** Request forecast generation for a specific date/meal type/location (or trigger the backend's forecasting process for that period, per TRD Section 12's on-demand or scheduled generation approach — exact cadence is a TRD/implementation detail).
- **Request body:**
  ```json
  { "forecastDate": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f" }
  ```
- **Validation:** All three fields required; `locationId`/`mealTypeId` must reference existing, active records.
- **Success response (201 or 200 if returning an existing active forecast per the single-active-forecast model, Database Spec Section 6.8):**
  ```json
  {
    "id": "fc_7g8h9i",
    "forecastDate": "2026-09-01",
    "locationId": "loc_1a2b3c",
    "mealTypeId": "meal_4d5e6f",
    "forecastedDemand": 420,
    "generatedAt": "2026-08-16T10:35:00Z"
  }
  ```
- **Insufficient historical data (SRS-FR-013):**
  ```json
  { "error": { "category": "FORECAST_UNAVAILABLE", "message": "Not enough historical data to generate a reliable forecast for this period." } }
  ```
  Returned with an appropriate 4xx status (Section 28) — **no fabricated forecast value is ever returned.**
- **Forecast generation failure (technical, not data-related):**
  ```json
  { "error": { "category": "FORECAST_UNAVAILABLE", "message": "Forecast is temporarily unavailable. Please try again shortly." } }
  ```

### Retrieve Forecasts
- **Endpoint:** `GET /forecasts`
- **Query params:** `locationId`, `mealTypeId`, `dateFrom`, `dateTo`, `page`, `pageSize`.
- **Response:** Collection envelope of forecast records (same shape as above).

### Retrieve Single Forecast
- **Endpoint:** `GET /forecasts/{forecastId}`
- **Response:** Single forecast record, or `404` if not found.

**No forecasting algorithm is specified anywhere in this API.** The API only consumes the forecasting module's result (`forecastedDemand` value); it has no visibility into or control over the underlying model.

---

## 16. Planned Quantity API

Supports SRS-FR-014–017. Create/Edit authorization for Operations Staff is confirmed; Admin/Manager ability to enter is **pending permission confirmation**. View is available to all roles.

- **`POST /planned-quantities`** — Create a Planned Quantity entry.
  - Request: `{ "planDate": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "quantity": 450 }`
  - Validation: `planDate`, `locationId`, `mealTypeId`, `quantity` all required; `quantity` must be numeric and `>= 0`; `locationId`/`mealTypeId` must reference existing, active records.
  - Uniqueness: One Planned Quantity per (location, meal type, date) — a second `POST` for the same period returns `409 CONFLICT` with guidance to use `PATCH` instead (per Database Spec Section 17's recommended uniqueness constraint).
  - Response (201): the created record, including `enteredByUserId` (from the authenticated session) and `createdAt`/`updatedAt`.
- **`GET /planned-quantities`** — List/filter. Query params: `locationId`, `mealTypeId`, `dateFrom`, `dateTo`, `page`, `pageSize`.
- **`GET /planned-quantities/{id}`** — Retrieve a single entry, or `404` if none exists for the given ID.
- **`PATCH /planned-quantities/{id}`** — Edit an existing entry.
  - Request: `{ "quantity": 480 }`
  - Validation: same as create for the `quantity` field.
  - **Edit-window rule:** **Not implemented as an API-level restriction.** The SRS explicitly leaves this open (whether editing is restricted after the meal period passes or after a comparison exists — SRS Section 12, Database Spec Section 11). This API allows editing at any time until the rule is confirmed; if later confirmed, it would be enforced as an additional validation check returning `409 CONFLICT` (`BUSINESS_RULE_VIOLATION`) — **this is a proposed extension point, not part of the current contract.**

---

## 17. Comparison API

The Database Specification decided that **Variance is computed dynamically** (Database Spec Section 12) — there is no persisted `variance` table, and this API does not expose CRUD operations for one.

- **Endpoint:** `GET /comparisons`
- **Purpose:** Return the dynamically computed comparison between Forecasted Demand and Planned Quantity for one or more periods.
- **Query params:** `locationId` (optional), `mealTypeId` (optional), `date` (single date) or `dateFrom`/`dateTo` (range).
- **Response (200):**
  ```json
  {
    "data": [
      {
        "date": "2026-09-01",
        "locationId": "loc_1a2b3c",
        "mealTypeId": "meal_4d5e6f",
        "forecastedDemand": 420,
        "plannedQuantity": 450,
        "potentialSurplus": 30,
        "potentialShortage": 0,
        "variancePercentage": 7.14
      }
    ]
  }
  ```
- **Computation (explicitly documented, not a stored value):** `potentialSurplus = plannedQuantity - forecastedDemand` (shown only when positive; otherwise `0`); `potentialShortage = forecastedDemand - plannedQuantity` (shown only when positive; otherwise `0`) — per SRS Section 13. `variancePercentage` is computed relative to `forecastedDemand` where meaningful; **the exact behavior when `forecastedDemand = 0` remains an open edge case** (SRS Section 13, Database Spec Section 29 item — not resolved here; this API will omit or null the field in that case pending confirmation of the intended behavior).
- **If only one of the two source values exists for a period:** the response includes the available value and `null` for the other, with `potentialSurplus`/`potentialShortage`/`variancePercentage` also `null` (comparison cannot be computed) rather than a misleading `0`.

No CRUD endpoints (`POST`/`PATCH`/`DELETE`) exist for comparisons — they are a read-only, computed view.

---

## 18. Classification API

The Database Specification decided that **Classification is derived dynamically** (Database Spec Section 13) — no persisted `classification` table exists, and no CRUD endpoints are created for one.

- **Endpoint:** `GET /classifications`
- **Purpose:** Return the dynamically computed Surplus/Shortage/Balanced status for one or more periods.
- **Query params:** Same as `/comparisons` (`locationId`, `mealTypeId`, `date`/`dateFrom`/`dateTo`).
- **Response (200):**
  ```json
  {
    "data": [
      {
        "date": "2026-09-01",
        "locationId": "loc_1a2b3c",
        "mealTypeId": "meal_4d5e6f",
        "status": "surplus",
        "thresholdApplied": null
      }
    ]
  }
  ```
- **`status`** is one of `"surplus"`, `"shortage"`, `"balanced"`, or `"unavailable"` (if one of Forecasted Demand/Planned Quantity is missing for the period).
- **`thresholdApplied`:** Included for traceability (per Database Spec Section 6, which notes storing the threshold used at classification time) but its value is explicitly `null`/unset in this specification, since **the numeric surplus/shortage threshold itself remains unresolved** (SRS Section 14, Database Spec Section 13/29). **This API does not invent a threshold value.** Once a threshold is confirmed and configured, this field will be populated automatically — no contract change is needed.

No CRUD endpoints exist for classifications — read-only, computed view only, consistent with the Database Specification's dynamic-derivation decision.

---

## 19. Recommendation API

Supports SRS-FR-024–027.

- **`GET /recommendations`** — List/filter recommendations. Query params: `locationId`, `mealTypeId`, `dateFrom`, `dateTo`, `page`, `pageSize`.
  - Response: collection envelope of:
    ```json
    {
      "id": "rec_3k4l5m",
      "periodDate": "2026-09-01",
      "locationId": "loc_1a2b3c",
      "mealTypeId": "meal_4d5e6f",
      "estimatedSurplusQuantity": 30,
      "recommendationText": "Potential surplus of 30 meals. Consider reducing the next preparation batch and redirecting available surplus to an approved secondary location.",
      "secondaryLocationId": "loc_9z8y7x",
      "isAdvisory": true,
      "generatedAt": "2026-08-16T10:40:00Z"
    }
    ```
- **`GET /recommendations/{recommendationId}`** — Retrieve a single recommendation, or `404` if not found.

**No `POST /recommendations` endpoint is created.** Per the TRD (Section 17) and the instruction in this task's brief, recommendations are generated by the backend's `recommendations` module automatically when a period is classified Surplus (e.g., as part of the same backend workflow that computes classification, triggered when a forecast/planned-quantity pair produces a Surplus result) — not via an explicit frontend-initiated creation action. This keeps the design simple and avoids exposing a manual "generate a recommendation" capability that the approved workflow does not call for.

`isAdvisory` is always `true` for MVP (Database Spec Section 6.10) and is included specifically to make the advisory, non-executing nature self-evident in every response (SRS-FR-027).

**No endpoints exist for:** route optimization, donor matching, logistics, external systems, or "executing" a recommendation — none of these are part of the approved scope.

---

## 20. Dashboard API

Supports SRS-FR-028–029.

- **Endpoint:** `GET /dashboard`
- **Purpose:** A single aggregated endpoint returning everything the dashboard needs, rather than one endpoint per card (per the TRD's aggregation-module design, TRD Section 18).
- **Query params:** `locationId` (optional), `mealTypeId` (optional), `date` or `dateFrom`/`dateTo` (optional; defaults to a sensible near-term window, e.g., "upcoming periods" — exact default window is an implementation detail not specified by source documents).
- **Response (200):**
  ```json
  {
    "data": [
      {
        "date": "2026-09-01",
        "locationId": "loc_1a2b3c",
        "mealTypeId": "meal_4d5e6f",
        "forecastedDemand": 420,
        "plannedQuantity": 450,
        "potentialSurplus": 30,
        "potentialShortage": 0,
        "variancePercentage": 7.14,
        "status": "surplus",
        "recommendation": {
          "id": "rec_3k4l5m",
          "estimatedSurplusQuantity": 30,
          "recommendationText": "Potential surplus of 30 meals...",
          "isAdvisory": true
        }
      }
    ]
  }
  ```
- The `recommendation` field is `null` when `status` is not `"surplus"`.

This single endpoint composes data from the `forecasts`, `planned-quantities`, `comparisons`/`classifications` logic, and `recommendations` modules server-side (TRD Section 8) — the frontend does not need to call multiple endpoints and merge results itself for the standard dashboard view. (The individual `/comparisons`, `/classifications`, `/forecasts`, `/recommendations` endpoints remain available for more targeted queries where useful.)

---

## 21. Reports API

Supports SRS-FR-030–031.

- **Endpoint:** `GET /reports`
- **Query params:** `dateFrom`, `dateTo` (required — a report without a date range is not a defined use case), `locationId` (optional), `mealTypeId` (optional), `status` (optional — filter by `surplus`/`shortage`/`balanced`, justified by SRS's requirement to show status within reports), `page`, `pageSize`.
- **Response (200):** Same per-period shape as `/dashboard`'s `data` array (date, forecastedDemand, plannedQuantity, variance figures, status), but scoped to historical, filterable ranges rather than "current/upcoming" — plus pagination metadata (Section 7).

**Explicitly not included:** PDF export, CSV export, scheduled/emailed reports — all confirmed Optional/Future (Foundation v1.1, PRD v1.0) and therefore absent from this API.

---

## 22. Filtering, Pagination and Sorting

| Collection | Filters | Pagination | Sorting |
|---|---|---|---|
| `/locations` | `includeInactive` | `page`, `pageSize` (default `pageSize=20`) | Default: `name` ascending |
| `/meal-types` | `includeInactive` | `page`, `pageSize` (default `20`) | Default: `name` ascending |
| `/historical-data/imports` | none (all jobs) | `page`, `pageSize` (default `20`) | Default: `uploadedAt` descending |
| `/forecasts` | `locationId`, `mealTypeId`, `dateFrom`, `dateTo` | `page`, `pageSize` (default `20`) | Default: `forecastDate` ascending |
| `/planned-quantities` | `locationId`, `mealTypeId`, `dateFrom`, `dateTo` | `page`, `pageSize` (default `20`) | Default: `planDate` ascending |
| `/dashboard` | `locationId`, `mealTypeId`, `date` / `dateFrom`/`dateTo` | Not paginated (bounded to a near-term window by nature) | `date` ascending |
| `/reports` | `dateFrom`, `dateTo` (required), `locationId`, `mealTypeId`, `status` | `page`, `pageSize` (default `20`) | Default: `date` descending (most recent first) |
| `/recommendations` | `locationId`, `mealTypeId`, `dateFrom`, `dateTo` | `page`, `pageSize` (default `20`) | Default: `generatedAt` descending |
| `/users` | none | `page`, `pageSize` (default `20`) | Default: `username` ascending |

**Pagination strategy:** A basic page/pageSize approach (`page` starting at 1, `pageSize` capped at a reasonable maximum, e.g., 100) is used throughout — **cursor-based pagination is not implemented**, as no source requirement or expected data volume (internship/single-institution scale, TRD Section 27) justifies the added complexity.

---

## 23. API Validation Rules

| Resource | Field | Rule |
|---|---|---|
| Users | `username` | Required, non-empty, unique |
| Users | `role` | Must be one of `administrator`, `manager`, `operations_staff` |
| Locations | `name` | Required, non-empty, unique |
| Meal Types | `name` | Required, non-empty, unique |
| Historical Data (per row) | `date` | Required, valid calendar date |
| Historical Data (per row) | `locationId`/location reference | Required, must reference a valid, active location |
| Historical Data (per row) | `mealTypeId`/meal type reference | Required, must reference a valid, active meal type |
| Historical Data (per row) | `actualConsumedQuantity` | Required, numeric, `>= 0` |
| Forecasts | `forecastDate`, `locationId`, `mealTypeId` | All required for generation; `locationId`/`mealTypeId` must reference valid, active records |
| Planned Quantities | `planDate`, `locationId`, `mealTypeId` | All required |
| Planned Quantities | `quantity` | Required, numeric, `>= 0` |
| Reports | `dateFrom`, `dateTo` | Required; `dateTo` must not precede `dateFrom` |
| Any date filter (`dateFrom`/`dateTo`) | — | Must be valid ISO 8601 calendar dates |
| Any ID reference (`locationId`, `mealTypeId`, `userId`, etc.) | — | Must reference an existing record, or a `404`/validation error is returned |

No business rules beyond those explicitly supported by the SRS or Database Specification are introduced.

---

## 24. API-Level Business Rules

### Variance (computed, not stored — Section 17)
```text
potentialSurplus  = plannedQuantity - forecastedDemand   (shown when positive)
potentialShortage = forecastedDemand - plannedQuantity   (shown when positive)
```

### Classification (computed, not stored — Section 18)
- `surplus` — `plannedQuantity` exceeds `forecastedDemand` beyond the threshold.
- `shortage` — `forecastedDemand` exceeds `plannedQuantity` beyond the threshold.
- `balanced` — difference within the threshold.
- **Numeric threshold remains unresolved** — the API does not hardcode or infer a value; classification behavior for a given comparison cannot be fully exercised end-to-end until a threshold is configured (consistent with Database Spec Section 13/29).

### Recommendation
- Generated **only** for periods classified `surplus`.
- Rule-based (no ML, no optimization).
- Always `isAdvisory: true`.
- Non-executing — the API never provides a way to mark a recommendation as "acted upon" or to trigger any downstream action; it is read-only from the frontend's perspective once generated.
- No logistics, routing, or donor-matching fields exist anywhere in the recommendation response shape.

---

## 25. API ↔ Database Mapping

| Endpoint | Database Table(s) | Operation |
|---|---|---|
| `POST /auth/login` | `users`, `roles` | Read (credential verification) |
| `POST /users`, `PATCH /users/{id}`, `POST /users/{id}/deactivate` | `users` | Write |
| `GET /users`, `GET /users/{id}` | `users`, `roles` | Read |
| `POST /locations`, `PATCH /locations/{id}`, `DELETE /locations/{id}` | `locations` | Write |
| `GET /locations`, `GET /locations/{id}` | `locations` | Read |
| `POST /meal-types`, `PATCH /meal-types/{id}`, `DELETE /meal-types/{id}` | `meal_types` | Write |
| `GET /meal-types`, `GET /meal-types/{id}` | `meal_types` | Read |
| `POST /historical-data/imports` | `import_job`, `import_record_error`, `historical_consumption` | Write |
| `GET /historical-data/imports`, `GET /historical-data/imports/{id}` | `import_job`, `import_record_error` | Read |
| `POST /forecasts` | `forecasted_demand`, `historical_consumption` (read for generation input) | Write (forecast) / Read (input) |
| `GET /forecasts`, `GET /forecasts/{id}` | `forecasted_demand` | Read |
| `POST /planned-quantities` | `planned_quantity` | Write |
| `GET /planned-quantities`, `GET /planned-quantities/{id}` | `planned_quantity` | Read |
| `PATCH /planned-quantities/{id}` | `planned_quantity` | Write |
| `GET /comparisons` | `forecasted_demand`, `planned_quantity` (dynamic computation, no dedicated table) | Read |
| `GET /classifications` | `forecasted_demand`, `planned_quantity` (dynamic computation, no dedicated table) | Read |
| `GET /recommendations`, `GET /recommendations/{id}` | `redistribution_recommendation` | Read |
| `GET /dashboard` | `forecasted_demand`, `planned_quantity`, `redistribution_recommendation` (aggregated) | Read |
| `GET /reports` | `historical_consumption`, `forecasted_demand`, `planned_quantity` | Read |

This mapping is fully consistent with the locked Database Specification v1.0 — no endpoint implies a table that does not exist there, and no table lacks a corresponding endpoint (see Section 26). Internal schema details (e.g., surrogate key formats, `import_job.status` internal representation) are not exposed beyond what's needed for the response shapes shown above.

---

## 26. API ↔ SRS Traceability

| API Endpoint/Group | SRS Requirement(s) | Purpose |
|---|---|---|
| `/auth/*` | SRS-FR-001–003 | Authentication and role-based authorization support |
| `/users/*` | SRS-FR-004 | User management |
| `/locations/*` | SRS-FR-005 | Location management |
| `/meal-types/*` | SRS-FR-006 | Meal-type management |
| `/historical-data/*` | SRS-FR-007–010 | Historical data upload, validation, storage, import status |
| `/forecasts/*` | SRS-FR-011–013 | Forecast generation, retrieval, insufficient-data handling |
| `/planned-quantities/*` | SRS-FR-014–017 | Planned Quantity entry, edit, view, validation |
| `/comparisons` | SRS-FR-018–020 | Variance calculation and display |
| `/classifications` | SRS-FR-021–023 | Surplus/Shortage/Balanced classification and alert display |
| `/recommendations/*` | SRS-FR-024–027 | Rule-based, advisory recommendation display |
| `/dashboard` | SRS-FR-028–029 | Aggregated summary display with filtering |
| `/reports` | SRS-FR-030–031 | Historical, filterable reporting |

All 31 SRS requirements have a corresponding endpoint/group. No requirement lacks API coverage, and no endpoint exists without a traceable SRS requirement.

---

## 27. API Security Requirements

- **Authenticated access:** Every endpoint except `POST /auth/login` requires a valid session/token (Section 5); an invalid or missing credential returns `401`.
- **Backend-authoritative RBAC:** All role checks (Section 9's Authorization column) are enforced server-side; the frontend's own role-based UI hiding is a convenience only, never the enforcement point (TRD Section 15).
- **Generic authentication failures:** Login failures never reveal whether the username or password was the incorrect part (Section 10).
- **No password/hash exposure:** No endpoint response — including `/users` and `/auth/me` — ever includes `passwordHash` or any credential material.
- **Input validation:** All request bodies are validated against the rules in Section 23 before any business logic executes.
- **Secure transport:** All API traffic occurs over HTTPS; no endpoint is exposed over plain HTTP in a deployed environment.
- **Authorization on every protected action:** Not just endpoint-level checks — e.g., `PATCH /planned-quantities/{id}` verifies not just "is this user Operations Staff" but that the action is permitted by the current (possibly still-unresolved) permission matrix (Section 5).
- **Safe error responses:** Per the Standard Error Model (Section 8) — no internal details leak.
- **No direct database exposure:** No endpoint returns raw database rows, internal IDs beyond opaque resource identifiers, or schema metadata.

No enterprise API gateway, WAF, or dedicated security platform is introduced — not justified at this scale (consistent with TRD Section 20).

---

## 28. Error Response Catalogue

| Error Category | Typical HTTP Status | Example |
|---|---:|---|
| `AUTHENTICATION_ERROR` | 401 | Invalid username or password |
| `FORBIDDEN` | 403 | Operations Staff attempted to upload historical data |
| `NOT_FOUND` | 404 | Location `loc_xyz` not found |
| `VALIDATION_ERROR` | 400 | Quantity must be a non-negative number |
| `DUPLICATE_RESOURCE` | 409 | Username already exists |
| `BUSINESS_RULE_VIOLATION` | 409 | Cannot delete a location referenced by historical data (if the restricted-delete policy is confirmed) |
| `FORECAST_UNAVAILABLE` | 422 | Insufficient historical data to generate a forecast |
| `INTERNAL_ERROR` | 500 | Unexpected server failure |

**Status-code strategy notes (proposed API decisions, not source-mandated):**
- `400` is used for straightforward request-shape/field validation errors; `422` is reserved for requests that are well-formed but cannot be semantically fulfilled (e.g., forecast unavailable) — this distinction is a proposed convention for consistency, not dictated by any source document.
- `409` covers both simple duplicate conflicts and business-rule conflicts (e.g., a blocked deletion) — a single status code with differing `category` values in the body, to keep the status-code surface small and practical.

---

## 29. Open and Deferred API Decisions

The following remain explicitly open and are **not** resolved by this API Specification:
1. Operations Staff permission scope (view access to forecasts, alerts, recommendations, reports) — Section 5, Section 9.
2. Administrator/Manager ability to enter Planned Quantity — Section 5, Section 16.
3. Location deletion behavior (soft-delete/archive vs. restricted delete) — Section 12; the API contract is designed to remain valid under either outcome.
4. Meal-Type deletion behavior — Section 13; same treatment as Location.
5. Duplicate historical-record handling (reject/merge/overwrite) — Section 14; the response shape accommodates a "reject and report" outcome without a guaranteed contract change for other outcomes.
6. Username duplicate UX behavior beyond the generic `409 CONFLICT` — Section 11.
7. Planned Quantity edit-window rule — Section 16; not currently enforced, flagged as a future extension point.
8. Numeric surplus/shortage threshold — Section 18, Section 24; `thresholdApplied` field left `null`/unset.
9. Zero-forecast variance-percentage behavior — Section 17; field omitted/nulled pending confirmation.
10. Minimum historical-data sufficiency threshold — Section 15 (`FORECAST_UNAVAILABLE` condition exists, but the exact data-sufficiency rule triggering it is defined at the ML/backend layer, not the API layer).
11. Forecast versioning strategy — Section 15 (API assumes the Database Specification's "single active forecast per period" recommendation, but this itself is a Database Spec proposed, not confirmed, decision).
12. Final hosting/deployment constraints — Section 4 (`<host>` placeholder only).
13. Any company-mandated technology constraints — not known; the entire API design follows the TRD's proposed (not confirmed) stack.

Where practical (Sections 12, 13, 14, 17, 18), the endpoint contracts are explicitly designed to remain valid across multiple possible resolutions of these open items, so that resolving them later does not require breaking API changes.

---

## 30. API Design Decisions / ADRs

| Decision | Proposed Choice | Reason |
|---|---|---|
| API style | REST | Simple, well-understood integration pattern matching the TRD's chosen architecture (TRD Section 6). |
| Versioning | `/api/v1` path prefix | Allows future breaking changes without disrupting the initial integration; TRD-proposed convention. |
| Field naming | camelCase | Matches idiomatic JSON/TypeScript conventions for the Next.js frontend consuming this API. |
| Response envelope | Raw object for single resources; `{ data, pagination }` for collections | Simpler for the common case; consistent, minimal structure for paginated lists. |
| Authentication | Session/token-based (mechanism-agnostic contract) | Matches TRD's proposed application-level authentication (TRD Section 14); avoids over-engineering with external identity providers. |
| Error model | Single consistent `{ error: { category, message, details? } }` shape | Predictable frontend error handling across all endpoints. |
| Pagination | Page/pageSize (offset-based) | Sufficient for internship-scale data volumes; avoids unjustified cursor-pagination complexity. |
| Comparison/Classification | Read-only computed endpoints, no CRUD, no persisted resource exposed | Matches the Database Specification's decision to compute these dynamically rather than persist them (Database Spec Sections 12–13) — **this is a proposed technical decision that directly follows a database decision, not an independent business decision.** |
| Dashboard | Single aggregated `GET /dashboard` endpoint | Matches TRD's aggregation-module design (TRD Section 18); avoids one endpoint per dashboard card. |
| Authorization | Backend-authoritative; frontend hides UI only for UX | Matches TRD Section 15's explicit statement that backend authorization is authoritative. |
| Recommendation creation | No `POST /recommendations`; generated automatically by backend workflow on Surplus classification | Matches TRD Section 17's design; avoids exposing an unnecessary manual-trigger capability. |

Each row above is a **proposed technical decision** derived from the TRD/Database Specification, not a company-confirmed requirement, except where it directly implements an already-confirmed business rule (e.g., the Variance/Classification formulas themselves, which come from the SRS).

---

## 31. API Documentation Examples

### Login
**Request:**
```json
POST /api/v1/auth/login
{ "username": "jane.manager", "password": "hunter2example" }
```
**Success (200):**
```json
{ "token": "opaque-example-token", "user": { "id": "usr_9f8e7d", "username": "jane.manager", "role": "manager" } }
```
**Failure (401):**
```json
{ "error": { "category": "AUTHENTICATION_ERROR", "message": "Invalid username or password." } }
```

### Historical Data Import
**Request concept:** `POST /api/v1/historical-data/imports` (`multipart/form-data`, file field containing sample synthetic rows — never real SensorSpine data).
**Response (202):**
```json
{ "importId": "imp_5c6d7e", "status": "processing", "uploadedAt": "2026-08-16T10:30:00Z" }
```

### Forecast
**Request:**
```json
POST /api/v1/forecasts
{ "forecastDate": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f" }
```
**Response (200):**
```json
{ "id": "fc_7g8h9i", "forecastDate": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "forecastedDemand": 420, "generatedAt": "2026-08-16T10:35:00Z" }
```

### Planned Quantity
**Request:**
```json
POST /api/v1/planned-quantities
{ "planDate": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "quantity": 450 }
```
**Response (201):**
```json
{ "id": "pq_2n3m4l", "planDate": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "quantity": 450, "enteredByUserId": "usr_1x2y3z", "createdAt": "2026-08-16T10:36:00Z", "updatedAt": "2026-08-16T10:36:00Z" }
```

### Comparison
**Response (200):**
```json
{ "data": [ { "date": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "forecastedDemand": 420, "plannedQuantity": 450, "potentialSurplus": 30, "potentialShortage": 0, "variancePercentage": 7.14 } ] }
```

### Dashboard
**Response (200):**
```json
{ "data": [ { "date": "2026-09-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "forecastedDemand": 420, "plannedQuantity": 450, "potentialSurplus": 30, "potentialShortage": 0, "variancePercentage": 7.14, "status": "surplus", "recommendation": { "id": "rec_3k4l5m", "estimatedSurplusQuantity": 30, "recommendationText": "Potential surplus of 30 meals. Consider reducing the next preparation batch and redirecting available surplus to an approved secondary location.", "isAdvisory": true } } ] }
```

### Report
**Response (200):**
```json
{ "data": [ { "date": "2026-08-01", "locationId": "loc_1a2b3c", "mealTypeId": "meal_4d5e6f", "forecastedDemand": 400, "plannedQuantity": 410, "potentialSurplus": 10, "potentialShortage": 0, "variancePercentage": 2.5, "status": "balanced" } ], "pagination": { "page": 1, "pageSize": 20, "totalItems": 1, "totalPages": 1 } }
```

### Error Response
```json
{ "error": { "category": "VALIDATION_ERROR", "message": "Quantity must be a non-negative number.", "details": [ { "field": "quantity", "issue": "must be >= 0" } ] } }
```

No production URLs, real credentials, or real SensorSpine data appear anywhere in these examples — all values are illustrative/synthetic.

---

## 32. API Review Checklist

**Requirements**
- ✅ All API-relevant SRS requirements (FR-001–031) are covered (Section 26).
- ✅ No future feature (Actual Prepared/Consumed capture, accuracy tracking, PDF/CSV export, external integrations, etc.) became mandatory — none has an endpoint.
- ✅ No out-of-scope endpoint (routing, donor matching, IoT, payments, etc.) was created.

**Database alignment**
- ✅ All resource fields align with the locked Database Specification (Section 25).
- ✅ Variance is not represented as a CRUD table — `/comparisons` is read-only and computed (Section 17).
- ✅ Classification is not represented as a CRUD table — `/classifications` is read-only and computed (Section 18).
- ✅ Historical import uses `import_job`/`import_record_error` (Section 14, Section 25).
- ✅ Forecasts align with the proposed single-active-forecast versioning strategy (Section 15), flagged as a proposed (not confirmed) decision.
- ✅ Planned Quantity aligns with its uniqueness/edit model (Section 16).

**Security**
- ✅ Backend authorization is authoritative (Section 27).
- ✅ Protected endpoints require authentication (Section 9).
- ✅ Password hashes are never returned (Sections 10, 11, 27).

**Simplicity**
- ✅ No unnecessary endpoints — every endpoint traces to an approved capability (Section 26).
- ✅ No GraphQL, no WebSockets, no event-bus APIs, no microservice-specific APIs.

**Open decisions**
- ✅ Unresolved permissions remain unresolved (Section 5, Section 9).
- ✅ Threshold remains unresolved (Section 18, Section 24).
- ✅ Duplicate handling remains unresolved (Section 14).
- ✅ Edit-window rule remains unresolved (Section 16).
- ✅ Deletion safety remains unresolved where applicable, with contract designed to survive either outcome (Sections 12–13).

**Consistency**
- ✅ Endpoint names are consistent (resource-oriented, plural nouns, kebab-case paths).
- ✅ Field naming is consistent (camelCase throughout).
- ✅ Date/timestamp conventions are consistent (ISO 8601 throughout, Section 6).
- ✅ Error responses are consistent (single envelope shape, Section 8).
- ✅ Traceability to SRS is complete (Section 26).

---

## API REVIEW SUMMARY

- **Total endpoint groups:** 12 — Authentication, Users, Locations, Meal Types, Historical Data, Forecasts, Planned Quantities, Comparisons, Classifications, Recommendations, Dashboard, Reports.
- **Total proposed endpoints:** 33 (see the full inventory, Section 9) — 3 auth, 5 user-management, 5 location, 5 meal-type, 3 historical-data, 3 forecast, 4 planned-quantity, 1 comparison, 1 classification, 2 recommendation, 1 dashboard, 1 reports.
- **Major API design decisions:** REST over `/api/v1`; camelCase JSON fields; raw-object responses for single resources with a `{data, pagination}` envelope for collections; a single consistent error shape; offset-based page/pageSize pagination; **no CRUD for Variance or Classification** (both read-only, computed endpoints, directly following the Database Specification's dynamic-derivation decisions); a single aggregated `/dashboard` endpoint; recommendations generated automatically server-side with no manual-creation endpoint.
- **Authentication approach:** Session/token-based login (`POST /auth/login`), logout, and a current-user endpoint (`GET /auth/me`); mechanism-agnostic contract compatible with either server-side sessions or stateless tokens, per the TRD's proposed (not finalized) approach.
- **Authorization approach:** Backend-authoritative role checks on every protected endpoint, using the same three-role permission matrix from SRS v1.0/PRD v1.0; unresolved cells (primarily around Operations Staff visibility and Admin/Manager Planned Quantity entry) are explicitly marked "Pending permission confirmation" throughout rather than resolved.
- **Error model:** A single `{ error: { category, message, details? } }` shape across all endpoints, with a defined category-to-HTTP-status catalogue (Section 28); no internal details (stack traces, DB errors, secrets, password hashes) are ever exposed.
- **Database alignment summary:** Every endpoint's data shape and operation maps cleanly to the locked Database Specification's tables (Section 25) — including correctly treating Variance and Classification as computed, not persisted, consistent with Database Spec Sections 12–13.
- **SRS traceability summary:** All 31 SRS requirements (FR-001–031) map to at least one endpoint/group (Section 26); no requirement is uncovered, and no endpoint lacks a traceable requirement.
- **Deferred API decisions:** 13 items carried forward (Section 29), covering unresolved permissions, deletion-safety policy, duplicate-record handling, edit-window rule, surplus/shortage threshold, zero-forecast edge case, forecast versioning, hosting, and technology-stack constraints — none guessed at.
- **Key API risks:** Endpoints whose authorization is "pending confirmation" (Operations Staff visibility, Admin/Manager Planned Quantity entry) cannot be fully implemented and tested until those cells are resolved; the classification/threshold-dependent endpoints (`/classifications`, `/dashboard` status fields, recommendation generation) cannot be meaningfully exercised end-to-end until a numeric threshold is configured; the deletion endpoints' actual behavior (archive vs. block) is contract-compatible with either outcome but not fully implementable until the Database Specification's open deletion-safety item is confirmed.
- **Contradictions discovered:** None. Foundation v1.1, PRD v1.0, SRS v1.0, TRD v1.0, and Database Specification v1.0 remained internally consistent and translated directly into this API contract without requiring reconciliation.
- **Assumptions introduced:** Only standard, clearly-labeled API-engineering conventions (camelCase naming, ISO 8601 date/time formats, page/pageSize pagination, the specific HTTP status-code mapping in Section 28) — no new product-level or business-rule assumptions were introduced beyond what the five source documents already established.
- **Readiness:** This API Specification is ready to serve as the contract for FastAPI implementation and frontend integration, provided the Open and Deferred API Decisions (Section 29) — particularly the permission-matrix cells and the surplus/shortage threshold — are tracked and resolved during implementation rather than silently decided in code.

**Next planned stage: ML & Testing Plan**

*(The ML & Testing Plan has not been created. No FastAPI source code, Pydantic models, ORM code, SQL, migration files, or frontend implementation has been produced at this stage.)*
