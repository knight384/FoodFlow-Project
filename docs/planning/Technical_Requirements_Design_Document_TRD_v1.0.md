# Technical Requirements / Technical Design Document (TRD) v1.0
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality

---

## 1. Document Control

- **Document title:** Technical Requirements / Technical Design Document (TRD)
- **Project name:** Food-Service Demand Forecasting and Surplus Redistribution System (working title: FoodFlow — placeholder, to be confirmed)
- **Version:** 1.0
- **Status:** Draft, pending review
- **Purpose:** Define how the approved MVP will be technically built — architecture, data model concepts, API approach, ML architecture, security, and deployment strategy — while remaining implementation-level (no code, no full schema, no full API spec).
- **Source documents:** Project Foundation & Scope Definition v1.1; Product Requirements Document (PRD) v1.0; Software Requirements Specification (SRS) v1.0 — all approved.
- **Intended audience:** Project/Product Mentor, Software Developers (implementer), QA/Testers (later stage), Technical Reviewers.

*(No author names or approval dates are stated, as none have been provided.)*

---

## 2. Technical Objectives

The technical architecture must achieve:
- Full support for the end-to-end workflow: historical data → forecast → Planned Quantity → comparison → classification → recommendation → dashboard/reports.
- Maintainability appropriate for a solo/small-team intern project.
- Simplicity — no component exists without a clear justification.
- Demonstrability — the system must be easy to run and show to a mentor.
- Reliable data processing (validation, storage) for historical and planning data.
- A working, real (non-mocked) forecasting capability.
- Secure, role-based access aligned with the three approved roles.
- Easy local development and easy deployment.
- Future extensibility (e.g., adding Actual Prepared/Consumed capture later) without requiring architectural rework.

---

## 3. Architectural Principles

- **MVP-first:** Build only what the approved scope requires.
- **Simplicity over sophistication:** Prefer the simplest architecture that satisfies the requirements.
- **Modularity:** Organize by business capability (auth, data, forecasting, comparison, recommendations, reporting) so each can evolve independently.
- **Separation of concerns:** Presentation, application/business logic, forecasting, and data storage are kept distinct.
- **Secure-by-default:** Authentication and role checks are enforced at the backend for every protected action.
- **Traceability to requirements:** Every technical component maps back to specific SRS requirements (see Section 31).
- **Minimal infrastructure:** No component is introduced unless a real MVP requirement justifies it.
- **Testability:** Business logic (variance, classification, recommendation rules) is structured to be independently testable.
- **Future extensibility without premature abstraction:** The design leaves room for Optional/Future features (Section 22, PRD) without building for them now.

---

## 4. High-Level System Architecture

```text
                        ┌────────────────────────┐
                        │         Users           │
                        │ Admin / Manager / Staff │
                        └───────────┬─────────────┘
                                    ↓
                        ┌────────────────────────┐
                        │   Next.js Frontend      │
                        │ (role-aware UI, forms,  │
                        │  dashboard, reports)    │
                        └───────────┬─────────────┘
                                    ↓  (HTTPS / REST, authenticated)
                        ┌────────────────────────┐
                        │      FastAPI Backend     │
                        ├────────────────────────┤
                        │ Auth / RBAC              │
                        │ User Management          │
                        │ Location / Meal-Type Mgmt│
                        │ Historical Data Mgmt     │
                        │ Forecast Interface        │
                        │ Planned Quantity Mgmt     │
                        │ Comparison / Classification│
                        │ Recommendation Engine     │
                        │ Dashboard / Reports        │
                        └───────┬──────────┬────────┘
                                ↓          ↓
                  ┌────────────────┐  ┌─────────────────────────┐
                  │  PostgreSQL     │  │ Forecasting / ML Module  │
                  │ (all persisted  │  │ (Python, invoked by the  │
                  │  business data) │  │  backend as an internal  │
                  └────────────────┘  │  library/module — not a  │
                                       │  separate network service│
                                       │  unless later justified) │
                                       └─────────────────────────┘
```

**Component rationale:**
- **Next.js Frontend:** Single web client serving all three roles with role-aware views; no separate admin app needed at MVP scale.
- **FastAPI Backend:** Single application exposing all business capabilities as modules (Section 8); Python fits naturally with the forecasting component.
- **PostgreSQL:** Single relational store for all structured business data (users, locations, meal types, historical data, forecasts, planned quantities, classifications, recommendations).
- **Forecasting/ML Module:** Runs as an internal Python module within (or directly callable by) the backend process for MVP simplicity — not a separate microservice, since the added network/deployment complexity is not justified by the current scope. This can be split out later if genuinely needed (see Section 29).

This diagram may be refined during implementation but reflects the simplest structure that satisfies all 31 SRS requirements.

---

## 5. Architecture Style Decision

| Option | Fit for this project |
|---|---|
| **Monolith (single undivided codebase, no internal module boundaries)** | Fast to start but risks becoming tangled as forecasting, business rules, and CRUD logic mix together; harder to reason about later. |
| **Microservices** | Introduces network calls, service discovery, independent deployments, and operational overhead disproportionate to a single-team, single-database, internship-scale MVP. Not justified by current requirements (Section 21, Foundation v1.1 — explicitly out of scope unless genuinely necessary). |
| **Modular monolith (single deployable application, internally organized into clear business-capability modules)** | Matches the project's scale: one small team, one database, one deployable unit, but with clean internal boundaries (Section 8) that make the codebase understandable and allow a module (e.g., forecasting) to be extracted later if truly needed. |

**Decision: Modular monolith.**

**Reasoning:**
- Small project, likely solo/small team (Working Assumption, Foundation v1.1).
- Single, simple deployment target — easier to run locally and demonstrate.
- Easier debugging — one process, one log stream, one database transaction boundary for most operations.
- Lower infrastructure overhead — no service mesh, no inter-service auth, no distributed tracing needed.
- Still provides enough separation (via backend modules, Section 8) to support future extension without a full rewrite.

Microservices are explicitly not selected — this is consistent with Foundation v1.1's exclusion of "unnecessary microservices" and is not chosen for resume value.

---

## 6. Technology Stack

*(All choices below are **proposed technical decisions**, not company-confirmed requirements — see Section 29 for the open "actual company stack constraints" item.)*

| Layer | Proposed Technology | Purpose | Reason |
|---|---|---|---|
| Frontend | Next.js + TypeScript | Web UI for all three roles | Component-based, widely supported, good fit for a role-aware dashboard/forms app; TypeScript reduces runtime errors in a small-team project. |
| Styling | Tailwind CSS | UI styling | Fast to build consistent, clean UI without a heavy design-system dependency. |
| Charts | A lightweight React-compatible charting library (e.g., a standard React charting library) | Dashboard/report visualizations | Needed to satisfy dashboard/report visual requirements (SRS Sections 16–17) without building custom chart rendering. |
| Backend/API | FastAPI (Python) | Application/business logic, REST API | Python-native, integrates naturally with the forecasting module (same language, same process), strong request/response validation built in, good fit for a small backend team. |
| Database | PostgreSQL | Persisted business data | Mature relational database; the data model (Section 10) is inherently relational (users, roles, locations, meal types, historical records, forecasts, planned quantities) — no requirement suggests document/NoSQL flexibility is needed. |
| ML / Data Processing | Python, pandas, and a lightweight forecasting library (algorithm not yet selected) | Historical data preparation and Forecasted Demand generation | Standard, well-supported data-science stack; keeps the ML component in the same language as the backend, simplifying integration. |
| Authentication | Application-level session/token-based authentication (see Section 14) | Login, session management | Simple, sufficient for MVP; no external identity provider needed given the small, closed user base (three internal roles). |
| Validation | FastAPI's built-in request validation (schema-based) | Input validation at the API boundary | Reduces custom validation code; aligns with SRS validation requirements (Section 18, SRS). |
| Testing tools | A standard Python testing framework (backend/unit/integration) and a standard JS/TS testing framework (frontend) — specific libraries to be finalized at implementation | Verify business logic and UI behavior | Testing approach only; specific tools are an implementation detail deferred slightly, but the testing *layers* are defined in Section 25. |
| Version control | Git + GitHub | Source control and collaboration | Standard practice; supports a small-team or solo development workflow. |
| Deployment | Single-host / managed-platform deployment (see Section 22) | Running the application for demo/use | Matches internship scale; avoids unnecessary infrastructure. |

Explicitly **not used** (per Foundation v1.1 exclusions and lack of justification): Redis, Kafka/message brokers, Kubernetes, Docker Swarm, WebSockets, service meshes, complex multi-region cloud infrastructure.

---

## 7. Frontend Architecture

- **Application structure:** A single Next.js application with role-aware routing — the same application serves Administrator, Manager, and Operations Staff, with navigation and available pages adapted to the authenticated user's role.
- **Route organization:** Logical route groups mirroring backend modules — e.g., authentication, dashboard, forecasts, planned-quantities, locations, meal-types, historical-data (Admin only), reports.
- **Page/module organization:** Pages correspond to major user journeys (Section 6, PRD): login, dashboard, forecast view, Planned Quantity entry/edit, historical data upload (Admin), location/meal-type management (Admin), reports.
- **Reusable component strategy:** Shared components for forms (Planned Quantity entry), tables (historical data, reports), status badges (Surplus/Shortage/Balanced), and recommendation display cards — reused across pages rather than duplicated.
- **Form handling:** Standard form-state handling for Planned Quantity entry/edit and Admin management forms, with client-side validation mirroring (not replacing) backend validation.
- **Data fetching:** Server-driven data fetching from the FastAPI backend for dashboard, forecasts, and reports; no separate data layer beyond calling the backend's REST API.
- **Client/server responsibilities:** The frontend is presentation and interaction only — no business logic (variance calculation, classification, recommendation generation) is duplicated on the client. All authoritative logic lives in the backend (Section 9).
- **State management approach:** Local/component-level state plus straightforward data-fetching state (loading/error/success) is sufficient; no heavy global state-management library is introduced, since the app's state needs are modest (current user/session, current view's data).
- **Authentication state:** The frontend tracks whether a user is authenticated and their role, to control which navigation/pages are shown — but this is a UX convenience only; the backend remains the authoritative enforcement point (Section 15).
- **Error handling:** Consistent handling of backend error responses (validation errors, unauthorized actions, unavailable forecast, etc.) with clear user-facing messages, per Section 19.
- **Loading states:** Standard loading indicators for data-fetching operations (forecast requests, report queries, historical data uploads).

No frontend code is written here.

---

## 8. Backend Architecture

The backend is organized into the following modules, each owning a clear business capability:

```text
auth                 — login, logout, session/token issuance, role resolution
users                — Administrator-managed user CRUD, role assignment
locations             — location CRUD, availability to other modules
meal-types            — meal-type CRUD, availability to other modules
historical-data       — upload, validation, storage, import status
forecasting           — interfaces with the ML module to produce Forecasted Demand
planned-quantities    — Operations Staff entry/edit/view of Planned Quantity
comparison            — variance and variance-percentage calculation
classification        — Surplus/Shortage/Balanced threshold logic
recommendations       — rule-based redistribution recommendation generation
dashboard             — aggregates data from the above modules for summary display
reports               — historical, filterable reporting queries
```

**Module boundaries and responsibilities:**
- `auth` is the only module that issues sessions/tokens and resolves the current user's role; all other modules depend on it for authorization checks, not for direct database access to user credentials.
- `locations` and `meal-types` are simple reference-data modules consumed by `historical-data`, `forecasting`, `planned-quantities`, and `reports`.
- `historical-data` owns ingestion and validation; it hands off clean, valid records for `forecasting` to consume — it does not itself generate forecasts.
- `forecasting` is the sole interface to the ML component (Section 12); other modules never call the ML component directly.
- `comparison` and `classification` are pure business-logic modules that consume `forecasting` output and `planned-quantities` input; they do not persist their own separate "source of truth" beyond derived values.
- `recommendations` consumes `classification` output only when a period is Surplus; it does not call any external system.
- `dashboard` and `reports` are read-oriented aggregation modules — they compose data from the modules above rather than owning primary data themselves.

No implementation code is defined here — only module responsibilities and boundaries.

---

## 9. Business Logic Architecture

- **Forecast generation** — lives in the **Forecasting/ML module** (Section 12); the backend's `forecasting` module is a thin interface over it.
- **Variance calculation** — lives in the backend's **business logic layer** (`comparison` module), applying the approved formulas (Section 10, PRD/SRS): Potential Surplus = Planned Quantity − Forecasted Demand; Potential Shortage = Forecasted Demand − Planned Quantity.
- **Surplus/Shortage classification** — lives in the backend's **business logic layer** (`classification` module), applying the threshold rule (numeric threshold itself is an open/configurable parameter — see Section 29).
- **Redistribution recommendation** — lives in the backend's **rule-based business logic layer** (`recommendations` module); explicitly not part of the ML/forecasting module, since it is deterministic rule logic, not a learned model (consistent with Foundation v1.1 and PRD Section 9/15).

**Interaction flow:** `forecasting` produces Forecasted Demand → `comparison` combines it with `planned-quantities` data to compute variance → `classification` applies the threshold to variance → `recommendations` reacts only to a Surplus classification. Each module has a single, clear input/output boundary, making the pipeline traceable and testable in isolation.

---

## 10. Data Architecture

*(Conceptual entities only — no SQL schema, indexes, migrations, or ORM code are defined here; that belongs to the Database Specification stage.)*

- **User** — Purpose: represents an authenticated system user. Conceptual fields: identifier, credentials reference, assigned Role, active/deactivated status. Relationships: has one Role; may be referenced by Planned Quantity entries (who entered it) and Historical Data uploads (who uploaded it).
- **Role** — Purpose: defines the permission set (Administrator, Manager, Operations Staff). Relationships: assigned to exactly one User per account.
- **Location** — Purpose: represents a cafeteria/food-service site. Conceptual fields: identifier, name. Relationships: referenced by Historical Consumed Quantity, Forecasted Demand, Planned Quantity, Classification, and Recommendation records.
- **Meal Type** — Purpose: represents a configurable meal category (e.g., Breakfast, Lunch, Dinner). Conceptual fields: identifier, name. Relationships: same referencing pattern as Location.
- **Historical Consumed Quantity** — Purpose: historical record used to train/inform forecasting. Conceptual fields: date, day of week, meal type reference, location reference, quantity. Relationships: references Meal Type and Location; consumed by the Forecasting module.
- **Forecasted Demand** — Purpose: system-generated prediction for a future period. Conceptual fields: date, meal type reference, location reference, predicted quantity, generation metadata (e.g., when it was generated). Relationships: references Meal Type and Location; consumed by Comparison.
- **Planned Quantity** — Purpose: staff-entered intended preparation quantity. Conceptual fields: date, meal type reference, location reference, quantity, entered-by (User reference), last-updated metadata. Relationships: references Meal Type, Location, and User; consumed by Comparison.
- **Variance** — Purpose: derived comparison value between Forecasted Demand and Planned Quantity for a period. Conceptual fields: period reference (date/meal type/location), Potential Surplus value, Potential Shortage value, variance percentage (where computable). Relationships: derived from Forecasted Demand and Planned Quantity; consumed by Classification.
- **Classification** — Purpose: derived Surplus/Shortage/Balanced status for a period. Conceptual fields: period reference, status label, threshold value used (for traceability). Relationships: derived from Variance; consumed by Recommendations and Dashboard/Reports.
- **Redistribution Recommendation** — Purpose: rule-based advisory recommendation for a Surplus-classified period. Conceptual fields: period reference, estimated surplus quantity, recommendation text, advisory flag (always true for MVP). Relationships: derived from Classification.
- **Import Job / Import Result** — Purpose: represents a historical-data upload event and its outcome, needed to satisfy SRS-FR-010 (view import status). Conceptual fields: initiated-by (User reference), timestamp, total records processed, valid count, invalid count, per-record failure reasons. Relationships: references User; produces the valid records that become Historical Consumed Quantity entries.

No entity here represents Actual Prepared Quantity or forward-looking Actual Consumed Quantity capture, as these remain Optional/Future (PRD Section 7) — but the conceptual model does not preclude adding them later (e.g., as a straightforward extension referencing the same Location/Meal Type/date period).

---

## 11. Data Flow Architecture

### Historical data flow
```text
Administrator Upload
        ↓
Validation (required fields, valid dates, valid quantities,
            valid meal type/location references, structural checks)
        ↓
Split: Valid records            Invalid records
        ↓                              ↓
   Store as Historical            Reported with reasons
   Consumed Quantity              (Import Result)
        ↓
Available to the Forecasting module
```

### Forecast flow
```text
Historical Consumed Quantity (stored)
        ↓
Forecasting/ML module (Section 12)
        ↓
Forecasted Demand (per date/meal type/location)
        ↓
Stored and made available for display and Comparison
```

### Comparison flow
```text
Forecasted Demand   +   Planned Quantity
        (same date/meal type/location)
                ↓
          Variance calculation
                ↓
      Classification (threshold rule)
                ↓
   Recommendation (only if Surplus)
                ↓
      Dashboard / Reports display
```

Each stage is a clear handoff point: the historical data flow feeds the forecast flow, which combines with independently entered Planned Quantity to drive the comparison flow — no stage silently reaches back into another stage's data without going through its defined interface (the module boundaries in Section 8).

---

## 12. ML / Forecasting Architecture

*(Architecture only — no final algorithm is selected.)*

- **Dataset input:** Historical Consumed Quantity records (date, day of week, meal type, location, quantity), retrieved from PostgreSQL via the backend's `forecasting` module interface.
- **Preprocessing:** Cleaning and structuring historical records into a form usable for forecasting (e.g., grouping by date/meal type/location, handling missing periods) — exact preprocessing steps depend on the eventual algorithm and are not defined here.
- **Feature preparation:** Derivable signals such as day-of-week patterns may be used; exact feature set is deferred to the ML implementation stage, once dataset characteristics are understood (consistent with Foundation v1.1, Section 15).
- **Training/inference separation:** The architecture distinguishes a training step (learning patterns from historical data) from an inference step (producing a Forecasted Demand for a specific future date/meal type/location). These may run on different cadences (e.g., retraining periodically, inference on-demand or scheduled) — exact cadence is an implementation decision.
- **Model artifact concept:** Whatever model is eventually chosen is expected to produce a reusable "trained state" (a model artifact) that inference can load, rather than retraining from scratch on every request — the specific storage mechanism (file, database, or otherwise) is deferred.
- **Prediction interface:** The Forecasting/ML module exposes a single internal interface to the backend's `forecasting` module: given a date/meal type/location, return a Forecasted Demand value or a clear "insufficient data" / "unavailable" signal (see SRS-FR-013).
- **Forecast storage:** Generated Forecasted Demand values are persisted (per the Forecasted Demand entity, Section 10) so they can be displayed, compared, and included in historical reports without needing to be regenerated on every view.
- **Model evaluation concept:** Not required for MVP success criteria (no accuracy target is mandated — PRD Section 16), but the architecture does not preclude adding evaluation against Actual Consumed Quantity later (Optional/Future, per Foundation v1.1/PRD).
- **Handling insufficient historical data:** The Forecasting/ML module is responsible for determining when it cannot produce a reliable forecast and communicating this back through the prediction interface, rather than the backend inferring this independently. The exact minimum-data threshold is an open decision (Section 29).
- **Future model replacement capability:** Because the module exposes a single, narrow prediction interface (date/meal type/location → Forecasted Demand or unavailability signal), the underlying algorithm can be replaced later without changes to the backend's other modules or the frontend.

**Interface with FastAPI:** The Forecasting/ML module runs as an internal Python module callable directly by the `forecasting` backend module within the same application process (consistent with the modular-monolith decision, Section 5) — not as a separate network service, unless a future, justified need (e.g., significantly different scaling or resource requirements) emerges.

No specific algorithm (regression-based, tree-based, time-series-specific, or neural) is selected in this document.

---

## 13. Historical Data Processing Architecture

- **Accepted input:** A dataset (e.g., file upload) containing date, day of week, meal type, location, and Actual Consumed Quantity per record.
- **Validation:** Structural checks (readable format), required-field checks, valid-date checks, valid-quantity checks (numeric, non-negative), and valid meal-type/location reference checks (Section 10, SRS).
- **Normalization:** Consistent internal representation of dates, meal-type/location references, and quantities before storage (exact normalization rules are an implementation detail, not defined here).
- **Duplicate handling placeholder:** The architecture includes an explicit checkpoint in the validation flow (between "structural/field validation" and "store as valid") where a duplicate-detection rule *could* be applied. **The rule itself (reject, merge, or overwrite) is not defined here**, consistent with the SRS's explicit statement that this is unresolved. The Import Result entity (Section 10) is designed generically enough (per-record outcome + reason) to represent whatever duplicate policy is eventually chosen, without needing a data-model change.
- **Invalid record handling:** Invalid records are excluded from storage and reported individually with a reason, captured in the Import Result entity.
- **Storage:** Valid records are persisted as Historical Consumed Quantity entries (Section 10).
- **Import status:** The Import Job/Import Result entity supports the Administrator's ability to view total/valid/invalid counts and reasons (SRS-FR-010) without needing a separate reporting mechanism.

---

## 14. Authentication and Authorization Architecture

- **Authentication flow:** User submits credentials → backend `auth` module verifies them → on success, a session/token is issued and returned to the frontend; on failure, a generic error is returned (no indication of whether username or password was incorrect), consistent with SRS-FR-001.
- **Session/token approach:** A standard application-level session or token mechanism (e.g., a signed token or server-side session) sufficient for a small, closed user base of three roles. The specific mechanism (server session vs. stateless token) is an implementation decision; either is appropriate at this scale, and no external identity provider is required.
- **Authorization:** Every protected backend operation checks the authenticated user's role against the required permission before proceeding (Section 15).
- **Role checks:** Performed centrally in the backend (e.g., a shared authorization check invoked by each module) rather than duplicated ad hoc in each endpoint, to keep enforcement consistent.
- **Protected routes (frontend):** Pages are conditionally rendered/navigable based on the user's role, purely for UX — this is not the enforcement boundary (Section 15).
- **Protected API operations (backend):** Every module's operations (Section 8) declare which role(s) may invoke them; this is the authoritative enforcement point.
- **Account deactivation behavior:** A deactivated account cannot authenticate (SRS-FR-004); reactivation behavior is not specified in the source documents and is not invented here.

Not included: social login, multi-factor authentication, external identity providers — none are required by the source documents.

---

## 15. Permission Architecture

Role checks occur in two layers:
```text
Frontend visibility   — determines what is shown/navigable (UX convenience only)
        +
Backend authorization — determines what is actually permitted (authoritative)
```

**Backend authorization is authoritative.** Even if a UI element is hidden, the backend independently enforces the permission on every request.

**Baseline permission matrix (carried unchanged from SRS v1.0, Section 6):**

| Capability | Admin | Manager | Operations Staff |
|---|---|---|---|
| Login | ✓ | ✓ | ✓ |
| Manage Users | ✓ | — | — |
| Manage Locations | ✓ | View | View |
| Manage Meal Types | ✓ | View | View |
| Upload Historical Data | ✓ | — | — |
| View Forecasted Demand | ✓ | ✓ | **Unresolved** |
| Enter Planned Quantity | **Unresolved** | **Unresolved** | ✓ |
| View Surplus/Shortage Alerts | ✓ | ✓ | **Unresolved** |
| View Redistribution Recommendations | ✓ | ✓ | **Unresolved** |
| View Reports | ✓ | ✓ | **Unresolved (Limited, per PRD)** |

**These "Unresolved" cells are not resolved in this TRD.** The authorization layer is designed to be configuration-driven per role/capability (rather than hardcoded per endpoint) specifically so that resolving these cells later is a configuration change, not a structural one.

---

## 16. API Architecture

*(High-level approach only — full request/response field definitions belong to the API Specification stage.)*

- **API style:** REST, using standard HTTP methods (GET for reads, POST for creates/actions, PUT/PATCH for updates, DELETE for removals), consistent with FastAPI's conventions.
- **Versioning approach:** A simple path-based version prefix (e.g., a `v1`-style prefix) is anticipated so future breaking changes don't disrupt the initial frontend integration; exact convention is an implementation detail.
- **Request/response conventions:** JSON request and response bodies; consistent structure for success and error responses (Section 19).
- **Authentication handling:** Protected endpoints require the session/token established during login (Section 14); the mechanism for attaching it (header-based) is standard and not elaborated further here.
- **Error response conventions:** A consistent error shape (e.g., a message and an error category) across modules, so the frontend can handle errors uniformly (Section 19).
- **Validation behavior:** Request validation occurs at the API boundary (leveraging FastAPI's schema validation) before business logic executes, consistent with SRS validation requirements.
- **Resource/module boundaries:** API resource groupings mirror the backend modules (Section 8).

**High-level endpoint map (illustrative, not exhaustive):**
```text
/auth
/users
/locations
/meal-types
/historical-data
/forecasts
/planned-quantities
/comparisons
/classifications
/recommendations
/dashboard
/reports
```

No individual request/response field is defined here.

---

## 17. Recommendation Engine Architecture

The recommendation engine (backend `recommendations` module) is deliberately minimal:

1. Receives a Surplus classification for a period (from the `classification` module).
2. Determines the estimated surplus quantity (Planned Quantity − Forecasted Demand, from the `comparison` module's output).
3. Applies predefined rules (e.g., a rule mapping surplus-quantity ranges to suggested actions, and optionally referencing a configured secondary location if one exists).
4. Produces advisory recommendation text.
5. Returns the recommendation to the calling module (`dashboard`/`reports`) for display.
6. **Never** executes any external action — it only produces text and data for human review.

**Explicitly excluded from this engine's architecture:** route optimization, donor/recipient matching, logistics optimization, and any external system integration — consistent with Foundation v1.1, PRD Section 15/18, and SRS Section 15.

---

## 18. Dashboard / Reporting Architecture

### Dashboard
Data required, aggregated by the `dashboard` module from underlying modules:
- Forecasted Demand (from `forecasting`)
- Planned Quantity (from `planned-quantities`)
- Variance and variance percentage where meaningful (from `comparison`)
- Surplus/Shortage/Balanced status (from `classification`)
- Relevant alerts (periods flagged Surplus/Shortage)
- Recommendations (from `recommendations`, for Surplus periods)
- Filters by location, meal type, and date (Section 6, SRS)

### Reports
Data required, served by the `reports` module:
- Historical Forecasted Demand vs. Planned Quantity records
- Date-range, location, and meal-type filters
- Status visibility (Surplus/Shortage/Balanced) per historical record

Neither the dashboard nor the reports module owns primary data — both compose it from the modules that do (Section 8), keeping a single source of truth for each data concept.

No final visual design, chart types, or color scheme is defined here.

---

## 19. Error Handling Architecture

| Category | Example | High-level approach |
|---|---|---|
| Authentication errors | Invalid credentials | Generic error message; no session issued; no indication of which credential was wrong. |
| Authorization errors | Role attempts a restricted action | Action blocked; user informed the action is not permitted; no partial execution. |
| Validation errors | Missing/invalid field in a form or upload | Rejected at the API boundary with a clear, field-level message where practical. |
| Data import errors | Malformed or invalid historical records | Reported per-record with a reason (Import Result); valid records still processed. |
| Forecast availability errors | Insufficient historical data | Clear "forecast not available" message; no fabricated value returned. |
| Forecast generation failures | Technical failure in the ML module | "Forecast temporarily unavailable" message; other system functions unaffected. |
| Business-rule errors | e.g., invalid combination of filters | Clear message describing the issue; no silent failure. |
| Not-found errors | Requested location/meal-type/record does not exist | Clear "not found" response. |
| Internal server errors | Unexpected technical failure | Generic, non-leaking error message to the user; details available only in server-side logs (Section 26). |

A consistent, module-agnostic error response shape is used across the API so the frontend can handle all categories uniformly. Exact HTTP status codes per endpoint are deferred to the API Specification stage.

---

## 20. Security Architecture

- **Authentication:** Required for all system access beyond the login page itself (Section 14).
- **Authorization:** Enforced authoritatively at the backend for every module operation (Section 15).
- **Password handling:** Passwords (or equivalent credentials) are never stored or transmitted in plain text; standard secure hashing is used for storage (specific algorithm is an implementation detail, not selected here, but must be an established, non-reversible hashing approach).
- **Session/token security:** Tokens/sessions are transmitted over HTTPS only; expiration behavior is applied (exact duration is an implementation decision).
- **Input validation:** Enforced at the API boundary (Section 16) to reduce injection and malformed-data risks.
- **Sensitive data handling:** User credentials are the primary sensitive data at this scale; no payment data, health data, or other high-sensitivity categories exist in this system's scope (consistent with Out-of-Scope items).
- **Secure configuration:** Secrets (database credentials, signing keys) are kept out of source control (Section 21).
- **Least privilege:** Each role is granted only the operations defined in the permission matrix (Section 15); database access from the application uses credentials scoped to what the application needs, not administrative database privileges.
- **Auditability:** Historical data import events already capture who performed an upload and when (Import Job entity, Section 10); this provides a basic audit trail without a dedicated audit-logging subsystem.
- **Protection against common web risks:** Standard practices (parameterized queries via the ORM/database layer to prevent injection, output encoding to prevent script injection in the frontend, HTTPS in transit) are assumed as baseline engineering practice, not itemized as separate "products."

This is explicitly **not** an enterprise-grade security posture — no claim of formal compliance, penetration testing, or advanced threat monitoring is made, consistent with the MVP's scope.

---

## 21. Configuration and Environment Strategy

Conceptual configuration areas (no actual secret values are defined; illustrative names only):
- **Database connection** — connection details supplied via environment configuration, not hardcoded.
- **Authentication secrets** — signing/session secrets supplied via environment configuration.
- **ML/model location** — a configured path or location for the forecasting module's model artifact (Section 12), not hardcoded into application code.
- **Application configuration** — general settings (e.g., which environment is active) supplied via environment variables.
- **Environment separation** — three conceptual environments:
  - **Development** — local developer setup, sample/synthetic data.
  - **Test** — used for automated testing (Section 25), isolated from development/demo data.
  - **Production/Demo** — the environment used to demonstrate the working system to the mentor/stakeholders.

Secrets are never committed to source control; environment-specific values are supplied at runtime through standard environment-variable mechanisms.

---

## 22. Deployment Architecture

| Option | Assessment |
|---|---|
| Single-host deployment (frontend + backend + database on one host or a small set of simply-managed services) | Simplest to set up and reason about; matches internship scale and a single small team. |
| Managed frontend + managed backend (e.g., separately hosted frontend and backend, managed database) | Slightly more moving parts than single-host, but still simple; may be convenient if using platform-specific hosting for Next.js and FastAPI separately. |
| Containerized monolith (single container image running the modular monolith, plus a managed database) | Adds a small amount of packaging complexity but improves consistency between development and demo environments. |

**Decision:** A simple deployment — either a single-host setup or a containerized monolith with a managed PostgreSQL instance — is appropriate. The specific choice between these two closely related options is left as an implementation-stage decision (Section 29), since both satisfy the "simple, intern-deployable" requirement equally well; the deciding factor (available hosting platform, mentor/company preference) is not yet known.

**Explicitly excluded:** Kubernetes, multi-region deployment, and complex cloud architecture — none are justified by the MVP's scale (single institution, small number of concurrent users, per Foundation v1.1).

---

## 23. Development Environment

- **Local development prerequisites:** A Node.js runtime (for the Next.js frontend) and a Python runtime (for the FastAPI backend and ML module), plus a local or containerized PostgreSQL instance.
- **Runtime versions:** Specific version pinning is an implementation detail, to be finalized when development begins (not defined here).
- **Package management:** Standard package managers for each ecosystem (a Node.js package manager for the frontend; a Python package manager for the backend/ML).
- **Environment variables concept:** Local development uses a local environment configuration file (not committed to source control) mirroring the categories in Section 21.
- **Database setup approach:** A local PostgreSQL instance (or containerized equivalent) initialized with the conceptual schema once the Database Specification stage defines it.
- **Migration approach (conceptual):** Schema changes are expected to be managed through a migration mechanism (specific tool deferred to the Database Specification stage) rather than manual, untracked database changes.
- **Linting/formatting:** Standard linting/formatting tools for each language are expected to keep the codebase consistent across contributors; specific tool choice is an implementation detail.
- **Git workflow:** A simple branch-based workflow (e.g., feature branches merged into a main branch) appropriate for a solo/small-team project; no complex branching strategy is warranted at this scale.

No implementation code, exact version numbers, or configuration file contents are provided here.

---

## 24. Repository / Project Structure

```text
foodflow/
├── frontend/        # Next.js application (all three roles' UI)
├── backend/         # FastAPI application, organized by module (Section 8)
├── ml/              # Forecasting/ML module (preprocessing, training, inference interface)
├── docs/            # Project documentation (Foundation, PRD, SRS, TRD, and future docs)
├── data/            # Sample/synthetic historical datasets used for development and demo
├── scripts/         # Small utility scripts (e.g., local setup helpers) — kept minimal
└── README.md        # Project overview and setup instructions
```

**Rationale:** A single repository (monorepo-style, but simple) keeps the frontend, backend, and ML module together for a small team, avoiding the overhead of coordinating multiple repositories at this scale. Each top-level directory maps directly to a major technical concern, avoiding unnecessary sub-packaging. The `ml/` directory is kept separate from `backend/` to reflect that it is a distinct concern (Section 12) even though it runs within the same deployable process for MVP simplicity (Section 5).

---

## 25. Testing Architecture

*(Testing layers only — no detailed test cases; that is a later-stage document.)*

- **Unit testing:** Business logic functions (variance calculation, classification, recommendation rule application) are the highest-priority unit-test targets, since they are pure, deterministic logic (Section 9).
- **Integration testing:** Verifies that backend modules correctly interact end-to-end (e.g., a historical data upload flows correctly into a forecast being generated; a Planned Quantity entry correctly triggers a comparison once a forecast exists).
- **API testing:** Verifies that API endpoints (Section 16) enforce authentication/authorization (Section 15), return correct data shapes, and handle validation/error cases (Section 19) as specified.
- **Frontend/component testing:** Verifies that key UI components (Planned Quantity form, status badges, recommendation display) render and behave correctly given various data states (including error and loading states, Section 7).
- **End-to-end testing:** Verifies the core user journeys (PRD Section 6) work correctly across the full stack — e.g., Administrator uploads data → Manager sees a forecast → Staff enters Planned Quantity → system shows a Surplus alert and recommendation.
- **ML evaluation:** Not a formal test-plan requirement for MVP success (no accuracy target mandated), but the architecture supports comparing Forecasted Demand to real outcomes later if/when forward-looking Actual Consumed Quantity capture (Optional/Future) is added.

Detailed test cases are deferred to a later testing-stage document.

---

## 26. Observability and Logging

Kept lightweight, appropriate for MVP scale:
- **Application logs:** Standard server-side logs for request handling, errors, and key business events.
- **Authentication/security events:** Login successes/failures and authorization denials are logged, supporting basic traceability without a dedicated security-monitoring product.
- **Data import events:** Each historical data upload's outcome (Import Job/Import Result, Section 10) is inherently logged as business data, and may also be reflected in application logs.
- **Forecasting failures:** Logged when the ML module cannot produce a forecast (whether due to insufficient data or a technical failure), to help diagnose issues during development and demonstration.
- **Important business-process errors:** Errors in the comparison/classification/recommendation pipeline are logged to aid debugging.

No full observability stack (metrics dashboards, distributed tracing, alerting infrastructure) is introduced — not justified at this scale.

---

## 27. Performance and Scalability

- **Design target:** A single institution's dataset (one or a small number of locations, per Foundation v1.1's working assumption) and a small number of concurrent users (three roles, internship-scale usage).
- **Likely bottlenecks:** Forecast generation (if computationally heavier than simple CRUD operations) and historical data validation/import for larger file uploads are the most likely points of slower performance — both are naturally bounded at this project's scale and not expected to be problematic.
- **Future scaling (discussion only, not designed for now):** If the system were to grow to multiple institutions or much larger datasets, the modular monolith's clear module boundaries (Section 8) would make it feasible to extract a module (e.g., forecasting) into a separate service later — but this is explicitly not built now, consistent with the MVP-first principle.

No enterprise-scale performance targets, concurrency numbers, or SLAs are defined, as none have been confirmed as required.

---

## 28. Technical Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Limited historical data available (real or synthetic) | Use synthetic/sample data as a working fallback (already an approved assumption); design the ML interface to clearly signal insufficient data rather than fail silently (SRS-FR-013). |
| Poor data quality in uploads | Robust validation at ingestion (Section 13); clear per-record reporting so issues are visible and correctable. |
| Forecasting model limitations (a simple model may be imprecise) | No accuracy target is required for MVP success; the ML interface (Section 12) allows the model to be replaced later without touching other modules. |
| Threshold ambiguity (surplus/shortage cutoff undefined) | Design classification (Section 9) around a configurable threshold parameter rather than a hardcoded value, so the eventual number can be set without code changes. |
| Unresolved role permissions | Design authorization (Section 15) to be configuration-driven per role/capability, so resolving the open cells later is a configuration change, not a structural one. |
| Unclear deployment constraints (hosting platform not yet known) | Choose a deployment approach (Section 22) that works equally well in either a single-host or simple containerized setup, deferring only the final hosting choice. |
| Scope creep (pressure to add routing, matching, optimization, IoT, etc.) | Explicit architectural exclusions stated throughout (Sections 5, 12, 17, 20, 22); any such addition requires a documented scope change, not an incidental technical decision. |

---

## 29. Deferred Technical Decisions

The following remain explicitly open and are **not** resolved in this TRD:
1. Exact forecasting algorithm (Section 12).
2. Minimum historical-data sufficiency threshold for forecast generation (Section 12).
3. Numeric surplus/shortage threshold value (Section 9/14, business rule).
4. Duplicate historical-record handling policy (Section 13).
5. Planned Quantity edit-window rule (carried from SRS Section 12).
6. Zero-forecast variance-percentage edge-case behavior (carried from SRS Section 13).
7. Location/meal-type deletion-safety strategy (block/cascade/archive) (Sections 8–9, SRS).
8. User account duplicate-identifier handling (carried from SRS Section 7).
9. Unresolved role-permission cells (Section 15/PRD Section 13/SRS Section 6).
10. Actual company technology-stack constraints, if any (Section 6 — current stack is proposed, not confirmed).
11. Real vs. synthetic dataset availability (Foundation/PRD/SRS — carried forward).
12. Final deployment target/hosting platform (Section 22 — narrowed to two closely related simple options, not finalized).

None of these are guessed at or silently resolved in this document.

---

## 30. Architecture Decision Records

| Decision | Choice | Why |
|---|---|---|
| Architecture style | Modular Monolith | Simple, maintainable, appropriate for a small team and internship scale; avoids unjustified microservices overhead. |
| Frontend | Next.js + TypeScript | Component-based web UI fit for a role-aware dashboard/forms application; TypeScript reduces errors in a small codebase. |
| Styling | Tailwind CSS | Fast, consistent styling without a heavy design-system dependency. |
| Backend | FastAPI (Python) | Natural fit with the Python-based ML module; strong built-in request validation. |
| Database | PostgreSQL | The data model (Section 10) is inherently relational; no requirement suggests a document/NoSQL store is needed. |
| ML integration | Internal Python module within the backend process | Avoids unjustified network/service overhead of a separate ML microservice at this scale; algorithm itself remains unselected. |
| API style | REST | Simple, well-understood integration pattern between the Next.js frontend and FastAPI backend. |
| Authentication | Application-level session/token auth | Sufficient for a small, closed set of three internal roles; avoids the complexity of external identity providers. |
| Deployment | Single-host or containerized monolith (final choice deferred) | Both are simple and intern-deployable; final choice depends on hosting platform availability, which is not yet known. |

Only decisions with clear justification are included; unresolved items remain in Section 29 rather than being forced into this table.

---

## 31. Requirements Traceability

```text
SRS-FR-001–003  → Auth / RBAC module (Sections 8, 14, 15)
SRS-FR-004      → Users module (Section 8)
SRS-FR-005      → Locations module (Section 8)
SRS-FR-006      → Meal-Types module (Section 8)
SRS-FR-007–010  → Historical Data module (Sections 8, 10, 13)
SRS-FR-011–013  → Forecasting module + Forecasting/ML module (Sections 8, 12)
SRS-FR-014–017  → Planned Quantities module (Sections 8, 10)
SRS-FR-018–020  → Comparison module (Sections 8, 9, 10)
SRS-FR-021–023  → Classification module (Sections 8, 9, 10)
SRS-FR-024–027  → Recommendations module (Sections 8, 9, 17)
SRS-FR-028–029  → Dashboard module (Sections 8, 18)
SRS-FR-030–031  → Reports module (Sections 8, 18)
```

Every one of the 31 SRS requirements has a clear technical home in the module structure defined in Section 8. No requirement is left without an owning component.

---

## 32. Final Technical Blueprint

**Frontend:** Next.js + TypeScript + Tailwind CSS. Responsible for role-aware presentation, forms (especially Planned Quantity entry), dashboard and report visualization, and client-side UX (loading/error states). Contains no authoritative business logic.

**Backend:** FastAPI (Python), organized as a modular monolith (Section 8). Responsible for authentication/authorization, all CRUD operations (users, locations, meal types), historical data ingestion/validation, the comparison/classification/recommendation business logic, and serving the dashboard/reports.

**Database:** PostgreSQL. Conceptual role: the single source of truth for all persisted business data (Section 10) — users, locations, meal types, historical data, forecasts, planned quantities, and derived classification/recommendation records.

**ML:** Python-based Forecasting/ML module, integrated as an internal module within the backend process (not a separate service) for MVP simplicity. Exposes a narrow prediction interface so the underlying algorithm can be selected and later changed without affecting other modules. No algorithm is locked in this document.

**Authentication:** Application-level session/token-based authentication, with backend-enforced, role-based authorization as the single source of truth for permissions (frontend visibility is UX-only).

**Architecture:** Modular monolith — one deployable application with clear internal module boundaries mirroring business capabilities.

**Deployment:** A simple, single-host or containerized-monolith deployment with a managed PostgreSQL instance; final choice between these two options deferred pending hosting-platform information.

**Development approach:** A single repository (Section 24) housing the frontend, backend, and ML module together; developed with standard Git workflow practices suitable for a solo/small-team internship project; components are integrated through the well-defined module interfaces described throughout this document, not through ad hoc coupling.

---

## 33. TRD Review Checklist

**Requirements**
- ✅ All 31 SRS requirements have technical coverage (Section 31).
- ✅ No future feature (Actual Prepared/Consumed capture, accuracy tracking, PDF/CSV export, notifications, external integrations, multi-location analytics, mobile PWA, advanced models) became mandatory.
- ✅ No out-of-scope feature (IoT, computer vision, blockchain, routing, donor matching, external logistics, native apps, payments, unnecessary microservices, enterprise multi-org architecture) was introduced.

**Architecture**
- ✅ Modular monolith selected — appropriate for internship scope.
- ✅ No unnecessary microservices.
- ✅ No Kubernetes.
- ✅ No unnecessary message queues.
- ✅ No unnecessary real-time infrastructure (no WebSockets, no streaming platform).

**Technology**
- ✅ Each major technology choice is justified (Section 6).
- ✅ Proposed stack is explicitly labeled as proposed, not company-confirmed (Sections 6, 29).
- ✅ Chosen technologies are compatible (Next.js/TypeScript frontend, Python/FastAPI backend, PostgreSQL, Python-based ML — a coherent, common combination).
- ✅ Python/ML integration is practical (same-language, same-process integration, Section 12).

**ML**
- ✅ No final ML algorithm selected (Section 12, explicitly deferred).
- ✅ Forecasting module designed to be replaceable/evolvable later via a narrow interface.

**Data**
- ✅ Conceptual entities (Section 10) align exactly with SRS data requirements (SRS Section 19).
- ✅ No contradictory data concepts — Forecasted Demand, Planned Quantity, Actual Prepared/Consumed Quantity remain distinct throughout.

**Security**
- ✅ Authentication and authorization are clearly separated (Sections 14–15).
- ✅ Backend authorization is stated as authoritative; frontend checks are UX-only.

**Deployment**
- ✅ Deployment approach (Section 22) is realistic for an intern to execute.
- ✅ Infrastructure is not unnecessarily complex — no Kubernetes, no multi-region, no unjustified cloud architecture.

**Open Issues**
- ✅ Unresolved decisions (Section 29) remain explicitly unresolved — none are silently resolved elsewhere in the document.
- ✅ No guesses are presented as confirmed requirements.

---

## TRD REVIEW SUMMARY

- **Architecture selected:** Modular monolith — a single deployable application (Next.js frontend, FastAPI backend, PostgreSQL database) with an internally integrated Python-based forecasting module, organized into clear business-capability modules (Section 8).
- **Technology stack selected:** Next.js + TypeScript + Tailwind CSS (frontend); FastAPI/Python (backend); PostgreSQL (database); Python/pandas + an unselected lightweight forecasting approach (ML); application-level session/token authentication; REST API style; Git/GitHub for version control. All explicitly labeled as **proposed**, not company-confirmed.
- **Major technical decisions:** Modular monolith over microservices/pure monolith (Section 5); ML module runs in-process rather than as a separate service (Section 12); REST API style (Section 16); rule-based, non-executing recommendation engine (Section 17); backend-authoritative authorization with configuration-driven permissions to accommodate unresolved role cells (Section 15); single-repository project structure (Section 24).
- **Major deferred decisions:** Final forecasting algorithm; minimum historical-data sufficiency threshold; numeric surplus/shortage threshold; duplicate-record handling policy; Planned Quantity edit-window rule; zero-forecast variance-percentage edge case; location/meal-type deletion-safety strategy; user duplicate-identifier handling; unresolved role-permission cells; actual company technology constraints; real vs. synthetic dataset availability; final deployment/hosting target (Section 29 — 12 items total, none guessed at).
- **Key technical risks:** Limited/synthetic historical data affecting forecast usefulness; data-quality issues at ingestion; forecasting model imprecision (no accuracy target required); undefined threshold values; unresolved permissions; unclear hosting platform; ongoing scope-creep pressure (Section 28) — each paired with a practical, already-designed-for mitigation.
- **Contradictions discovered:** None. Foundation v1.1, PRD v1.0, and SRS v1.0 remained internally consistent and translated directly into this technical design without requiring any reconciliation.
- **Assumptions made:** Only those already carried forward from the Foundation/PRD/SRS as Working Assumptions (Section 22, SRS) — no new assumptions were introduced at the technical layer beyond standard, clearly-labeled engineering defaults (e.g., HTTPS in transit, parameterized queries, secure password hashing) that do not represent product-level decisions.
- **Readiness:** This TRD is ready to serve as the implementation blueprint for the Database Specification and API Specification stages, provided the Deferred Technical Decisions (Section 29) are tracked and resolved as they come up rather than silently decided during implementation.

**Next planned stage: Database + API Specification**

*(The Database Specification and API Specification have not been created. No SQL schema, ER diagram, full API request/response definitions, code, or deployment scripts have been produced at this stage.)*
