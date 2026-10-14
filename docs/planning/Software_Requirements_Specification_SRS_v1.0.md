# Software Requirements Specification (SRS) v1.0
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality

---

## 1. Document Control

- **Document title:** Software Requirements Specification (SRS)
- **Project name:** Food-Service Demand Forecasting and Surplus Redistribution System (working title: FoodFlow — placeholder, to be confirmed)
- **Version:** 1.0
- **Status:** Draft, pending review
- **Purpose:** Define precisely how the software must behave from a system-requirements perspective, at an implementation-agnostic level, building on the approved Foundation and PRD.
- **Source documents:** Project Foundation & Scope Definition v1.1 (approved); Product Requirements Document (PRD) v1.0 (approved)
- **Scope:** MVP system requirements only. Excludes TRD, database schema, ER diagrams, API specification, ML model selection, UI implementation, and code — these belong to later stages.

*(No author names, reviewer names, dates, or approvals are stated, as none have been provided.)*

---

## 2. Introduction

### 2.1 Purpose
This SRS exists to translate the approved PRD's product-level requirements into system-level requirements precise enough for developers and testers to implement and verify the software without needing to guess intended behavior, while still not prescribing any specific technology, architecture, or algorithm.

### 2.2 Product Scope
The approved MVP is a role-based web application that ingests historical Actual Consumed Quantity data, generates Forecasted Demand for future date/meal-type/location combinations, allows Operations Staff to enter Planned Quantity, compares the two, classifies each period as Surplus/Shortage/Balanced, generates a rule-based advisory redistribution recommendation for Surplus periods, and presents all of this through a dashboard and basic historical reports, with authentication and role-based access for Administrator, Manager, and Operations Staff.

### 2.3 Intended Audience
- Product/Project Mentor
- Software Developers (for the later TRD/implementation stage)
- QA/Testers (for the later test-plan stage)
- Technical Reviewers

### 2.4 References
- Project Foundation & Scope Definition v1.1
- Product Requirements Document (PRD) v1.0

No other source documents are referenced.

---

## 3. System Overview

The system supports a data-driven planning workflow for food-service operations, structured as follows:

```
Historical Actual Consumed Quantity Data
        ↓
Forecasted Demand Generation
        ↓
Planned Quantity Entry
        ↓
Forecasted Demand vs Planned Quantity Comparison
        ↓
Surplus / Shortage / Balanced Classification
        ↓
Rule-Based Redistribution Recommendation (if Surplus)
        ↓
Dashboard / Historical Reports
```

**Major functional areas:**
1. Authentication & Authorization
2. User Management (Administrator)
3. Location Management (Administrator)
4. Meal-Type Management (Administrator)
5. Historical Data Management (Administrator)
6. Forecasting (system-generated, Manager-viewed)
7. Planned Quantity Management (Operations Staff)
8. Forecast Comparison (system)
9. Surplus/Shortage Classification (system)
10. Redistribution Recommendation (system, Manager-reviewed)
11. Dashboard (Manager, Administrator)
12. Historical Reporting (Manager, Administrator)

No technical architecture diagram, technology stack, or deployment topology is defined here — those belong to the TRD.

---

## 4. Actors and System Roles

### 4.1 Administrator
- **Responsibilities:** User management, location management, meal-type management, historical data upload/management, system configuration oversight.
- **Allowed interactions:** Full CRUD on users, locations, and meal types; upload and review historical data; view dashboard and reports (per Section 6 permission notes).
- **Restrictions:** Does not enter Planned Quantity in the core operational workflow (unless later confirmed otherwise — see Section 6).
- **Major use cases:** Load historical data; configure locations/meal types; manage user accounts.

### 4.2 Manager
- **Responsibilities:** Review Forecasted Demand, review Planned Quantity, review surplus/shortage status, review redistribution recommendations, review historical reports.
- **Allowed interactions:** View forecasts, view Planned Quantity, view dashboard, view/filter historical reports, view recommendations.
- **Restrictions:** Does not manage users, locations, meal types, or historical data uploads.
- **Major use cases:** Review dashboard for upcoming periods; review a flagged Surplus period and its recommendation; review historical trends via reports.

### 4.3 Operations Staff
- **Responsibilities:** Enter Planned Quantity; view relevant operational information; optionally record actual quantities in future functionality (not in MVP).
- **Allowed interactions:** Create/edit Planned Quantity for date/meal-type/location combinations; view information relevant to their role (exact scope of "relevant" per Section 6 — some cells unresolved).
- **Restrictions:** Does not manage users, locations, meal types, or historical data; does not generate forecasts manually.
- **Major use cases:** Enter Planned Quantity for an upcoming meal period; view whether a previously entered Planned Quantity was saved correctly.

No additional actors are introduced.

---

## 5. Functional Requirements

Every PRD requirement (FR-001–FR-031) has one or more corresponding SRS requirements below. Traceability is stated explicitly per requirement, and consolidated in Section 24.

### SRS-FR-001 — User Login *(traces to PRD FR-001)*
- **Purpose:** Authenticate a registered user and grant role-scoped access.
- **Actors:** Administrator, Manager, Operations Staff.
- **Preconditions:** A user account exists.
- **Trigger:** User submits credentials.
- **Main behavior:** System verifies credentials; on success, establishes an authenticated session scoped to the user's role.
- **Alternate behavior:** On invalid credentials, system denies access and returns a generic error that does not reveal whether the username or password was incorrect.
- **Validation rules:** Credentials must be non-empty; format validation is implementation-dependent (not defined here).
- **Failure conditions:** Invalid credentials; account not found; account deactivated (deactivation behavior — see SRS-FR-005).
- **Postconditions:** Authenticated session established (success) or no session established (failure).
- **Dependencies:** User account must exist (SRS-FR-004).
- **Priority:** Essential.

### SRS-FR-002 — User Logout *(traces to PRD FR-002)*
- **Purpose:** Terminate an authenticated session.
- **Actors:** Administrator, Manager, Operations Staff.
- **Preconditions:** User is authenticated.
- **Trigger:** User selects logout.
- **Main behavior:** System terminates the session; subsequent actions require re-authentication.
- **Alternate behavior:** None identified at SRS level.
- **Validation rules:** N/A.
- **Failure conditions:** N/A (logout is expected to always succeed for an active session).
- **Postconditions:** Session ended.
- **Dependencies:** SRS-FR-001.
- **Priority:** Essential.

### SRS-FR-003 — Role-Based Access Enforcement *(traces to PRD FR-003)*
- **Purpose:** Restrict actions and views according to the authenticated user's role.
- **Actors:** Administrator, Manager, Operations Staff.
- **Preconditions:** User is authenticated.
- **Trigger:** User attempts an action or requests a view.
- **Main behavior:** System checks the action/view against the user's role permissions (Section 6) and allows or denies accordingly.
- **Alternate behavior:** On denial, system informs the user the action/view is not permitted, without exposing details of restricted data.
- **Validation rules:** Permission set per Section 6; several cells remain unresolved (see Section 6 and Section 23).
- **Failure conditions:** Attempted access to a restricted action/view.
- **Postconditions:** Action performed (allowed) or blocked (denied).
- **Dependencies:** SRS-FR-001.
- **Priority:** Essential.

### SRS-FR-004 — Create/View/Update/Deactivate User *(traces to PRD FR-004)*
- **Purpose:** Allow the Administrator to manage user accounts and role assignment.
- **Actors:** Administrator.
- **Preconditions:** Administrator is authenticated.
- **Trigger:** Administrator initiates a user-management action.
- **Main behavior:** System creates, displays, updates, or deactivates a user account, with an assigned role (Administrator, Manager, or Operations Staff).
- **Alternate behavior:** N/A — password reset, email verification, MFA, and social login are not part of MVP (not stated in source documents).
- **Validation rules:** Required fields for a user account are not fully specified in the PRD; minimally a unique identifier/username and an assigned role are required. Additional field-level validation is an open decision.
- **Failure conditions:** Missing required fields; duplicate identifier (exact duplicate-handling behavior for users is not defined in source documents — open item).
- **Postconditions:** User account created/updated/deactivated with the specified role.
- **Dependencies:** SRS-FR-003 (only Administrator may perform this).
- **Priority:** Essential.

### SRS-FR-005 — Create/View/Update/Delete Location *(traces to PRD FR-005)*
- **Purpose:** Allow the Administrator to manage locations/cafeterias.
- **Actors:** Administrator (manage); Manager, Operations Staff (view, per Section 6).
- **Preconditions:** Administrator is authenticated (for management actions).
- **Trigger:** Administrator initiates a location-management action.
- **Main behavior:** System creates, displays, updates, or deletes a location record; created locations become selectable in forecasting, Planned Quantity entry, and reporting.
- **Alternate behavior:** Deletion of a location currently referenced by existing data (historical records, forecasts, Planned Quantity) — exact behavior (block, cascade, or archive) is **unresolved**, per PRD Section 8/9. It is carried forward here as an open decision, not invented.
- **Validation rules:** Location name/identifier required and presumably unique; exact rules not further specified.
- **Failure conditions:** Missing required fields; deletion attempted on a referenced location (behavior open — see above).
- **Postconditions:** Location available (create/update) or removed (delete, subject to the unresolved rule above).
- **Dependencies:** SRS-FR-003.
- **Priority:** Essential.

### SRS-FR-006 — Create/View/Update/Delete Meal Type *(traces to PRD FR-006)*
- **Purpose:** Allow the Administrator to manage meal types (e.g., Breakfast, Lunch, Dinner), kept configurable per Foundation v1.1.
- **Actors:** Administrator (manage); Manager, Operations Staff (view, per Section 6).
- **Preconditions:** Administrator is authenticated (for management actions).
- **Trigger:** Administrator initiates a meal-type-management action.
- **Main behavior:** System creates, displays, updates, or deletes a meal-type record; created meal types become selectable in forecasting, Planned Quantity entry, and reporting.
- **Alternate behavior:** Deletion-safety behavior for a referenced meal type — same unresolved status as SRS-FR-005.
- **Validation rules:** Meal-type name/identifier required and presumably unique.
- **Failure conditions:** Missing required fields; deletion attempted on a referenced meal type (behavior open).
- **Postconditions:** Meal type available (create/update) or removed (delete, subject to the unresolved rule above).
- **Dependencies:** SRS-FR-003.
- **Priority:** Essential.

### SRS-FR-007 — Upload Historical Data *(traces to PRD FR-007)*
- **Purpose:** Allow the Administrator to submit historical meal-demand data for use in forecasting.
- **Actors:** Administrator.
- **Preconditions:** Administrator is authenticated.
- **Trigger:** Administrator initiates an upload.
- **Main behavior:** System accepts a data submission containing, at minimum, date, day of week, meal type, location, and historical Actual Consumed Quantity, and passes it to validation (SRS-FR-008).
- **Alternate behavior:** N/A.
- **Validation rules:** Presence of the required business fields listed above (format-level rules defined in SRS-FR-008).
- **Failure conditions:** Upload cannot be initiated/accepted (e.g., empty submission) — exact failure surface is a technical-stage decision.
- **Postconditions:** Submission is queued/passed for validation.
- **Dependencies:** SRS-FR-003; existing/uploaded locations and meal types (SRS-FR-005, SRS-FR-006).
- **Priority:** Essential.

### SRS-FR-008 — Validate Historical Data *(traces to PRD FR-008)*
- **Purpose:** Ensure only structurally and logically valid historical records are accepted for storage.
- **Actors:** System (triggered by Administrator upload).
- **Preconditions:** An upload has been submitted (SRS-FR-007).
- **Trigger:** Completion of upload submission.
- **Main behavior:** System checks each record for: required fields present; valid date; valid (non-negative, numeric) Actual Consumed Quantity; valid meal type (matches a configured meal type, or is included for creation — open decision); valid location (matches a configured location, or is included for creation — open decision). Records are separated into valid and invalid sets.
- **Alternate behavior:** Malformed records (e.g., unreadable structure) are rejected outright and reported as invalid.
- **Validation rules:** As listed above. **Duplicate record handling (e.g., same date/meal type/location appearing more than once) is explicitly unresolved** — the PRD leaves this open; this SRS does not invent reject/merge/overwrite behavior.
- **Failure conditions:** Missing required fields; invalid date; negative or non-numeric quantity; unrecognized meal type/location (if not permitted to be created inline — open decision); potential duplicates (open decision).
- **Postconditions:** A validated set of records (valid/invalid, with reasons) is produced for SRS-FR-009 and SRS-FR-010.
- **Dependencies:** SRS-FR-007.
- **Priority:** Essential.

### SRS-FR-009 — Store Validated Historical Data *(traces to PRD FR-009)*
- **Purpose:** Persist valid historical records so they are available to the forecasting function.
- **Actors:** System.
- **Preconditions:** Validation (SRS-FR-008) has produced a valid-records set.
- **Trigger:** Validation completion.
- **Main behavior:** Valid records are stored and become available as input to Forecasted Demand generation (SRS-FR-011).
- **Alternate behavior:** Invalid records are not stored as historical data.
- **Validation rules:** Only records that passed SRS-FR-008 are stored.
- **Failure conditions:** Storage failure is a technical-stage concern, not defined here.
- **Postconditions:** Historical dataset updated with new valid records.
- **Dependencies:** SRS-FR-008.
- **Priority:** Essential.

### SRS-FR-010 — View Historical Data Import Status *(traces to PRD FR-010)*
- **Purpose:** Let the Administrator confirm the outcome of an upload.
- **Actors:** Administrator.
- **Preconditions:** An upload has completed validation (SRS-FR-008).
- **Trigger:** Administrator views import status/history.
- **Main behavior:** System displays a summary: total records processed, count valid, count invalid, and the reason(s) each invalid record failed.
- **Alternate behavior:** N/A.
- **Validation rules:** N/A (read-only reporting of prior validation outcome).
- **Failure conditions:** No import history exists yet (system indicates this rather than showing an error).
- **Postconditions:** Administrator has visibility into the import outcome.
- **Dependencies:** SRS-FR-007, SRS-FR-008.
- **Priority:** Essential.

### SRS-FR-011 — Generate/View Forecasted Demand *(traces to PRD FR-011)*
- **Purpose:** Produce a predicted meal-quantity value (Forecasted Demand) for a selected future date/meal-type/location.
- **Actors:** Manager (viewer); system (generator).
- **Preconditions:** Sufficient historical data exists for the selected location/meal type (see SRS-FR-013 for the insufficient case).
- **Trigger:** A forecast is requested for a date/meal-type/location, or generated on a defined cadence (exact mechanism is a TRD-stage decision, not defined here).
- **Main behavior:** System applies its forecasting function (algorithm not selected in this document) to the relevant historical data and returns a Forecasted Demand value.
- **Alternate behavior:** See SRS-FR-013 for insufficient data; forecast-generation failure is handled per Section 18.
- **Validation rules:** Selected date must be a valid future (or otherwise permitted) date; selected meal type/location must exist.
- **Failure conditions:** Insufficient historical data; forecast-generation failure (technical, not data-related).
- **Postconditions:** A Forecasted Demand value is available for the selected period.
- **Dependencies:** SRS-FR-009 (historical data must exist); SRS-FR-005, SRS-FR-006 (location/meal type must exist).
- **Priority:** Essential.
- **Note:** No specific forecasting algorithm, model architecture, training approach, or hyperparameter is selected in this SRS — this is explicitly deferred to the ML/TRD stage.

### SRS-FR-012 — Select Date/Meal Type/Location for Forecast *(traces to PRD FR-012)*
- **Purpose:** Let the Manager choose which period's forecast to view.
- **Actors:** Manager.
- **Preconditions:** Locations and meal types are configured (SRS-FR-005, SRS-FR-006).
- **Trigger:** Manager navigates to the forecast view and makes a selection.
- **Main behavior:** System presents available locations, meal types, and a date selector, and returns the Forecasted Demand for the chosen combination (if available).
- **Alternate behavior:** If no forecast exists for the combination, system indicates this (see SRS-FR-011/SRS-FR-013).
- **Validation rules:** Selection must reference existing, valid location/meal-type values.
- **Failure conditions:** Invalid or nonexistent combination selected.
- **Postconditions:** Requested Forecasted Demand displayed, or an appropriate message shown.
- **Dependencies:** SRS-FR-011.
- **Priority:** Essential.

### SRS-FR-013 — Handle Insufficient Historical Data for Forecasting *(traces to PRD FR-013)*
- **Purpose:** Prevent the system from presenting a misleading or fabricated Forecasted Demand when the underlying historical data is inadequate.
- **Actors:** System.
- **Preconditions:** A forecast has been requested (SRS-FR-011/SRS-FR-012) for a location/meal-type combination that does not meet the minimum data requirement.
- **Trigger:** Forecast request evaluated against data sufficiency.
- **Main behavior:** System returns a clear message indicating a reliable forecast is not currently available, instead of a numeric value.
- **Alternate behavior:** N/A.
- **Validation rules:** The exact minimum-data threshold that defines "sufficient" is **not defined at this stage** — carried forward as an open decision for the TRD/ML stage.
- **Failure conditions:** This requirement itself describes a failure-handling path for SRS-FR-011.
- **Postconditions:** User is clearly informed; no fabricated forecast is shown.
- **Dependencies:** SRS-FR-011.
- **Priority:** Essential.

### SRS-FR-014 — Enter Planned Quantity *(traces to PRD FR-014)*
- **Purpose:** Capture the quantity Operations Staff intend to prepare for a period.
- **Actors:** Operations Staff.
- **Preconditions:** User is authenticated with appropriate permission (see Section 6 — some cells unresolved); location and meal type exist.
- **Trigger:** User submits a Planned Quantity for a date/meal-type/location.
- **Main behavior:** System validates (SRS-FR-017) and stores the Planned Quantity against the specified period.
- **Alternate behavior:** Invalid input is rejected (see SRS-FR-017).
- **Validation rules:** See SRS-FR-017.
- **Failure conditions:** Invalid value; nonexistent location/meal-type reference.
- **Postconditions:** Planned Quantity stored for the period; confirmation returned to the user.
- **Dependencies:** SRS-FR-005, SRS-FR-006, SRS-FR-017.
- **Priority:** Essential.

### SRS-FR-015 — Edit Planned Quantity *(traces to PRD FR-015)*
- **Purpose:** Allow correction/update of a previously entered Planned Quantity.
- **Actors:** Operations Staff.
- **Preconditions:** A Planned Quantity record exists for the period.
- **Trigger:** User submits an updated Planned Quantity.
- **Main behavior:** System validates and updates the stored value.
- **Alternate behavior:** Invalid input rejected (see SRS-FR-017).
- **Validation rules:** Same as SRS-FR-017. **The edit-window rule — i.e., whether editing is permitted after the meal period has occurred or after a forecast comparison has been generated — is explicitly unresolved** and is not invented here; it is carried forward as an open decision (see Section 23).
- **Failure conditions:** Invalid value; edit attempted outside a permitted window (once such a window is defined).
- **Postconditions:** Planned Quantity updated (subject to the open edit-window decision); confirmation returned.
- **Dependencies:** SRS-FR-014, SRS-FR-017.
- **Priority:** Essential.

### SRS-FR-016 — View Planned Quantity *(traces to PRD FR-016)*
- **Purpose:** Let authorized users see the Planned Quantity for a period.
- **Actors:** Manager, Operations Staff, Administrator (per Section 6).
- **Preconditions:** N/A (a period may or may not have a Planned Quantity yet).
- **Trigger:** User views a period.
- **Main behavior:** System displays the stored Planned Quantity, or indicates that none has been entered.
- **Alternate behavior:** N/A.
- **Validation rules:** N/A (read operation).
- **Failure conditions:** N/A.
- **Postconditions:** Planned Quantity (or its absence) is visible to the user.
- **Dependencies:** SRS-FR-014.
- **Priority:** Essential.

### SRS-FR-017 — Validate Planned Quantity *(traces to PRD FR-017)*
- **Purpose:** Ensure only valid Planned Quantity values are stored.
- **Actors:** System.
- **Preconditions:** A Planned Quantity value has been submitted (SRS-FR-014 or SRS-FR-015).
- **Trigger:** Submission of a value.
- **Main behavior:** System checks that the value is present, numeric, and non-negative.
- **Alternate behavior:** On failure, system rejects the value with an explanatory message; no partial/invalid value is stored.
- **Validation rules:** Required; numeric; non-negative. (Whether a decimal or integer-only value is expected is not specified in source documents — open item, though minor.)
- **Failure conditions:** Missing, non-numeric, or negative value.
- **Postconditions:** Value stored (valid) or rejected with message (invalid).
- **Dependencies:** N/A.
- **Priority:** Essential.

### SRS-FR-018 — Calculate Variance *(traces to PRD FR-018)*
- **Purpose:** Quantify the gap between Forecasted Demand and Planned Quantity.
- **Actors:** System.
- **Preconditions:** Both Forecasted Demand (SRS-FR-011) and Planned Quantity (SRS-FR-014) exist for the same date/meal-type/location.
- **Trigger:** Both values become available for a period.
- **Main behavior:** System computes:
  - Potential Surplus = Planned Quantity − Forecasted Demand
  - Potential Shortage = Forecasted Demand − Planned Quantity
- **Alternate behavior:** If only one of the two values exists, variance is not computed; the period is shown as "awaiting forecast" or "awaiting planned quantity" as applicable.
- **Validation rules:** Both inputs must be valid, already-validated values.
- **Failure conditions:** Missing one of the two inputs.
- **Postconditions:** Variance value available for SRS-FR-019/020 and classification (SRS-FR-021).
- **Dependencies:** SRS-FR-011, SRS-FR-014.
- **Priority:** Essential.

### SRS-FR-019 — Calculate Variance Percentage *(traces to PRD FR-019)*
- **Purpose:** Express variance as a percentage for easier interpretation.
- **Actors:** System.
- **Preconditions:** SRS-FR-018 has produced a variance value.
- **Trigger:** Variance calculation completes.
- **Main behavior:** System computes a percentage representation of the variance relative to Forecasted Demand, where Forecasted Demand is non-zero.
- **Alternate behavior:** **The exact behavior when Forecasted Demand is zero (or otherwise makes percentage calculation undefined) is not specified in the PRD and is explicitly not invented here.** This is carried forward as an open edge-case decision (see Section 23).
- **Validation rules:** N/A beyond the above.
- **Failure conditions:** Forecasted Demand equal to zero (edge case — open).
- **Postconditions:** Variance percentage available for display, where computable.
- **Dependencies:** SRS-FR-018.
- **Priority:** Essential.

### SRS-FR-020 — Display Forecast Comparison *(traces to PRD FR-020)*
- **Purpose:** Present Forecasted Demand, Planned Quantity, and variance together for a period.
- **Actors:** Manager, Administrator.
- **Preconditions:** At least one of Forecasted Demand or Planned Quantity exists for the period.
- **Trigger:** User views the period.
- **Main behavior:** System displays all available values (Forecasted Demand, Planned Quantity, variance, variance percentage where computable) together.
- **Alternate behavior:** If one value is missing, system indicates which value is not yet available rather than showing an incomplete or misleading comparison.
- **Validation rules:** N/A (read operation).
- **Failure conditions:** N/A.
- **Postconditions:** User has a clear view of the comparison state for the period.
- **Dependencies:** SRS-FR-011, SRS-FR-014, SRS-FR-018, SRS-FR-019.
- **Priority:** Essential.

### SRS-FR-021 — Apply Threshold Rule *(traces to PRD FR-021)*
- **Purpose:** Determine, from the variance, which classification a period should receive.
- **Actors:** System.
- **Preconditions:** Variance (SRS-FR-018) exists.
- **Trigger:** Variance calculation completes.
- **Main behavior:** System compares the variance against a defined threshold to determine Surplus, Shortage, or Balanced.
- **Alternate behavior:** N/A.
- **Validation rules:** **The exact numeric threshold value is intentionally not defined in this SRS.** It is treated as a configurable/defined business parameter to be finalized in a later stage (see Section 23). The rule direction (Section 14) is fixed; only the numeric cutoff is open.
- **Failure conditions:** Threshold parameter undefined at runtime (a TRD-stage concern for how a default/config value is supplied).
- **Postconditions:** Classification input is ready for SRS-FR-022.
- **Dependencies:** SRS-FR-018.
- **Priority:** Essential.

### SRS-FR-022 — Classify Period (Surplus/Shortage/Balanced) *(traces to PRD FR-022)*
- **Purpose:** Assign a clear status label to each period.
- **Actors:** System.
- **Preconditions:** SRS-FR-021 has been applied.
- **Trigger:** Threshold rule application.
- **Main behavior:**
  - **Surplus:** Planned Quantity exceeds Forecasted Demand beyond the defined threshold.
  - **Shortage:** Forecasted Demand exceeds Planned Quantity beyond the defined threshold.
  - **Balanced:** The difference is within the defined threshold.
- **Alternate behavior:** N/A.
- **Validation rules:** Depends on the (currently unresolved) threshold value from SRS-FR-021.
- **Failure conditions:** N/A beyond dependency on SRS-FR-021.
- **Postconditions:** Period is labeled Surplus, Shortage, or Balanced, and this label is available to SRS-FR-023 and SRS-FR-024.
- **Dependencies:** SRS-FR-021.
- **Priority:** Essential.

### SRS-FR-023 — Display Alert/Status *(traces to PRD FR-023)*
- **Purpose:** Make the classification visible to the Manager (and Administrator, per Section 6).
- **Actors:** Manager, Administrator.
- **Preconditions:** A period has been classified (SRS-FR-022).
- **Trigger:** User views the dashboard or the relevant period.
- **Main behavior:** System clearly displays the status label alongside the period's data.
- **Alternate behavior:** N/A.
- **Validation rules:** N/A (read operation).
- **Failure conditions:** N/A.
- **Postconditions:** Status is visible to the user.
- **Dependencies:** SRS-FR-022.
- **Priority:** Essential.

### SRS-FR-024 — Generate Rule-Based Redistribution Recommendation *(traces to PRD FR-024)*
- **Purpose:** Provide a practical, advisory next step when a period is classified Surplus.
- **Actors:** System.
- **Preconditions:** A period is classified Surplus (SRS-FR-022).
- **Trigger:** Surplus classification.
- **Main behavior:** System generates a recommendation using predefined rules, which may reference: the estimated surplus quantity, a configured secondary location (if one has been set up — mechanism not defined here), and a predefined priority/action template.
- **Alternate behavior:** N/A.
- **Validation rules:** Recommendation generation must remain rule-based; it must not perform routing, matching, optimization, or external-system calls (see Section 15).
- **Failure conditions:** N/A beyond dependency on classification.
- **Postconditions:** A recommendation record is available for SRS-FR-025–027.
- **Dependencies:** SRS-FR-022.
- **Priority:** Essential.

### SRS-FR-025 — Display Estimated Surplus Quantity *(traces to PRD FR-025)*
- **Purpose:** Show the Manager how much surplus is estimated.
- **Actors:** Manager.
- **Preconditions:** SRS-FR-024 has produced a recommendation.
- **Trigger:** User views the recommendation.
- **Main behavior:** System displays the estimated surplus quantity (per the Section 13 formula) alongside the recommendation.
- **Alternate behavior:** N/A.
- **Validation rules:** N/A (read/display operation).
- **Failure conditions:** N/A.
- **Postconditions:** Estimated surplus quantity visible.
- **Dependencies:** SRS-FR-024.
- **Priority:** Essential.

### SRS-FR-026 — Display Recommendation/Action Text *(traces to PRD FR-026)*
- **Purpose:** Communicate the suggested action to the Manager.
- **Actors:** Manager.
- **Preconditions:** SRS-FR-024 has produced a recommendation.
- **Trigger:** User views the recommendation.
- **Main behavior:** System displays short, human-readable recommendation text (e.g., suggested reduction and/or redirection to a configured secondary location, if applicable).
- **Alternate behavior:** N/A.
- **Validation rules:** Text content must remain within the rule-based, advisory scope defined in Section 15.
- **Failure conditions:** N/A.
- **Postconditions:** Recommendation text visible.
- **Dependencies:** SRS-FR-024.
- **Priority:** Essential.

### SRS-FR-027 — Indicate Advisory Nature of Recommendation *(traces to PRD FR-027)*
- **Purpose:** Prevent the Manager from mistaking the recommendation for an executed or automatic action.
- **Actors:** Manager.
- **Preconditions:** A recommendation is displayed.
- **Trigger:** User views a recommendation.
- **Main behavior:** System clearly labels the recommendation as advisory, requiring human review and decision; the Manager retains full decision-making authority. No redistribution action is executed by the system.
- **Alternate behavior:** N/A.
- **Validation rules:** Must not imply an automated or completed action.
- **Failure conditions:** N/A.
- **Postconditions:** User understands the recommendation is advisory only.
- **Dependencies:** SRS-FR-024, SRS-FR-026.
- **Priority:** Essential.

### SRS-FR-028 — Dashboard Summary Display *(traces to PRD FR-028)*
- **Purpose:** Provide an at-a-glance operational view for the Manager (and Administrator).
- **Actors:** Manager, Administrator.
- **Preconditions:** User is authenticated with dashboard access (Section 6).
- **Trigger:** User navigates to the dashboard.
- **Main behavior:** System displays Forecasted Demand, Planned Quantity, variance, status, and recommendations for relevant periods.
- **Alternate behavior:** If data for a given period is incomplete, the dashboard indicates the missing piece rather than showing a misleading complete view.
- **Validation rules:** Content shown is scoped by role permissions.
- **Failure conditions:** N/A beyond upstream data availability.
- **Postconditions:** User has an accurate operational overview.
- **Dependencies:** SRS-FR-011, SRS-FR-014, SRS-FR-018–027.
- **Priority:** Essential.

### SRS-FR-029 — Dashboard Filtering by Location/Meal Type/Date *(traces to PRD FR-029)*
- **Purpose:** Let users narrow the dashboard to relevant periods.
- **Actors:** Manager, Administrator.
- **Preconditions:** Locations, meal types, and relevant data exist.
- **Trigger:** User applies a filter.
- **Main behavior:** System updates the dashboard to reflect the selected location/meal-type/date filter.
- **Alternate behavior:** If no data matches the filter, system indicates no matching data rather than an empty/ambiguous state.
- **Validation rules:** Filter values must reference existing locations/meal types.
- **Failure conditions:** Invalid filter selection.
- **Postconditions:** Dashboard reflects the filtered view.
- **Dependencies:** SRS-FR-028.
- **Priority:** Essential.

### SRS-FR-030 — View Historical Report *(traces to PRD FR-030)*
- **Purpose:** Let users review past Forecasted Demand vs. Planned Quantity performance.
- **Actors:** Manager, Administrator.
- **Preconditions:** Historical Forecasted Demand and Planned Quantity data exist.
- **Trigger:** User navigates to the reports view.
- **Main behavior:** System displays historical data (Forecasted Demand, Planned Quantity, variance, status) in table/chart form.
- **Alternate behavior:** If no historical data exists yet, system indicates this.
- **Validation rules:** Access scoped by role (Section 6).
- **Failure conditions:** N/A beyond data availability.
- **Postconditions:** Historical data visible to the user.
- **Dependencies:** SRS-FR-018, SRS-FR-022.
- **Priority:** Essential.

### SRS-FR-031 — Filter Reports by Date/Location/Meal Type *(traces to PRD FR-031)*
- **Purpose:** Let users narrow historical reports to a relevant subset.
- **Actors:** Manager, Administrator.
- **Preconditions:** SRS-FR-030 view is available.
- **Trigger:** User applies filters.
- **Main behavior:** System updates the report to show only records matching the selected date range, location, and/or meal type.
- **Alternate behavior:** If no records match, system indicates no matching data.
- **Validation rules:** Filter values must reference existing locations/meal types and a logically valid date range.
- **Failure conditions:** Invalid filter combination (e.g., end date before start date).
- **Postconditions:** Report reflects the filtered view.
- **Dependencies:** SRS-FR-030.
- **Priority:** Essential.

*(PDF/CSV export, scheduled reporting, and advanced analytics are explicitly Optional/Future and are not included as SRS requirements — see Section 17.)*

---

## 6. Authentication and Authorization Requirements

### Login
- Valid credentials → session established, scoped to role (SRS-FR-001).
- Invalid credentials → access denied, generic error message, no session established.
- Session behavior beyond this (timeout duration, token mechanism) is a TRD-stage decision.

### Logout
- Active session → session terminated (SRS-FR-002).
- After logout, any further action requires re-authentication.

### Role-based permissions
Unauthorized actions and, where applicable, unauthorized views must be prevented (SRS-FR-003). The baseline permission set, carried from the PRD, is:

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

**Cells marked "Unresolved" are carried forward exactly as the PRD left them** ("confirmation needed"). This SRS does not resolve them. They must be confirmed before or during the TRD stage (see Section 23).

---

## 7. User Management Requirements

- Create user: Administrator supplies at minimum an identifier and a role; system creates the account (SRS-FR-004).
- View user: Administrator can view existing user accounts and their assigned roles.
- Update user: Administrator can update user details and reassign roles.
- Deactivate user: Administrator can deactivate an account, preventing further login (reactivation behavior not specified — open item).
- Assign role: Every user account has exactly one of the three approved roles (Administrator, Manager, Operations Staff).

Only Administrators may perform these actions (enforced via SRS-FR-003). Password reset flows, email verification, multi-factor authentication, and social login are **not** included, as none are stated in the Foundation or PRD.

---

## 8. Location Management Requirements

- Create location: Administrator adds a new location, which becomes available in forecasting, Planned Quantity entry, and reporting (SRS-FR-005).
- View location: All roles with view permission (Section 6) can see the list of locations.
- Update location: Administrator can edit location details.
- Delete location: Administrator can request deletion. **The deletion-safety strategy (block deletion if referenced, cascade delete, or archive) is unresolved and is not decided in this SRS**, consistent with the PRD's unresolved status on this point.
- Locations must be available for selection wherever date/meal-type/location combinations are used (forecast requests, Planned Quantity entry, reports, dashboard filters).

---

## 9. Meal-Type Management Requirements

- Create meal type: Administrator adds a new meal type (e.g., Breakfast, Lunch, Dinner, or others), which becomes available in forecasting, Planned Quantity entry, and reporting (SRS-FR-006).
- View meal type: All roles with view permission (Section 6) can see the list of meal types.
- Update meal type: Administrator can edit meal-type details.
- Delete meal type: Same unresolved deletion-safety status as Section 8.
- Meal types remain fully configurable (not hardcoded), consistent with the Foundation's working assumption.

---

## 10. Historical Data Requirements

### Upload
System accepts an Administrator-submitted dataset containing date, day of week, meal type, location, and historical Actual Consumed Quantity (SRS-FR-007).

### Validation
At minimum, the system checks for:
- Required fields present
- Valid dates (logically valid calendar dates)
- Valid quantities (numeric, non-negative)
- Valid meal types (recognized/configured, or handled per an open decision on inline creation)
- Valid locations (recognized/configured, or handled per an open decision on inline creation)
- Malformed data (structurally unreadable records rejected outright)

(SRS-FR-008)

### Invalid records
The system identifies invalid records individually and reports the specific reason(s) each failed (SRS-FR-008, SRS-FR-010).

### Valid records
Valid records are stored and become available to the forecasting function (SRS-FR-009).

### Import status
The Administrator can view: records processed, valid record count, invalid record count, and validation failure reasons (SRS-FR-010).

### Duplicate records
**The PRD explicitly leaves duplicate handling unresolved. This SRS does not invent a reject/merge/overwrite policy.** It is carried forward as an open decision (Section 23).

No CSV libraries, parsers, storage engines, or APIs are defined in this section.

---

## 11. Forecasting Requirements

### Forecast Generation
The system shall generate Forecasted Demand for a selected date, meal type, and location (SRS-FR-011, SRS-FR-012), using the stored historical Actual Consumed Quantity data as input.

### Forecast Availability
- **Sufficient historical data exists:** System returns a Forecasted Demand value.
- **Insufficient historical data exists:** System clearly indicates a reliable forecast is not available, rather than fabricating or misleadingly displaying a value (SRS-FR-013). The exact sufficiency threshold is not defined here.
- **Forecast generation fails (technical failure, not a data-sufficiency issue):** System indicates the forecast is temporarily unavailable (see Section 18).

### Important restriction
No specific forecasting algorithm (e.g., regression-based, tree-based, time-series-specific, or neural approaches) is selected. No model training architecture, hyperparameters, feature-engineering implementation, or model-storage implementation is defined. These are explicitly deferred to the ML/TRD stage.

---

## 12. Planned Quantity Requirements

- **Enter:** Operations Staff submits a Planned Quantity for a date/meal-type/location (SRS-FR-014).
- **Validate:** Value must be present, numeric, and non-negative (SRS-FR-017).
- **View:** Authorized users can view the stored Planned Quantity (SRS-FR-016).
- **Edit:** Authorized users can update a previously entered Planned Quantity (SRS-FR-015). **The edit-window rule (whether/when editing becomes restricted, e.g., after the meal period passes) is explicitly unresolved and is not invented here.**

---

## 13. Forecast Comparison Requirements

### Variance
- Potential Surplus = Planned Quantity − Forecasted Demand
- Potential Shortage = Forecasted Demand − Planned Quantity

(SRS-FR-018)

### Variance percentage
A percentage representation is required where meaningful (i.e., where Forecasted Demand is non-zero) (SRS-FR-019). **The exact edge-case behavior when Forecasted Demand is zero (or otherwise makes the percentage undefined) is intentionally left open**, as the PRD does not define a formula for this case. This is not silently resolved here — see Section 23.

---

## 14. Surplus/Shortage Classification Requirements

- **Surplus:** Planned Quantity exceeds Forecasted Demand beyond the defined threshold.
- **Shortage:** Forecasted Demand exceeds Planned Quantity beyond the defined threshold.
- **Balanced:** The difference is within the defined threshold.

(SRS-FR-021, SRS-FR-022)

**The exact numeric threshold is intentionally not defined in this SRS.** It is treated as a configurable/defined business parameter whose final value must be determined at a later stage (TRD or business-rule confirmation). This SRS defines the classification logic's direction and structure only, not the cutoff value.

---

## 15. Redistribution Recommendation Requirements

The recommendation system is strictly:
- **Rule-based** — generated from predefined, non-ML logic.
- **Advisory** — informs, does not execute.
- **Human-reviewed** — the Manager retains the decision.
- **Non-executing** — no redistribution action is carried out by the system.

The recommendation may contain: estimated surplus quantity, a suggested action, an optional configured secondary location, and predefined priority/action text (SRS-FR-024–026).

The recommendation must **not**: perform transportation routing, perform donor/recipient matching, optimize logistics, integrate with external partners, execute any redistribution action, or imply that an action has already occurred (SRS-FR-027).

---

## 16. Dashboard Requirements

Required information (SRS-FR-028, SRS-FR-029):
- Forecasted Demand
- Planned Quantity
- Variance
- Variance percentage, where meaningful
- Surplus/Shortage/Balanced status
- Relevant alerts
- Recommendations
- Summary information sufficient for an at-a-glance operational view
- Historical information where reasonably supported by the underlying reporting data

No chart libraries, visual color schemes, frontend framework, or component architecture are defined here — these are TRD/UI-design-stage decisions.

---

## 17. Historical Reporting Requirements

Required (SRS-FR-030, SRS-FR-031):
- Historical Forecasted Demand vs. Planned Quantity records
- Date-range filtering
- Location filtering
- Meal-type filtering
- Status (Surplus/Shortage/Balanced) visibility within the report

**Not included** (Optional/Future, per Foundation v1.1 and PRD v1.0): PDF exports, CSV downloads, advanced analytics, scheduled reporting.

---

## 18. Validation and Error Handling

| Condition | Detection | System/User Response | Data Stored? | User Can Continue? |
|---|---|---|---|---|
| Invalid login | Credential check fails | Generic error message; access denied | No session | Yes, may retry |
| Malformed historical data | Structural check during validation | Record(s) rejected, reason reported | No | Yes, may re-upload |
| Missing required fields (any form) | Field presence check | Rejected with explanatory message | No | Yes, may resubmit |
| Invalid dates | Date format/logic check | Rejected with explanatory message | No | Yes, may resubmit |
| Negative quantities | Numeric range check | Rejected with explanatory message | No | Yes, may resubmit |
| Invalid Planned Quantity | SRS-FR-017 validation | Rejected with explanatory message | No | Yes, may resubmit |
| Duplicate records | **Detection method unresolved** | **Response unresolved** — carried forward as open decision | **Unresolved** | N/A until resolved |
| Insufficient historical data | Data-sufficiency check (threshold undefined) | Clear message that forecast is unavailable | N/A | Yes, other functions unaffected |
| Unavailable forecast (post insufficient-data check) | Same as above | Same as above | N/A | Yes |
| Forecasting failure (technical) | Generation process fails | Message that forecast is temporarily unavailable | N/A | Yes, other functions unaffected |
| Unauthorized actions | Role/permission check (SRS-FR-003) | Action blocked; user informed it is not permitted | N/A | Yes, may continue with permitted actions |

No programming-level exception handling (e.g., specific error codes, stack traces, retry/backoff logic) is defined — these are technical-stage decisions.

---

## 19. Data Requirements

Business-level information required by the system (no schema, tables, keys, or database technology defined):

- **User** — identifier, assigned Role.
- **Role** — Administrator, Manager, or Operations Staff.
- **Location** — identifier/name.
- **Meal Type** — identifier/name (configurable).
- **Historical Consumed Quantity** — date, day of week, meal type, location, quantity (historical Actual Consumed Quantity).
- **Forecasted Demand** — date, meal type, location, predicted quantity.
- **Planned Quantity** — date, meal type, location, quantity, entered-by reference.
- **Variance** — derived value linking a Forecasted Demand and a Planned Quantity for the same period.
- **Variance Percentage** — derived value, where computable.
- **Surplus/Shortage/Balanced Status** — derived classification for a period.
- **Redistribution Recommendation** — derived text and estimated surplus quantity, linked to a Surplus-classified period.

---

## 20. Non-Functional Requirements

- **Usability:** The system must be understandable and operable by non-technical food-service staff without extensive training, particularly for the Planned Quantity entry workflow (the most frequent Operations Staff interaction).
- **Security:** Authentication is required for all system access; role-based access control governs all actions and views per Section 6; unauthorized operations must be prevented, not merely hidden.
- **Reliability:** The core workflow (forecast generation → comparison → classification → recommendation → dashboard) must behave consistently across repeated use for the same inputs.
- **Performance:** The system must respond acceptably for dataset sizes typical of a single institution's historical records at internship/demo scale. No specific millisecond targets, uptime percentages, concurrent-user targets, or SLA commitments are defined.
- **Maintainability:** At the system-requirements level, the system's functional areas (Section 3) should remain separable enough that Optional/Future features (e.g., Actual Prepared/Consumed capture) can be added later without requiring a redesign of the core MVP requirements.
- **Responsive behavior:** The system must function as a responsive web application in standard desktop and reasonably sized tablet/mobile browser windows. It is not a native mobile application.
- **Accessibility:** Basic accessibility practices (e.g., readable contrast, clear labeling) should be followed where reasonable. No formal accessibility compliance standard is mandated.

---

## 21. System Constraints

- Internship-level project scope and timeline.
- MVP-scale system, not a production/enterprise deployment.
- No confirmed availability of real SensorSpine operational data at this stage.
- No confirmed hosting/deployment environment at this stage.
- Technology stack (frontend, backend, database) is not yet finalized.
- ML forecasting algorithm is not yet selected.

---

## 22. Assumptions and Dependencies

### Working Assumptions (carried forward, not confirmed facts)
1. Development team is solo or small.
2. Meal types are configurable by the Administrator rather than hardcoded.
3. Exact deployment/hosting environment will be proposed at a later stage.
4. No specific regulatory/food-safety/compliance requirements apply.
5. Actual Prepared/Consumed Quantity capture is optional for MVP but should not be architecturally precluded later.
6. "Surplus redistribution" means a system-generated recommendation only, not integration with external partners.
7. No specific forecast-accuracy target is required for MVP success.

### External Dependencies
- Availability of real historical company data (currently unconfirmed; synthetic/sample data is the fallback).
- Any company-specific requirements not yet communicated by SensorSpine.
- Technology/infrastructure constraints within SensorSpine, if any, not yet specified.

**Confirmed vs. assumed vs. unresolved status is preserved exactly as in the Foundation and PRD — nothing listed above has been upgraded to "confirmed" in this SRS.**

---

## 23. Open Issues Requiring Later Resolution

1. Real vs. synthetic historical data availability.
2. Single vs. multiple location scope for the MVP.
3. Technology stack preference/mandate (if any).
4. Whether redistribution must remain strictly recommendation-only, or whether any conceptual routing/logistics element is expected.
5. Whether an existing system requires integration.
6. Actual internship/project timeline, if it materially affects scope.
7. Permission-matrix cells marked "Unresolved" in Section 6 (Operations Staff visibility into forecasts, alerts, recommendations, reports; Admin/Manager ability to enter Planned Quantity).
8. Planned Quantity edit-window rule (Section 12).
9. Duplicate historical record handling policy (Section 10).
10. Exact numeric surplus/shortage threshold (Section 14).
11. Variance-percentage edge-case behavior when Forecasted Demand is zero (Section 13).
12. Minimum historical-data sufficiency threshold for forecast generation (Section 11 / SRS-FR-013).
13. Location/meal-type deletion-safety strategy (Sections 8–9).
14. User account duplicate-identifier handling (Section 7 / SRS-FR-004).

None of these are resolved in this SRS. They are explicitly carried forward for confirmation before or during the TRD stage.

---

## 24. Requirements Traceability Matrix

| PRD Requirement | SRS Requirement | Section | Status |
|---|---|---|---|
| FR-001 | SRS-FR-001 | 5, 6 | Defined |
| FR-002 | SRS-FR-002 | 5, 6 | Defined |
| FR-003 | SRS-FR-003 | 5, 6 | Defined (permission cells partly Open Decision) |
| FR-004 | SRS-FR-004 | 5, 7 | Defined (duplicate-identifier handling: Open Decision) |
| FR-005 | SRS-FR-005 | 5, 8 | Defined (deletion-safety: Open Decision) |
| FR-006 | SRS-FR-006 | 5, 9 | Defined (deletion-safety: Open Decision) |
| FR-007 | SRS-FR-007 | 5, 10 | Defined |
| FR-008 | SRS-FR-008 | 5, 10 | Defined (duplicate handling: Open Decision) |
| FR-009 | SRS-FR-009 | 5, 10 | Defined |
| FR-010 | SRS-FR-010 | 5, 10 | Defined |
| FR-011 | SRS-FR-011 | 5, 11 | Defined (algorithm: Open Decision, deferred by design) |
| FR-012 | SRS-FR-012 | 5, 11 | Defined |
| FR-013 | SRS-FR-013 | 5, 11 | Defined (sufficiency threshold: Open Decision) |
| FR-014 | SRS-FR-014 | 5, 12 | Defined |
| FR-015 | SRS-FR-015 | 5, 12 | Defined (edit-window rule: Open Decision) |
| FR-016 | SRS-FR-016 | 5, 12 | Defined |
| FR-017 | SRS-FR-017 | 5, 12 | Defined |
| FR-018 | SRS-FR-018 | 5, 13 | Defined |
| FR-019 | SRS-FR-019 | 5, 13 | Defined (zero-forecast edge case: Open Decision) |
| FR-020 | SRS-FR-020 | 5, 13 | Defined |
| FR-021 | SRS-FR-021 | 5, 14 | Defined (threshold value: Open Decision) |
| FR-022 | SRS-FR-022 | 5, 14 | Defined |
| FR-023 | SRS-FR-023 | 5, 14 | Defined |
| FR-024 | SRS-FR-024 | 5, 15 | Defined |
| FR-025 | SRS-FR-025 | 5, 15 | Defined |
| FR-026 | SRS-FR-026 | 5, 15 | Defined |
| FR-027 | SRS-FR-027 | 5, 15 | Defined |
| FR-028 | SRS-FR-028 | 5, 16 | Defined |
| FR-029 | SRS-FR-029 | 5, 16 | Defined |
| FR-030 | SRS-FR-030 | 5, 17 | Defined |
| FR-031 | SRS-FR-031 | 5, 17 | Defined |

All 31 PRD requirements are represented. None were removed or silently merged.

---

## 25. SRS-Level Acceptance Conditions

- **Authentication:** The system accepts valid credentials and denies invalid ones, in both cases per SRS-FR-001, with role-scoped access granted only on success.
- **Historical Data Import:** A submitted dataset is validated, valid records are stored and become available for forecasting, invalid records are reported with reasons, and the Administrator can view the import outcome.
- **Forecasted Demand:** For a location/meal-type combination with sufficient historical data, a Forecasted Demand value is returned; for insufficient data, a clear unavailability message is returned instead of a fabricated value.
- **Planned Quantity:** A valid Planned Quantity is stored and retrievable; an invalid value (negative, non-numeric, missing) is rejected with an explanatory message.
- **Forecast Comparison:** When both Forecasted Demand and Planned Quantity exist for a period, variance (and percentage, where computable) is correctly calculated per the defined formulas and displayed together with both source values.
- **Classification:** Periods are correctly labeled Surplus, Shortage, or Balanced according to the defined directional rule (exact threshold pending confirmation).
- **Redistribution Recommendation:** Every Surplus-classified period produces a rule-based, advisory recommendation including an estimated surplus quantity and action text, clearly marked as non-executing.
- **Dashboard:** The dashboard displays Forecasted Demand, Planned Quantity, variance, status, and recommendations for relevant periods, and supports filtering by location/meal type/date.
- **Reports:** Historical records are viewable and filterable by date range, location, and meal type.
- **Role Enforcement:** Actions and views outside a user's permitted set (per Section 6, including resolved cells) are blocked.
- **Location/Meal-Type Management:** Newly created locations/meal types become immediately selectable across forecasting, Planned Quantity entry, and reporting.

*(A detailed QA test-case plan is not created here — that is a separate later-stage document.)*

---

## 26. Final SRS Summary

### System Capability Summary
The completed MVP system must support: role-based authentication and access control for three roles; Administrator-managed users, locations, meal types, and historical data with validation and import-status visibility; system-generated Forecasted Demand for selected date/meal-type/location combinations (algorithm unspecified); Operations Staff entry, editing, and viewing of Planned Quantity; automatic calculation of variance and variance percentage between Forecasted Demand and Planned Quantity; threshold-based classification into Surplus/Shortage/Balanced; rule-based, advisory redistribution recommendations for Surplus periods; a dashboard summarizing all of the above with filtering; and basic, filterable historical reports. No specific ML algorithm, database technology, API design, or frontend/backend framework is chosen anywhere in this document.

### Requirements Coverage
All 31 PRD requirements (FR-001–FR-031) have corresponding SRS requirements (SRS-FR-001–SRS-FR-031), as shown in Section 24. No PRD requirement was removed, merged without explanation, or silently altered.

### Outstanding Decisions
1. Permission-matrix cells for Operations Staff (Section 6).
2. Deletion-safety strategy for locations/meal types (Sections 8–9).
3. Duplicate historical record handling (Section 10).
4. Minimum historical-data sufficiency threshold for forecasting (Section 11).
5. Planned Quantity edit-window rule (Section 12).
6. Variance-percentage edge case when Forecasted Demand is zero (Section 13).
7. Exact numeric surplus/shortage threshold (Section 14).
8. User account duplicate-identifier handling (Section 7).
9. All six Must-Clarify Questions carried from the Foundation/PRD (real vs. synthetic data, single vs. multi-location, tech stack, redistribution scope, external integration, project timeline).

These should be resolved before or during the TRD stage to avoid rework.

### Next Document

**Next planned document: TRD / Technical Design**

*(The TRD has not been created. No database schema, ER diagram, API specification, ML model selection, UI implementation, or code has been produced at this stage.)*
