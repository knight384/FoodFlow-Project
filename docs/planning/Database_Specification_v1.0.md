# Database Specification v1.0
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality

---

## 1. Document Control

- **Document title:** Database Specification
- **Project name:** Food-Service Demand Forecasting and Surplus Redistribution System (working title: FoodFlow — placeholder, to be confirmed)
- **Version:** 1.0
- **Status:** Draft, pending review
- **Purpose:** Define the complete logical and physical database design required to implement the approved MVP, sufficient for later implementation with minimal ambiguity — without providing SQL scripts, ORM code, or migrations.
- **Source documents:** Project Foundation & Scope Definition v1.1; Product Requirements Document (PRD) v1.0; Software Requirements Specification (SRS) v1.0; Technical Requirements / Technical Design Document (TRD) v1.0 — all approved.
- **Intended audience:** Project/Product Mentor, Backend Developers (implementers), Technical Reviewers, future API Specification author.

*(No author names or approval dates are stated, as none have been provided.)*

---

## 2. Database Objectives

The database must support:
- All approved MVP business data: users/roles, locations, meal types, historical consumed quantity, Forecasted Demand, Planned Quantity, derived variance/classification, and redistribution recommendations.
- Historical data ingestion, including validation outcomes and import-status tracking (SRS-FR-007–010).
- Forecast storage sufficient to support display, comparison, and historical reporting without regenerating forecasts on every view.
- Planned Quantity management, including entry, editing, and viewing (SRS-FR-014–017).
- Comparison and classification of Forecasted Demand vs. Planned Quantity (SRS-FR-018–023).
- Rule-based redistribution recommendations for Surplus periods (SRS-FR-024–027).
- Dashboard and historical reporting queries, including filtering by date/location/meal type (SRS-FR-028–031).
- Authentication and role-based authorization support (SRS-FR-001–004).
- Import status tracking with per-record validation outcomes (SRS-FR-010).

---

## 3. Database Architecture

- **Technology:** PostgreSQL, per TRD v1.0 Section 6. Treated as the selected technology for this technical stage; **not** a company-confirmed mandate (Foundation v1.1 / PRD v1.0 / SRS v1.0 all leave the technology stack as an open item — see Section 29).
- **Single database:** One PostgreSQL database serves the entire MVP. No additional persistence systems (no MongoDB, DynamoDB, Redis-as-primary-store, graph databases, or multiple databases) are introduced, consistent with the TRD's architectural guardrails.
- **Relational model:** All business data is modeled relationally, reflecting the inherently structured nature of the domain (users, locations, meal types, time-series-like historical/forecast/planned data).
- **Access pattern:** The FastAPI backend is the sole data access layer. The frontend never accesses the database directly; all reads and writes go through backend modules (TRD Section 8), which remain authoritative for business logic (validation, comparison, classification, recommendation generation).
- **No direct frontend database access**, consistent with the modular monolith architecture (TRD Section 5).

---

## 4. Logical Data Model

### 4.1 Entity Overview and Representation Decisions

Not every conceptual entity from the TRD becomes its own table. The mapping is:

| Conceptual Entity (TRD) | Relational Representation | Reasoning |
|---|---|---|
| User | Core table (`users`) | Primary business entity; needed for authentication and audit references. |
| Role | Reference table (`roles`), or a constrained value on `users` | See Section 7 — a small, fixed reference table is recommended over a free-text/enum-only approach, for clarity and future flexibility, while keeping a strict one-user-one-role relationship. |
| Location | Core/reference table (`locations`) | Referenced by nearly every other table; simple lookup entity but with enough independent lifecycle (create/update/delete) to be a first-class table, not embedded data. |
| Meal Type | Core/reference table (`meal_types`) | Same reasoning as Location — configurable, independently managed, referenced widely. |
| Historical Consumed Quantity | Core table (`historical_consumption`) | Primary source data for forecasting; a genuine business record, not derived. |
| Forecasted Demand | Core table (`forecasted_demand`) | System-generated but persisted output, needed for display/comparison/reporting without recomputation. |
| Planned Quantity | Core table (`planned_quantity`) | Staff-entered primary business data. |
| Variance | **Not a separate persisted table** — computed dynamically (see Section 12) | Fully derivable from `forecasted_demand` and `planned_quantity` at query time; persisting it risks staleness/duplication for no MVP-scale performance benefit. |
| Classification | **Persisted as a snapshot on-demand, not a separate always-current table** — see Section 13 for the recommended approach | Derived from Variance, but recommendation generation and reporting benefit from a stable, queryable status; recommended as a lightweight persisted snapshot recalculated when its inputs change, rather than a fully independent source of truth. |
| Redistribution Recommendation | Core table (`redistribution_recommendation`) | Genuinely new information (recommendation text, estimated surplus) tied to a Surplus-classified period; not fully re-derivable without recomputation logic, so persisting it is reasonable. |
| Import Job / Import Result | Two related tables (`import_job`, `import_record_error`) | See Section 15 — a job-level summary plus record-level error detail, avoiding both over-normalization and losing per-record traceability. |

### 4.2 ER Diagram (Mermaid)

```text
erDiagram
    ROLES ||--o{ USERS : "assigned to"
    USERS ||--o{ PLANNED_QUANTITY : "entered by"
    USERS ||--o{ IMPORT_JOB : "uploaded by"

    LOCATIONS ||--o{ HISTORICAL_CONSUMPTION : "recorded at"
    MEAL_TYPES ||--o{ HISTORICAL_CONSUMPTION : "categorizes"

    LOCATIONS ||--o{ FORECASTED_DEMAND : "forecast for"
    MEAL_TYPES ||--o{ FORECASTED_DEMAND : "forecast for"

    LOCATIONS ||--o{ PLANNED_QUANTITY : "planned at"
    MEAL_TYPES ||--o{ PLANNED_QUANTITY : "planned for"

    LOCATIONS ||--o{ REDISTRIBUTION_RECOMMENDATION : "primary period at"
    LOCATIONS ||--o{ REDISTRIBUTION_RECOMMENDATION : "optional secondary location"
    MEAL_TYPES ||--o{ REDISTRIBUTION_RECOMMENDATION : "for meal type"

    FORECASTED_DEMAND ||--o| REDISTRIBUTION_RECOMMENDATION : "basis for (via classification)"
    PLANNED_QUANTITY ||--o| REDISTRIBUTION_RECOMMENDATION : "basis for (via classification)"

    IMPORT_JOB ||--o{ IMPORT_RECORD_ERROR : "produces"
    IMPORT_JOB ||--o{ HISTORICAL_CONSUMPTION : "produces valid records"
```

*(Variance and Classification are intentionally not shown as standalone entities in this diagram beyond the recommendation link, since they are primarily derived/query-time or snapshot concepts — see Sections 12–13.)*

### 4.3 Relationships (Prose/Table Form)

| Relationship | Cardinality | Description |
|---|---|---|
| Role → User | 1 to many | Each user has exactly one role; a role may apply to many users. |
| User → Planned Quantity | 1 to many | A user (Operations Staff, typically) may enter many Planned Quantity records over time; each Planned Quantity record has exactly one entering user. |
| User → Import Job | 1 to many | A user (Administrator) may initiate many import jobs; each import job has exactly one initiating user. |
| Location → Historical Consumption | 1 to many | A location has many historical records; each historical record belongs to exactly one location. |
| Meal Type → Historical Consumption | 1 to many | Same pattern as Location. |
| Location → Forecasted Demand | 1 to many | A location has many forecasts over time; each forecast belongs to exactly one location. |
| Meal Type → Forecasted Demand | 1 to many | Same pattern. |
| Location → Planned Quantity | 1 to many | A location has many Planned Quantity entries; each entry belongs to exactly one location. |
| Meal Type → Planned Quantity | 1 to many | Same pattern. |
| Location → Redistribution Recommendation | 1 to many (as primary period location), optionally 1 to many (as secondary/destination location) | A recommendation is tied to one primary location/period and may optionally reference a secondary location. |
| Meal Type → Redistribution Recommendation | 1 to many | A recommendation is tied to one meal type/period. |
| Import Job → Import Record Error | 1 to many | An import job may produce many per-record error entries. |
| Import Job → Historical Consumption | 1 to many | An import job's valid records become historical consumption rows, linked back to the job for traceability (see Section 15). |

---

## 5. Table Inventory

| Table | Purpose | Type | Source Requirement |
|---|---|---|---|
| `roles` | Fixed set of approved roles | Reference | SRS-FR-001–004 |
| `users` | User accounts, authentication, role assignment | Core | SRS-FR-001–004 |
| `locations` | Cafeteria/food-service locations | Core/Reference | SRS-FR-005 |
| `meal_types` | Configurable meal categories | Core/Reference | SRS-FR-006 |
| `historical_consumption` | Historical Actual Consumed Quantity records | Core | SRS-FR-007–011 |
| `import_job` | Historical data upload job summary | Operational/Audit | SRS-FR-007, 010 |
| `import_record_error` | Per-record validation failure detail | Operational/Audit | SRS-FR-008, 010 |
| `forecasted_demand` | System-generated Forecasted Demand values | Core (system-generated, persisted) | SRS-FR-011–013 |
| `planned_quantity` | Staff-entered Planned Quantity values | Core | SRS-FR-014–017 |
| `redistribution_recommendation` | Rule-based recommendations for Surplus periods | Derived/Persisted | SRS-FR-024–027 |

**Not created as separate tables** (see Sections 12–13 for reasoning): a standalone `variance` table and a fully independent, always-current `classification` table. Classification is instead represented as a small set of persisted columns directly on a lightweight per-period record (see Section 13) rather than a separate heavyweight table — this keeps the design simple while still supporting fast dashboard/report queries.

No unnecessary tables (e.g., no separate "audit log" table beyond what's naturally captured by `import_job` and standard audit columns — Section 16; no tables for Actual Prepared Quantity or forward-looking Actual Consumed Quantity, per Section 23).

---

## 6. Detailed Table Specifications

### 6.1 `roles`

**Purpose:** Fixed reference list of the three approved roles.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | SMALLINT | No | — | Primary Key | Small, stable identifier. |
| `name` | VARCHAR(30) | No | — | Unique, Check (one of: `administrator`, `manager`, `operations_staff`) | The approved role name. |

**Note:** A reference table (rather than a free-text column with a check constraint directly on `users`) is chosen because it allows role metadata (e.g., a display label) to be added later without a schema change to `users`, and keeps role values centrally governed. Only three fixed rows are expected — this is a **proposed database decision**, and a simple enum/check-constrained column on `users` would also be valid; the reference-table approach is preferred for minor future flexibility.

---

### 6.2 `users`

**Purpose:** Represents an authenticated system user with exactly one role.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique user identifier (see Section 17 for PK strategy discussion). |
| `username` | VARCHAR(100) | No | — | Unique | Login identifier. Exact duplicate-handling behavior beyond DB-level uniqueness is an open item (Section 29). |
| `password_hash` | VARCHAR(255) | No | — | — | Securely hashed credential (algorithm not selected here — TRD Section 20). Never stores plain text. |
| `role_id` | SMALLINT | No | — | Foreign Key → `roles.id` | Enforces the one-user-one-role rule. |
| `is_active` | BOOLEAN | No | `true` | — | Supports account deactivation (Section 18) without deleting the record. |
| `created_at` | TIMESTAMP | No | current timestamp | — | Audit field (Section 16). |
| `updated_at` | TIMESTAMP | No | current timestamp | — | Audit field, updated on modification. |

**Design note:** A one-user-one-role model is used (`role_id` as a single foreign key, not a join table), matching the SRS's explicit statement that each user has exactly one approved role. A many-to-many role model is deliberately avoided as unjustified complexity.

---

### 6.3 `locations`

**Purpose:** Represents a cafeteria/food-service site.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique location identifier. |
| `name` | VARCHAR(150) | No | — | Unique, Check (non-empty) | Location display name. |
| `is_active` | BOOLEAN | No | `true` | — | Supports the recommended soft-delete/archive strategy (Section 18) rather than hard deletion. |
| `created_at` | TIMESTAMP | No | current timestamp | — | Audit field. |
| `updated_at` | TIMESTAMP | No | current timestamp | — | Audit field. |

---

### 6.4 `meal_types`

**Purpose:** Represents a configurable meal category (e.g., Breakfast, Lunch, Dinner, or others as configured).

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique meal-type identifier. |
| `name` | VARCHAR(100) | No | — | Unique, Check (non-empty) | Meal-type display name. |
| `is_active` | BOOLEAN | No | `true` | — | Supports soft-delete/archive strategy (Section 18). |
| `created_at` | TIMESTAMP | No | current timestamp | — | Audit field. |
| `updated_at` | TIMESTAMP | No | current timestamp | — | Audit field. |

---

### 6.5 `historical_consumption`

**Purpose:** Stores historical Actual Consumed Quantity records used as forecasting input.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique record identifier. |
| `record_date` | DATE | No | — | — | The calendar date of the historical record. |
| `location_id` | UUID/BIGINT | No | — | Foreign Key → `locations.id` | Must reference a valid location. |
| `meal_type_id` | UUID/BIGINT | No | — | Foreign Key → `meal_types.id` | Must reference a valid meal type. |
| `actual_consumed_quantity` | NUMERIC | No | — | Check (`>= 0`) | The historical Actual Consumed Quantity — not "actual_quantity"; kept explicit per approved terminology. |
| `import_job_id` | UUID/BIGINT | Yes | — | Foreign Key → `import_job.id` | Traces which upload produced this record (nullable to allow for a possible future non-upload data-entry path, though not built now). |
| `created_at` | TIMESTAMP | No | current timestamp | — | Audit field. |

**Day of Week — persisted or derived?**
**Recommendation: derive `day_of_week` at query time (e.g., from `record_date`), do not persist it as a column.**
- **Reasoning:** `day_of_week` is fully and unambiguously computable from `record_date` using standard date functions. Persisting it risks inconsistency if `record_date` is ever corrected without updating the derived column, and provides no meaningful query-performance benefit for MVP-scale data (a computed expression or generated column, if desired, can be added at the implementation stage without changing this specification's intent). This avoids redundant, potentially inconsistent data, consistent with the design principle of clearly distinguishing source vs. derived data.

**Uniqueness:** See Section 17 for the recommended uniqueness rule on (`location_id`, `meal_type_id`, `record_date`) — this interacts directly with the unresolved duplicate-handling policy (Section 29) and is discussed there rather than assumed here.

---

### 6.6 `import_job`

**Purpose:** Represents a single historical-data upload event and its summary outcome.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique job identifier. |
| `uploaded_by_user_id` | UUID/BIGINT | No | — | Foreign Key → `users.id` | Administrator who initiated the upload. |
| `uploaded_at` | TIMESTAMP | No | current timestamp | — | When the upload occurred. |
| `total_records` | INTEGER | No | `0` | Check (`>= 0`) | Total records submitted. |
| `valid_records` | INTEGER | No | `0` | Check (`>= 0`) | Count of records that passed validation. |
| `invalid_records` | INTEGER | No | `0` | Check (`>= 0`) | Count of records that failed validation. |
| `status` | VARCHAR(30) | No | — | Check (one of: `processing`, `completed`, `failed`) | High-level job status; exact processing model (synchronous vs. background) is a TRD/implementation concern, not decided here. |

---

### 6.7 `import_record_error`

**Purpose:** Stores per-record validation failure detail for an import job (supports SRS-FR-010).

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique error-record identifier. |
| `import_job_id` | UUID/BIGINT | No | — | Foreign Key → `import_job.id` | Which job this error belongs to. |
| `row_reference` | INTEGER or VARCHAR | No | — | — | Identifies which row/record in the original upload failed (e.g., row number). |
| `failure_reason` | TEXT | No | — | — | Human-readable reason the record was invalid. |
| `raw_data_snapshot` | JSONB or TEXT | Yes | — | — | Optional snapshot of the offending row's raw values, to aid Administrator review without needing to re-open the original file. |

**Design note:** This is a job-level summary (`import_job`) plus a record-level error detail table (`import_record_error`) — a two-table design that avoids over-normalizing (e.g., no separate table per validation-rule type) while still preserving full per-record traceability, as required by SRS-FR-010.

---

### 6.8 `forecasted_demand`

**Purpose:** Stores system-generated Forecasted Demand values for specific future periods.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique forecast-record identifier. |
| `forecast_date` | DATE | No | — | — | The date the forecast is *for* (a future period). |
| `location_id` | UUID/BIGINT | No | — | Foreign Key → `locations.id` | Must reference a valid location. |
| `meal_type_id` | UUID/BIGINT | No | — | Foreign Key → `meal_types.id` | Must reference a valid meal type. |
| `predicted_quantity` | NUMERIC | No | — | Check (`>= 0`) | The Forecasted Demand value. |
| `generated_at` | TIMESTAMP | No | current timestamp | — | When this forecast was generated — supports the TRD's "generation metadata" requirement. |
| `model_version` | VARCHAR(100) | Yes | — | — | Optional lightweight reference to which model/version produced this forecast, for traceability only — **not** a full model registry (TRD Section 12 explicitly avoids this). Nullable since the field is a proposed convenience, not a confirmed requirement. |

**Uniqueness / versioning strategy — proposed decision:**
**Recommendation: one *active* Forecasted Demand per (`location_id`, `meal_type_id`, `forecast_date`), with regeneration replacing (or superseding) the prior value rather than accumulating unlimited historical forecast versions.**
- **Reasoning:** The SRS and PRD describe a single Forecasted Demand value being compared against Planned Quantity per period — there is no stated requirement for multiple simultaneous forecast versions per period. Keeping one active row per period keeps comparison and reporting simple.
- **Implementation approaches this allows (not decided here):** either (a) a unique constraint on (`location_id`, `meal_type_id`, `forecast_date`) with updates overwriting `predicted_quantity`/`generated_at`, or (b) allowing multiple rows but always querying the most recent `generated_at` for a given period. **This specification recommends option (a) for simplicity**, but flags it as a proposed decision since neither the PRD nor SRS explicitly mandates it — see Section 29.

---

### 6.9 `planned_quantity`

**Purpose:** Stores the quantity Operations Staff intend to prepare for a period.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique record identifier. |
| `plan_date` | DATE | No | — | — | The date the plan is for. |
| `location_id` | UUID/BIGINT | No | — | Foreign Key → `locations.id` | Must reference a valid location. |
| `meal_type_id` | UUID/BIGINT | No | — | Foreign Key → `meal_types.id` | Must reference a valid meal type. |
| `quantity` | NUMERIC | No | — | Check (`>= 0`) | The Planned Quantity value. |
| `entered_by_user_id` | UUID/BIGINT | No | — | Foreign Key → `users.id` | Who entered/last edited the value. |
| `created_at` | TIMESTAMP | No | current timestamp | — | Audit field. |
| `updated_at` | TIMESTAMP | No | current timestamp | — | Audit field, updated on edit — supports edit operations (SRS-FR-015). |

**Uniqueness:** One Planned Quantity per (`location_id`, `meal_type_id`, `plan_date`) is recommended (a period is planned once, then edited in place) — see Section 17.

**Edit-window rule:** **Not implemented as a schema constraint.** The SRS explicitly leaves this rule unresolved (whether editing is restricted after the meal period passes, or after a comparison has been generated). No time-based CHECK constraint or trigger is added here; if such a rule is confirmed later, it can be enforced at the application layer initially, and optionally pushed into the schema afterward without restructuring this table.

---

### 6.10 `redistribution_recommendation`

**Purpose:** Stores the rule-based, advisory recommendation generated for a Surplus-classified period.

| Column | Data Type | Nullable | Default | Key/Constraint | Description |
|---|---|---|---|---|---|
| `id` | UUID or BIGINT (surrogate) | No | generated | Primary Key | Unique recommendation identifier. |
| `period_date` | DATE | No | — | — | The date of the period this recommendation applies to. |
| `location_id` | UUID/BIGINT | No | — | Foreign Key → `locations.id` | The primary location of the Surplus period. |
| `meal_type_id` | UUID/BIGINT | No | — | Foreign Key → `meal_types.id` | The meal type of the Surplus period. |
| `estimated_surplus_quantity` | NUMERIC | No | — | Check (`>= 0`) | Planned Quantity − Forecasted Demand for this period (the positive surplus amount). |
| `recommendation_text` | TEXT | No | — | — | Human-readable, rule-based advisory text. |
| `secondary_location_id` | UUID/BIGINT | Yes | — | Foreign Key → `locations.id` | Optional configured secondary/destination location referenced by the recommendation text, if applicable — reuses the existing `locations` table rather than introducing a new concept. |
| `is_advisory` | BOOLEAN | No | `true` | Check (must be `true` for MVP) | Explicitly marks the recommendation as advisory/non-executing, matching SRS-FR-027; kept as an explicit column (rather than assumed) so the data itself is self-documenting. |
| `generated_at` | TIMESTAMP | No | current timestamp | — | When the recommendation was generated. |

**No columns or tables are created for:** routing, donor/recipient matching, logistics optimization, or external-partner references — consistent with TRD Section 17 and Foundation v1.1 exclusions.

---

## 7. User and Role Data Model

- **Login support:** `users.username` + `users.password_hash` support SRS-FR-001; a failed lookup or hash mismatch results in a generic authentication failure at the application layer (no database-level distinction between "user not found" and "wrong password" is exposed).
- **Role-based access:** `users.role_id` → `roles.id` provides the single source of truth for a user's role, consumed by the backend's authorization layer (TRD Section 15).
- **User creation/updates:** Administrator-initiated changes to `users` rows (SRS-FR-004); `updated_at` reflects the most recent change.
- **User deactivation:** Represented via `users.is_active = false` (soft deactivation) rather than deletion — see Section 18 for full reasoning. A deactivated user cannot authenticate (enforced at the application layer using this flag).
- **Role assignment:** Exactly one `role_id` per user — a strict one-to-one relationship, not many-to-many, per the SRS's explicit statement.

**Explicitly not designed:** multi-factor authentication tables, social-login provider references, or email-verification-token tables — none are required by the source documents.

---

## 8. Location and Meal-Type Data Model

### Location
Supports create/view/update/delete (SRS-FR-005) via standard CRUD on the `locations` table; referenced by `historical_consumption`, `forecasted_demand`, `planned_quantity`, and `redistribution_recommendation` (both as primary and optional secondary location), enabling reporting/filtering by location across all of those tables.

### Meal Type
Supports create/view/update/delete (SRS-FR-006) via standard CRUD on the `meal_types` table; configurability is preserved (no hardcoded meal-type values anywhere in the schema); referenced by the same set of tables as Location.

### Deletion-safety — explicitly undecided, options presented

The SRS/PRD/TRD all leave this unresolved. **This specification does not silently choose cascade, hard, or soft delete.** Options:

| Option | Effect | Trade-off |
|---|---|---|
| Hard delete | Row physically removed from `locations`/`meal_types` | Simple, but breaks referential integrity for any historical/forecast/planned/recommendation row still referencing it — **not recommended**, as it would corrupt historical data. |
| Restricted delete (block if referenced) | Delete is rejected if any foreign-key reference exists | Preserves integrity perfectly, but may frustrate an Administrator who wants to "retire" a location that has historical data (which, realistically, almost every real location will have). |
| Soft delete / archive (recommended) | Row remains in the table; `is_active` flag set to `false`; row is excluded from selection lists for new entries but remains valid for historical references | Preserves full historical integrity (dates back to real past data), still allows "retiring" a location/meal type from active use, and requires no cascading logic. |

**Proposed database decision (requires confirmation): soft delete/archive via the `is_active` flag already included on both `locations` and `meal_types` (Sections 6.3–6.4).** This is recommended specifically because it preserves historical integrity — a stated design principle — without requiring a cascade strategy. This is flagged in Section 29 as needing confirmation before being treated as final.

---

## 9. Historical Consumed Quantity Model

Covered in full in Section 6.5. Summary of validation support:
- **Non-negative quantity:** `actual_consumed_quantity >= 0` check constraint.
- **Valid date:** `record_date` is a native DATE type, which PostgreSQL itself rejects if not a valid calendar date.
- **Valid location/meal type:** Foreign keys to `locations`/`meal_types` ensure only existing, valid references are stored.
- **Day of week:** Derived at query time from `record_date`, not persisted (Section 6.5 rationale).

No unapproved business fields (e.g., no cost, no supplier, no nutritional data) are added — only the five approved data points: date, day of week (derived), meal type, location, Actual Consumed Quantity.

---

## 10. Forecasted Demand Model

Covered in full in Section 6.8. Summary:
- **Fields:** `forecast_date`, `location_id`, `meal_type_id`, `predicted_quantity`, `generated_at`, optional `model_version`.
- **No complex model registry** — `model_version` is a single optional text field for traceability only, not a linked table of model metadata, training runs, or hyperparameters.
- **Versioning strategy (proposed, not confirmed):** one active forecast per (location, meal type, date), with regeneration overwriting the prior value — see Section 6.8 for full reasoning and the flag in Section 29.

---

## 11. Planned Quantity Model

Covered in full in Section 6.9. Summary:
- **Fields:** `plan_date`, `location_id`, `meal_type_id`, `quantity`, `entered_by_user_id`, `created_at`, `updated_at`.
- **Non-negative value:** `quantity >= 0` check constraint.
- **User reference:** `entered_by_user_id` foreign key to `users`.
- **Edit support:** `updated_at` tracks edits; the table supports in-place updates (no separate "edit history" table is created, as none is required by the SRS).
- **Edit-window rule:** Explicitly **not** encoded as a schema constraint — left as an application-layer concern until the business rule is confirmed (Section 29).

---

## 12. Variance and Comparison Model

**Options considered:**

| Option | Description | Assessment |
|---|---|---|
| A. Persisted as a table | A `variance` table storing computed Potential Surplus/Shortage/percentage per period | Introduces a table that must be kept in sync every time either `forecasted_demand` or `planned_quantity` changes — a source of potential staleness/inconsistency for a value that is trivial to compute. |
| B. Computed dynamically | No table; variance is calculated at query time from `forecasted_demand.predicted_quantity` and `planned_quantity.quantity` for the matching period | Always correct by construction (no sync risk); negligible computational cost at MVP scale (simple arithmetic over a small dataset). |
| C. Partially persisted/cached | Store variance only when a classification/recommendation is generated (a snapshot), not as a continuously maintained table | Reasonable middle ground, effectively what Section 13 recommends for classification, but a *separate* full variance table on top of that would be redundant. |

**Recommendation: Option B — compute Variance dynamically at query time.** No `variance` table is created. Potential Surplus (`Planned Quantity − Forecasted Demand`) and Potential Shortage (`Forecasted Demand − Planned Quantity`), along with the variance percentage where meaningful, are calculated by the backend's `comparison` module (TRD Section 9) directly from `forecasted_demand` and `planned_quantity` rows for the matching (location, meal type, date). This avoids duplicating source values and matches the "simplest design that preserves correctness" guidance — at this data scale, dynamic computation carries no meaningful performance cost, and it entirely eliminates a class of sync bugs.

**Zero-forecast edge case:** As noted in the SRS, the exact behavior of variance percentage when `predicted_quantity = 0` is unresolved. Because variance is computed dynamically (not persisted), this remains purely an application-layer computation concern and does not affect the schema (see Section 29).

---

## 13. Classification Model

**Options considered:**

| Option | Description | Assessment |
|---|---|---|
| Fully dynamic (no persistence at all) | Classification recalculated on every dashboard/report view from live variance | Simplest, but recommendation generation (Section 14) needs a stable reference to "this period was Surplus" at the moment the recommendation was created — recalculating from scratch every time risks a mismatch if the threshold configuration changes later. |
| Fully persisted, independently maintained | A `classification` table updated by triggers/jobs whenever inputs change | More moving parts than needed at MVP scale; risks becoming a second, potentially inconsistent source of truth for what is fundamentally a derived value. |
| **Persisted only as a snapshot at recommendation-generation time (recommended)** | No standalone `classification` table; the classification (Surplus/Shortage/Balanced) is computed on-demand for dashboard/report display (using the same dynamic Variance computation, Section 12, plus the configured threshold), and is **only persisted implicitly** via the existence of a `redistribution_recommendation` row (which only exists for periods that were Surplus at generation time) | Keeps the schema minimal: no extra table for something that is otherwise fully derivable, while still preserving a durable record of "this period was classified Surplus and a recommendation was generated" through `redistribution_recommendation`. Shortage and Balanced statuses, which do not produce a recommendation, remain purely dynamic/display-time values, which is acceptable since nothing else in the approved requirements needs them persisted. |

**Recommendation:** No standalone `classification` table. Classification is computed dynamically by the backend's `classification` module (TRD Section 9) from the dynamically-computed Variance (Section 12) and a configurable threshold value. The only durable trace of a Surplus classification is the corresponding `redistribution_recommendation` row.

**Threshold storage:** The numeric threshold value itself is **not defined here** (unresolved per SRS/PRD/TRD). This specification recommends storing it as a simple, single configurable parameter — not a complex policy-management table. A minimal option is a small `system_configuration` key-value style table (or an application-level configuration value, outside the database entirely). **This specification does not create a dedicated configuration table**, since a single scalar value does not justify a new table; it is noted here as a design option for the implementation stage, with the final storage location (database configuration row vs. application configuration) left open (Section 29).

---

## 14. Redistribution Recommendation Model

Covered in full in Section 6.10. Summary:
- **Fields:** `estimated_surplus_quantity`, `recommendation_text`, optional `secondary_location_id` (reusing the `locations` table — no new "destination" concept), `is_advisory` (constrained to `true`), `generated_at`.
- **Association with the surplus period:** `period_date` + `location_id` + `meal_type_id` ties the recommendation to the specific Surplus-classified period.
- **No structures for:** routing, donor/recipient matching, logistics, or external partners — consistent with the TRD's explicit exclusion (Section 17).

---

## 15. Import Job / Import Result Model

Covered in full in Sections 6.6–6.7. Design summary:

```text
import_job (one row per upload event)
   ↓ summary fields: total_records, valid_records, invalid_records, status
   ↓
import_record_error (one row per invalid record within that job)
   ↓ failure_reason, row_reference, optional raw_data_snapshot
```

- **Preserves:** who uploaded (`uploaded_by_user_id`), when (`uploaded_at`), total/valid/invalid counts, and per-record failure reasons — everything SRS-FR-010 requires.
- **Not over-normalized:** a single `import_record_error` table (not one table per validation-rule type) keeps the model simple while still fully traceable.
- **Duplicate-record policy:** Explicitly **not** implemented here. The model is designed so that whichever policy is eventually chosen (reject, merge, or overwrite) can be represented: a "duplicate" detection, if added, would simply produce another `import_record_error` row (for reject), an update to an existing `historical_consumption` row (for merge/overwrite), or a new distinct outcome type — none of which requires restructuring `import_job` or `import_record_error`. This is flagged again in Section 29.

---

## 16. Audit and Metadata Fields

| Table | `created_at` | `updated_at` | `created_by` / `updated_by` | Reasoning |
|---|---|---|---|---|
| `users` | ✓ | ✓ | — | Standard audit timestamps; a self-referential "who created this user" is not required by the source documents and is omitted to avoid unjustified complexity. |
| `locations` | ✓ | ✓ | — | Same reasoning; Administrator-managed but no requirement to track which Administrator created/edited a given location. |
| `meal_types` | ✓ | ✓ | — | Same reasoning as `locations`. |
| `planned_quantity` | ✓ | ✓ | `entered_by_user_id` (effectively `created_by`; also implicitly the last editor since edits are in-place) | Explicitly required — the SRS ties Planned Quantity to the entering user. |
| `import_job` | `uploaded_at` (serves this role) | — | `uploaded_by_user_id` | Required — SRS-FR-010 explicitly asks who uploaded and when. |
| `forecasted_demand` | `generated_at` (serves this role) | — | — | System-generated, not user-attributed; no "created_by" needed since forecasts are not manually entered by a specific user. |
| `redistribution_recommendation` | `generated_at` (serves this role) | — | — | Same reasoning — system-generated, not user-authored. |
| `historical_consumption` | `created_at` | — | `import_job_id` (traces provenance) | An `updated_by`/`updated_at` is not included, since historical records are not expected to be edited in place post-import in the approved MVP scope; provenance is via the import job link instead. |

Audit fields are **not** added blindly to every table — `roles` and `import_record_error`, for example, do not need them, since they are either a fixed reference set or inherently tied to their parent `import_job`'s timestamp.

---

## 17. Keys and Constraints

### Primary keys
**Recommendation: surrogate keys (UUID or auto-incrementing BIGINT) for every table**, rather than natural/composite keys. Reasoning: business identifiers (e.g., a location name) can change over time, and using a stable surrogate key avoids cascading updates through foreign keys when a name is edited. UUID vs. BIGINT is an implementation-stage choice; either satisfies this specification (UUIDs may be preferable if the system anticipates any need to generate IDs client-side or merge datasets later, but this is not a strong requirement here).

### Foreign keys
All relationships in Section 4.3 are enforced via foreign keys:
- `users.role_id` → `roles.id`
- `historical_consumption.location_id` → `locations.id`
- `historical_consumption.meal_type_id` → `meal_types.id`
- `historical_consumption.import_job_id` → `import_job.id`
- `import_record_error.import_job_id` → `import_job.id`
- `forecasted_demand.location_id` → `locations.id`
- `forecasted_demand.meal_type_id` → `meal_types.id`
- `planned_quantity.location_id` → `locations.id`
- `planned_quantity.meal_type_id` → `meal_types.id`
- `planned_quantity.entered_by_user_id` → `users.id`
- `redistribution_recommendation.location_id` → `locations.id`
- `redistribution_recommendation.meal_type_id` → `meal_types.id`
- `redistribution_recommendation.secondary_location_id` → `locations.id` (nullable)
- `import_job.uploaded_by_user_id` → `users.id`

### Unique constraints

| Combination | Table | Recommended? | Reasoning |
|---|---|---|---|
| (`location_id`, `meal_type_id`, `record_date`) | `historical_consumption` | **Proposed, pending duplicate-policy confirmation** — recommended as a unique constraint *if* the eventual duplicate policy is "reject/prevent duplicates"; **not yet enforced as final**, since the SRS explicitly leaves duplicate handling open. | A unique constraint here would directly implement a "reject duplicates" policy; since that policy isn't confirmed, this specification flags it as the *likely* constraint rather than asserting it now (Section 29). |
| (`location_id`, `meal_type_id`, `plan_date`) | `planned_quantity` | **Recommended** | A period is planned once and then edited in place (Section 6.9) — supports SRS-FR-015 (edit) cleanly without ambiguity about which row is "the" Planned Quantity for a period. |
| (`location_id`, `meal_type_id`, `forecast_date`) | `forecasted_demand` | **Recommended, per the proposed "one active forecast" versioning decision (Section 6.8)** | Supports the recommended single-active-forecast-per-period model; flagged as a proposed decision, not a confirmed requirement. |
| `users.username` | `users` | **Recommended** | Prevents duplicate login identifiers; exact duplicate-handling *behavior* (e.g., friendly error message) is an application concern, but DB-level uniqueness is a reasonable baseline regardless. |
| `locations.name`, `meal_types.name` | `locations`, `meal_types` | **Recommended** | Prevents obviously duplicate reference data; simple and low-risk to enforce. |

### Check constraints
- `historical_consumption.actual_consumed_quantity >= 0`
- `planned_quantity.quantity >= 0`
- `forecasted_demand.predicted_quantity >= 0`
- `redistribution_recommendation.estimated_surplus_quantity >= 0`
- `import_job.total_records >= 0`, `valid_records >= 0`, `invalid_records >= 0`
- `roles.name` restricted to the three approved values
- `import_job.status` restricted to approved status values
- `redistribution_recommendation.is_advisory` restricted to `true` for MVP
- Non-empty name checks on `locations.name` and `meal_types.name`

---

## 18. Delete / Deactivation Strategy

### User
**Recommendation: soft deactivation via `users.is_active`, not hard deletion.** Historical auditability strongly matters here: `planned_quantity.entered_by_user_id` and `import_job.uploaded_by_user_id` both reference users, and hard-deleting a user would either orphan or force cascading deletion of legitimate historical business records (Planned Quantity entries, import jobs) — which is unacceptable given the requirement to preserve historical data integrity. A deactivated (`is_active = false`) user cannot authenticate but their historical references remain intact.

### Location / Meal Type
As detailed in Section 8: **recommended soft delete/archive via `is_active`**, explicitly flagged as a **proposed technical decision requiring confirmation**, since the SRS/PRD/TRD leave this genuinely open. Hard delete is explicitly not recommended (breaks referential integrity with historical/forecast/planned/recommendation data); a strictly "restricted delete" (block entirely) is presented as a valid, safer-but-less-flexible alternative if the soft-delete/archive approach is not acceptable for some reason not currently known.

---

## 19. Indexing Strategy

| Index | Table | Reasoning |
|---|---|---|
| (`record_date`, `location_id`, `meal_type_id`) | `historical_consumption` | Directly supports forecasting input queries and historical report filtering (SRS-FR-030–031) — the most common lookup pattern for this table. |
| (`forecast_date`, `location_id`, `meal_type_id`) | `forecasted_demand` | Directly supports forecast lookup/comparison (SRS-FR-012, FR-018) — the primary access pattern. |
| (`plan_date`, `location_id`, `meal_type_id`) | `planned_quantity` | Directly supports comparison lookup and dashboard filtering (SRS-FR-018, FR-029). |
| (`period_date`, `location_id`, `meal_type_id`) | `redistribution_recommendation` | Supports dashboard alert/recommendation lookup for a given period (SRS-FR-023, FR-025–026). |
| `users.role_id` | `users` | Supports authorization checks that filter/join by role; small table, but a lightweight index is still low-cost and useful. |
| `users.is_active` | `users` | Supports quickly excluding deactivated users during authentication checks. |
| `import_job.uploaded_at` | `import_job` | Supports Administrator viewing recent import history in order (SRS-FR-010). |
| `import_record_error.import_job_id` | `import_record_error` | Supports retrieving all errors for a given job efficiently (SRS-FR-010). |

The unique constraints listed in Section 17 (e.g., on `planned_quantity` and `forecasted_demand`) already provide an underlying index for their respective columns, so no separate duplicate index is added there beyond what the constraint itself creates. No further speculative indexes (e.g., on rarely-filtered columns) are proposed at this stage — MVP-scale data volume does not justify them.

---

## 20. Data Integrity and Transaction Boundaries

- **Historical import:** The creation of `historical_consumption` rows and the corresponding `import_job` summary counts (and any `import_record_error` rows) must be consistent as a single logical unit — i.e., the job's `valid_records`/`invalid_records` counts must always match the actual number of resulting `historical_consumption` rows and `import_record_error` rows tied to that job. This is a data-integrity *requirement*, not a code-level transaction implementation (which belongs to the TRD/implementation stage).
- **Planned Quantity update:** An update to `planned_quantity.quantity` must not leave the row in a partially updated state (e.g., `quantity` updated but `updated_at` not) — the update must be atomic at the row level.
- **Forecast storage:** A `forecasted_demand` row must never be stored without valid `location_id`/`meal_type_id` foreign key references — enforced by the foreign key constraints themselves (Section 17), not by application logic alone.
- **Classification/recommendation:** Since classification is computed dynamically (Section 13) and not separately persisted, there is no risk of a persisted classification contradicting its source data. The one persisted derived artifact, `redistribution_recommendation`, must be generated only from a classification that was actually Surplus at generation time — an application-layer responsibility, but the schema itself does not allow a `redistribution_recommendation` row to exist without valid `location_id`/`meal_type_id` references, which is enforced via foreign keys.

No specific code-level transaction (e.g., `BEGIN`/`COMMIT` semantics) is defined here — only the integrity outcomes required.

---

## 21. Data Validation Rules

| Data | Validation |
|---|---|
| Historical Consumed Quantity (`actual_consumed_quantity`) | Numeric, non-negative |
| Planned Quantity (`quantity`) | Numeric, non-negative |
| Forecasted Demand (`predicted_quantity`) | Numeric, non-negative |
| Estimated Surplus Quantity (`estimated_surplus_quantity`) | Numeric, non-negative |
| Date (`record_date`, `forecast_date`, `plan_date`, `period_date`) | Valid calendar date (native DATE type) |
| Location (`location_id` references) | Must reference a valid, existing `locations` row |
| Meal Type (`meal_type_id` references) | Must reference a valid, existing `meal_types` row |
| Role (`roles.name` / `users.role_id`) | Must be one of the three approved roles |
| Import Job Status (`import_job.status`) | Must be one of the approved status values |
| Username (`users.username`) | Unique, non-empty |
| Location/Meal Type Name | Unique, non-empty |
| Advisory flag (`redistribution_recommendation.is_advisory`) | Must be `true` for MVP |

All validations above are from the SRS/PRD; no additional, unapproved validation rules are introduced.

---

## 22. Data Lifecycle

- **Historical data:** Upload (creates `import_job`) → validate (produces `import_record_error` rows for invalid records) → store (produces `historical_consumption` rows for valid records, linked to the `import_job`).
- **Forecast:** Generate (backend `forecasting` module + ML module) → persist (`forecasted_demand` row created/updated per the recommended single-active-forecast model) → display/report (read by dashboard/report queries).
- **Planned Quantity:** Create (`planned_quantity` row inserted) → edit (row updated in place, `updated_at` refreshed) → compare (read dynamically alongside the matching `forecasted_demand` row).
- **Classification:** Derived dynamically at query/generation time from Variance (Section 12) — no independent lifecycle of its own; it exists only transiently during a dashboard/report query or at the moment a recommendation is generated.
- **Recommendation:** Generated only when a period is classified Surplus (Section 13) → stored as a `redistribution_recommendation` row → displayed on dashboard/reports → remains advisory only; no lifecycle state exists for "executed" or "actioned," since the system never executes redistribution.

No lifecycle is defined for Actual Prepared Quantity or forward-looking Actual Consumed Quantity, as these remain Optional/Future and are not built now (Section 23).

---

## 23. Historical Data and Future Extensibility

The current model accommodates the following future additions **without redesigning core tables**:

- **Actual Prepared Quantity:** Could be added later as a new table (e.g., `actual_prepared_quantity`) following the same shape as `planned_quantity` (date/location/meal-type/quantity/entered-by), or as additional nullable columns if tightly coupled to `planned_quantity` — either approach is additive, not disruptive to the existing schema.
- **Forward-looking Actual Consumed Quantity:** Could reuse the existing `historical_consumption` table's shape (or a structurally identical new table) for post-hoc consumed-quantity capture, since the underlying fields (date, location, meal type, quantity) are identical in structure to what's already modeled.
- **Forecast Accuracy Tracking:** Once forward-looking Actual Consumed Quantity exists, accuracy tracking could be computed dynamically (comparing `forecasted_demand.predicted_quantity` to the new actual-consumed data) using the same "compute dynamically" pattern already established for Variance (Section 12) — no new persisted "accuracy" table would be strictly required.

**None of these tables/columns are created now** — this section only confirms that the current design does not foreclose them. This satisfies the future-extensibility principle without building unapproved functionality.

---

## 24. Database Security

- **Application database user:** The backend connects using a dedicated database user/role, not a database administrative superuser.
- **Least privilege:** The application's database user is granted only the privileges it needs (read/write on the application's own tables) — no privileges on PostgreSQL system catalogs or other databases.
- **Credentials from environment configuration:** Database connection credentials are supplied via environment configuration (TRD Section 21), never hardcoded.
- **No secrets in source control:** Consistent with the TRD's configuration strategy.
- **Controlled migrations:** Schema changes are applied through a tracked migration process (Section 25), not ad hoc manual changes against the demo/production database.
- **Restricted administrative database access:** Direct administrative access to the PostgreSQL instance is limited to whoever manages the deployment (not exposed to the application or to end users) — consistent with the frontend/backend never accessing the database directly (Section 3).

No complex database security infrastructure (e.g., row-level security policies, database-level encryption-at-rest configuration, dedicated secrets-management services) is introduced, as none is justified at this MVP scale.

---

## 25. Migration Strategy

- **Schema changes tracked:** All schema changes (new tables, new columns, constraint changes) are expected to be captured as a sequence of versioned migration steps, not applied as untracked manual changes.
- **Repeatable across environments:** The same migration sequence is applied consistently across Development, Test, and Production/Demo environments (TRD Section 21), ensuring schema consistency.
- **Development/test/demo consistency:** Migrations are the single source of truth for the schema's current state in every environment — no environment should have a schema that migrations don't account for.
- **Rollback/recovery concept:** Each migration step should conceptually be reversible (or, at minimum, safely forward-only with a clear recovery path) so that a problematic schema change can be identified and addressed without ambiguity about the database's state.

No specific migration tool/library is selected here (an implementation-stage decision, per TRD Section 23), and no migration files or SQL are provided.

---

## 26. Seed / Demo Data Strategy

- **Purpose of seed data:** To support local development and mentor demonstrations without requiring real SensorSpine operational data (which has not been confirmed as available — Foundation v1.1/PRD/SRS/TRD all note this as an open item).
- **Reference data:** The three `roles` rows (Administrator, Manager, Operations Staff) are seeded as fixed reference data — these are not "sample" data but genuinely part of the approved system configuration.
- **Demo locations and meal types:** A small number of illustrative locations (e.g., a couple of sample cafeteria names) and meal types (e.g., Breakfast/Lunch/Dinner) are seeded as clearly-labeled **synthetic demo data**, not real SensorSpine data.
- **Sample historical records:** A synthetic dataset of `historical_consumption` records (plausible but fabricated date/location/meal-type/quantity combinations) is seeded to allow the forecasting component to be demonstrated meaningfully.

**All seed data used for development/demo purposes must be clearly labeled as synthetic/demo data** — this specification does not fabricate or imply any real SensorSpine production data, consistent with the Foundation's explicit instruction.

---

## 27. Backup and Recovery — MVP Level

- **Minimum practical approach:** Regular, periodic backups (e.g., a daily database dump) of the single PostgreSQL database, retained for a reasonable short window (e.g., a handful of recent backups), sufficient to recover the demo/application data in case of accidental data loss during development or demonstration.
- **Not designed:** Multi-region replication, high-availability clustering, or enterprise disaster-recovery processes — none are justified at internship/demo scale, and building them would violate the project's simplicity principle.

This is a lightweight, "protect the demo" strategy, not a production-grade recovery plan.

---

## 28. Database Performance Considerations

- **Expected scale:** A single institution (or a small number of locations, per the Foundation's working assumption), with a modest volume of historical records, forecasts, and Planned Quantity entries — well within PostgreSQL's comfortable range without any special tuning.
- **Likely query patterns:** Lookups and filters by date, location, and meal type (individually and in combination) dominate — directly addressed by the composite indexes proposed in Section 19.
- **Historical reports:** Date-range + location + meal-type filtering (SRS-FR-031) is supported by the same composite indexes on `historical_consumption` and related tables.
- **Forecast lookup:** Supported by the composite index on `forecasted_demand`.

No enterprise-scale optimizations (partitioning, read replicas, caching layers, materialized views) are proposed — not justified at this scale, and would add unnecessary complexity.

---

## 29. Deferred Database Decisions

The following remain explicitly open and are **not** resolved in this specification. Where useful, a recommended option is noted separately from the unresolved status.

1. **Duplicate historical record handling** — Unresolved. *Recommended option (if/when decided): reject via a unique constraint on (`location_id`, `meal_type_id`, `record_date`), reporting duplicates as `import_record_error` rows* — but not enforced as final here.
2. **Location deletion strategy** — Unresolved. *Recommended option: soft delete/archive via `is_active`* (Section 18).
3. **Meal type deletion strategy** — Unresolved. *Recommended option: soft delete/archive via `is_active`*, same reasoning as Location.
4. **User duplicate identifier behavior** — Partially addressed (DB-level `UNIQUE` on `username` is recommended), but the application-level *user experience* of a duplicate attempt (e.g., exact error message, whether usernames are case-insensitive) remains open.
5. **Planned Quantity edit-window rule** — Unresolved; not encoded as a schema constraint (Section 11).
6. **Numeric surplus/shortage threshold storage strategy** — Unresolved whether it lives in the database (e.g., a minimal configuration table/row) or purely in application configuration; the numeric value itself is entirely undefined (Section 13).
7. **Forecast versioning strategy** — *Recommended option: single active forecast per period*, but not confirmed as final (Section 6.8/6.10 discussion).
8. **Final deployment/hosting implications for database hosting** — Unresolved (TRD Section 22 leaves the final hosting choice open); this may affect connection configuration but does not affect the logical schema in this document.

None of these are guessed at or silently resolved elsewhere in this document.

---

## 30. Database-to-Requirement Traceability

| SRS Requirement | Database Table(s) | Database Responsibility |
|---|---|---|
| SRS-FR-001–003 | `users`, `roles` | Store credentials (hashed), role assignment, active status for authentication and role-based authorization. |
| SRS-FR-004 | `users`, `roles` | Support create/view/update/deactivate operations and role assignment. |
| SRS-FR-005 | `locations` | Support create/view/update/(soft)delete; referenced across the schema. |
| SRS-FR-006 | `meal_types` | Support create/view/update/(soft)delete; referenced across the schema. |
| SRS-FR-007 | `import_job` | Record each upload event. |
| SRS-FR-008 | `import_job`, `import_record_error` | Store validation outcome and per-record failure reasons. |
| SRS-FR-009 | `historical_consumption` | Persist valid historical records. |
| SRS-FR-010 | `import_job`, `import_record_error` | Provide queryable import status (totals, valid/invalid counts, reasons). |
| SRS-FR-011–012 | `forecasted_demand`, `historical_consumption` | Store generated forecasts; provide input data for forecast generation. |
| SRS-FR-013 | `historical_consumption` (queried for sufficiency), `forecasted_demand` (absence of a row indicates unavailability) | Support determining whether sufficient input data exists (application-layer logic over this data). |
| SRS-FR-014–017 | `planned_quantity` | Store, validate, and support editing of Planned Quantity. |
| SRS-FR-018–020 | `forecasted_demand`, `planned_quantity` (Variance computed dynamically, Section 12) | Provide the two source values for dynamic variance calculation and display. |
| SRS-FR-021–023 | `forecasted_demand`, `planned_quantity` (Classification computed dynamically, Section 13) | Provide the source data for dynamic threshold-based classification. |
| SRS-FR-024–027 | `redistribution_recommendation` | Persist rule-based, advisory recommendations for Surplus periods. |
| SRS-FR-028–029 | `forecasted_demand`, `planned_quantity`, `redistribution_recommendation` (aggregated dynamically) | Provide all source data the dashboard module aggregates and filters. |
| SRS-FR-030–031 | `historical_consumption`, `forecasted_demand`, `planned_quantity` | Provide the historical, filterable data underlying reports. |

Every persisted data requirement has a clear database owner; no SRS requirement (FR-001–031) lacks a corresponding table/relationship.

---

## 31. Final Database Blueprint

### Database
PostgreSQL — single database, relational model, accessed exclusively through the FastAPI backend.

### Core Tables
`users`, `locations`, `meal_types`, `historical_consumption`, `forecasted_demand`, `planned_quantity`, `redistribution_recommendation`.

### Reference Tables
`roles`.

### Derived/Persisted Tables (Operational/Audit)
`import_job`, `import_record_error` (operational/audit); Variance and Classification are **not** separate tables — computed dynamically, with Classification's only durable trace being the existence of a `redistribution_recommendation` row for Surplus periods.

### Key Relationships
Role → User (1:many, one role per user); Location/Meal Type → Historical Consumption, Forecasted Demand, Planned Quantity, Redistribution Recommendation (1:many each); User → Planned Quantity (entered-by) and Import Job (uploaded-by); Import Job → Import Record Error and (via provenance) Historical Consumption.

### Integrity Strategy
Surrogate primary keys throughout; foreign keys enforcing every relationship in Section 4.3; non-negative check constraints on all quantity fields; role/status value constraints; recommended (but flagged as proposed) uniqueness on (location, meal type, date) for `historical_consumption`, `planned_quantity`, and `forecasted_demand`; soft deactivation/archival (`is_active`) recommended for `users`, `locations`, and `meal_types` to preserve historical integrity, pending confirmation for Location/Meal Type.

### Indexing
Composite (date, location, meal type) indexes on `historical_consumption`, `forecasted_demand`, `planned_quantity`, and `redistribution_recommendation`, directly supporting the dominant filter/lookup patterns; supporting indexes on `users.role_id`/`is_active` and `import_job`/`import_record_error` for authentication and import-status queries.

### Migration
Versioned, tracked migrations applied consistently across Development/Test/Production-Demo environments; no specific tool selected at this stage.

### Seed Data
Fixed `roles` reference rows plus clearly-labeled synthetic demo data (sample locations, meal types, and historical consumption records) — no real SensorSpine data is fabricated or implied.

---

## 32. Database Review Checklist

**Requirements**
- ✅ Every database-relevant SRS requirement has a table/relationship supporting it (Section 30).
- ✅ All 31 SRS requirements remain traceable.
- ✅ No future feature (Actual Prepared Quantity, forward-looking Actual Consumed Quantity, accuracy tracking) became mandatory — confirmed absent from the schema (Section 23).

**Data model**
- ✅ No contradictory entities — Forecasted Demand, Planned Quantity, and Historical Consumed (Actual Consumed) Quantity remain distinct tables with distinct column names throughout.
- ✅ Actual Prepared Quantity remains future/optional — no table/column created.
- ✅ Forward-looking Actual Consumed Quantity remains future/optional — no table/column created.

**Integrity**
- ✅ Foreign keys defined for every cross-table relationship (Section 17).
- ✅ Quantity fields constrained to non-negative values (Sections 6, 17, 21).
- ✅ Roles/statuses constrained to approved values (Sections 6.1, 6.6, 17).
- ✅ Historical data remains referentially safe — no hard-delete path is recommended for `locations`/`meal_types` (Section 18), avoiding orphaned historical references.

**Simplicity**
- ✅ No unnecessary tables — Variance and Classification deliberately not persisted as standalone tables (Sections 12–13).
- ✅ No unnecessary database technologies — single PostgreSQL database only (Section 3).
- ✅ No database duplication.
- ✅ No enterprise-scale features (no partitioning, replication, sharding, or NoSQL — Sections 24, 27, 28).

**Open decisions**
- ✅ Unresolved policies (duplicate handling, deletion strategy, edit-window rule, threshold storage, forecast versioning, deployment/hosting implications) remain clearly labeled throughout and consolidated in Section 29.
- ✅ Proposed recommendations (soft-delete approach, single-active-forecast model, dynamic variance/classification computation, surrogate keys) are clearly distinguished from confirmed requirements.

---

## DATABASE REVIEW SUMMARY

- **Final table inventory:** 10 tables — `roles` (reference); `users`, `locations`, `meal_types`, `historical_consumption`, `forecasted_demand`, `planned_quantity`, `redistribution_recommendation` (core); `import_job`, `import_record_error` (operational/audit). No standalone `variance` or `classification` table (both computed dynamically — Sections 12–13).
- **Major relationships:** Role↔User (1:1 per user); Location/Meal Type as widely-referenced lookup entities across Historical Consumption, Forecasted Demand, Planned Quantity, and Redistribution Recommendation; User as the entering/uploading party for Planned Quantity and Import Job; Import Job as the parent of Import Record Error and the provenance source for Historical Consumption.
- **Key constraints:** Non-negative checks on every quantity field; role/status value constraints; foreign keys on every cross-table relationship; recommended (proposed) uniqueness on (location, meal type, date) for the three period-based core tables; recommended soft-deactivation (`is_active`) on `users`, `locations`, and `meal_types`.
- **Important indexes:** Composite (date, location, meal type) indexes on `historical_consumption`, `forecasted_demand`, `planned_quantity`, and `redistribution_recommendation`; supporting indexes on `users` (role, active status) and import tables (timestamp, job reference).
- **Proposed database decisions (flagged, not confirmed):** soft delete/archive for Location and Meal Type; single-active-forecast-per-period model with a corresponding unique constraint; dynamic (non-persisted) computation of Variance and Classification; surrogate (not natural) primary keys; a reference table for `roles` rather than an inline enum.
- **Deferred database decisions:** duplicate historical-record handling policy; final location/meal-type deletion strategy confirmation; user duplicate-identifier UX behavior; Planned Quantity edit-window rule; numeric surplus/shortage threshold value and its storage location; final confirmation of the forecast-versioning approach; deployment/hosting implications for database hosting (Section 29 — 8 items, none guessed at).
- **Main data-integrity risks:** Historical/forecast/planned data could be orphaned if a hard-delete strategy were later chosen for Location/Meal Type instead of the recommended soft-delete approach; duplicate historical records could silently accumulate until the duplicate policy is confirmed and enforced; the numeric surplus/shortage threshold being undefined means classification cannot be *exercised* end-to-end until a value (even a placeholder) is supplied at the application/configuration layer.
- **Contradictions discovered:** None. Foundation v1.1, PRD v1.0, SRS v1.0, and TRD v1.0 remained internally consistent and translated directly into this database design without requiring reconciliation.
- **Assumptions introduced:** Only standard, clearly-labeled database-engineering defaults (surrogate keys, standard audit-timestamp conventions, a small reference table for roles) — no product-level assumptions were introduced beyond what the four source documents already established as Working Assumptions.
- **Readiness:** This Database Specification is ready to serve as the input to the API Specification stage, provided the Deferred Database Decisions (Section 29) — particularly the duplicate-record policy, deletion strategy, and threshold storage approach — are tracked and resolved as implementation proceeds, rather than silently decided during API or application-layer development.

**Next planned stage: API Specification**

*(The API Specification has not been created. No SQL CREATE TABLE statements, ORM code, migration scripts, or application code have been produced at this stage.)*
