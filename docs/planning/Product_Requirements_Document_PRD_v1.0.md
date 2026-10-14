# Product Requirements Document (PRD)
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality

---

## 1. Document Control

- **Document title:** Product Requirements Document (PRD)
- **Project name:** Food-Service Demand Forecasting and Surplus Redistribution System (working title: FoodFlow — placeholder, to be confirmed)
- **Version:** 1.0
- **Status:** Draft, pending review
- **Purpose:** Define what the product must do (product requirements), based strictly on the approved Foundation. This document does not define how the system will be technically implemented.
- **Source document:** Project Foundation & Scope Definition v1.1 (approved baseline)
- **Scope:** Covers MVP product requirements only. Excludes SRS, technical design, database schema, API specification, ML model selection, and test plan — these are later-stage documents.

*(No authors, reviewers, approval dates, or sign-offs are stated here, as none have been provided.)*

---

## 2. Product Overview

The product is a web-based system that helps food-service operations (campus cafeterias, hostels, hospitality kitchens) plan meal preparation more accurately. It generates a **Forecasted Demand** for upcoming meal periods using a real ML forecasting component, lets staff record the **Planned Quantity** they intend to prepare, compares the two, and flags potential surplus or shortage. When a surplus is flagged, the system generates a simple, rule-based redistribution recommendation. All of this is presented through a dashboard and basic historical reports, with role-based access for Manager, Operations Staff, and Administrator.

It serves food-service managers and operations staff who currently plan preparation quantities largely by estimation or habit, without a structured, data-driven comparison point.

It exists to reduce the frequency and impact of overproduction (waste, avoidable cost) and underproduction (shortages, dissatisfaction), by giving staff visibility into a forecast-vs-plan gap before it becomes a problem.

The MVP is intended to demonstrate a complete, working pipeline — frontend, backend, database, a real (non-mocked) ML forecasting component, business logic, and data visualization — at a scope realistic for an internship timeframe. It is not intended to be a production-grade or enterprise platform.

---

## 3. Problem Statement

Food-service operations typically decide how much to prepare using manual estimation, habit, or static planning, rather than a structured, data-driven forecast. This creates two recurring problems that are often not visible until after the fact:

- **Overproduction**, resulting in food surplus and avoidable waste.
- **Underproduction**, resulting in shortages and operational disruption.

There is currently no lightweight, easy-to-use tool that allows a food-service manager to see a data-driven **Forecasted Demand**, compare it against the **Planned Quantity**, and receive a simple, actionable recommendation when a surplus is likely.

*(No statistics, waste percentages, or cost figures are asserted, as none have been confirmed by SensorSpine.)*

---

## 4. Product Goals and Objectives

**Product Goals:**
- Give food-service staff a data-driven reference point (Forecasted Demand) before finalizing preparation plans.
- Make the gap between forecast and plan visible and actionable, not just informational.
- Provide a simple, advisory path from "surplus detected" to "practical next step."

**MVP Objectives:**
- Deliver a complete, working forecast → comparison → alert → recommendation → dashboard pipeline.
- Use a real, functioning ML forecasting component (not a hardcoded or mocked value).
- Keep the interface usable for non-technical operations staff.
- Keep the system's scope small enough to build and demonstrate within an internship timeframe.

**Non-Goals (for this MVP):**
- Achieving or guaranteeing a specific forecast accuracy percentage.
- Automating or executing redistribution logistics.
- Supporting multiple organizations, external partners, or enterprise-scale deployment.
- Providing real-time, hardware-integrated, or IoT-based data collection.

---

## 5. Target Users and Personas

### 5.1 Cafeteria / Food-Service Manager
- **Goals:** Make informed preparation decisions; avoid both waste and shortages.
- **Main responsibilities:** Review forecasts, review surplus/shortage status, review redistribution recommendations, review historical reports, make operational decisions.
- **Pain points:** No structured way to compare what's planned against what's actually likely to be needed; surplus/shortage typically discovered too late to act on.
- **Needs:** Clear, timely visibility into Forecasted Demand vs. Planned Quantity, and a simple recommended action when a surplus is likely.
- **Key interactions:** Views dashboard, views forecasts, views alerts and recommendations, reviews historical reports.

### 5.2 Kitchen / Operations Staff
- **Goals:** Record planning information quickly and accurately, without added workload.
- **Main responsibilities:** Enter Planned Quantity for upcoming meal periods; view relevant operational information; optionally record actual quantities if/when that capability is available.
- **Pain points:** Planning is currently based on estimation/habit; no simple system to record and check plans against a forecast.
- **Needs:** A fast, low-friction way to enter Planned Quantity and see relevant status information.
- **Key interactions:** Enters/edits Planned Quantity, views operational dashboard information relevant to their role.

### 5.3 Administrator
- **Goals:** Keep the system correctly configured and populated with the data it needs.
- **Main responsibilities:** Manage users, manage locations, manage meal types, upload/manage historical data, oversee configuration.
- **Pain points:** Without a defined way to manage locations/meal types/data, the system cannot function correctly for other users.
- **Needs:** Straightforward tools to configure the system and load historical data without developer assistance.
- **Key interactions:** Manages users, locations, and meal types; uploads and reviews historical data import status.

*(Personas are role-based only. No fictional names, ages, companies, or demographic details are included.)*

---

## 6. User Journeys

### Journey A — Administrator loads historical data
Admin logs in → Opens data management → Uploads dataset (historical Actual Consumed Quantity by date, day of week, meal type, location) → System validates dataset → System shows validation result → Valid data is stored → Data becomes available for forecasting.

### Journey B — Manager obtains forecast
Manager logs in → Selects location/meal type/date → Requests/views forecast → System displays Forecasted Demand → Manager reviews forecast.

### Journey C — Operations Staff enters Planned Quantity
Staff logs in → Selects location/meal type/date → Enters Planned Quantity → Saves record → System confirms successful save.

### Journey D — System detects surplus/shortage
Forecasted Demand and Planned Quantity both exist for a period → System calculates variance → System applies threshold rule → System classifies the period as Surplus / Shortage / Balanced → Status is displayed.

### Journey E — Manager reviews redistribution recommendation
Surplus detected for a period → System generates a rule-based recommendation → Manager reviews the recommendation → Manager decides on an operational action (outside the system).

*(No technical implementation is defined in these journeys — they describe product-level interaction flow only.)*

---

## 7. Product Scope

### In Scope — MVP
1. Historical Data Import/Seed
2. Forecasted Demand Generation
3. Planned Quantity Entry
4. Forecasted Demand vs Planned Quantity Comparison
5. Surplus/Shortage Detection & Alert
6. Rule-Based Redistribution Recommendation
7. Dashboard
8. Basic Historical Reports
9. User Roles & Basic Authentication
10. Location & Meal-Type Management

### Optional / Future (not MVP)
- Actual Prepared Quantity capture
- Forward-looking Actual Consumed Quantity capture
- Forecast Accuracy Tracking
- Expanded in-app notifications
- PDF/CSV report export
- Configurable per-location alert thresholds
- Email/SMS notifications
- External food-donation/redistribution integrations
- Multi-location comparative analytics
- Mobile PWA
- More advanced forecasting models

### Out of Scope (excluded entirely, not just from MVP)
- Real-time IoT hardware integration
- Computer vision for food/quantity measurement
- Blockchain-based tracking
- Advanced/academic-level optimization research
- Real-time fraud or security monitoring systems
- Native mobile applications (iOS/Android)
- Microservices architecture (unless a genuine need is later justified)
- Complex multi-organization enterprise architecture
- Integration with external donation/NGO logistics platforms
- Payment processing of any kind
- Multi-language/localization support
- Automated external notifications (SMS/email/push)
- Transportation routing or donor-matching logic

---

## 8. Functional Requirements

### Authentication

**FR-001 — User Login**
- Description: The system shall allow a registered user to log in using credentials.
- Preconditions: User account exists.
- Actor: Admin, Manager, Operations Staff.
- Trigger: User submits login credentials.
- Expected behavior: On valid credentials, the system authenticates the user and grants access appropriate to their role. On invalid credentials, access is denied with a clear message.
- Business rules: Access must be role-scoped (see Section 13).
- Priority: Essential.
- Acceptance criteria: Given valid credentials, when the user submits them, then the system grants access to the role-appropriate interface. Given invalid credentials, when the user submits them, then the system denies access and displays an error.

**FR-002 — User Logout**
- Description: The system shall allow an authenticated user to log out.
- Preconditions: User is logged in.
- Actor: Admin, Manager, Operations Staff.
- Trigger: User selects logout.
- Expected behavior: The system ends the user's session and returns to the login screen.
- Business rules: None beyond standard session termination.
- Priority: Essential.
- Acceptance criteria: Given a logged-in user, when they select logout, then their session ends and further access requires re-authentication.

**FR-003 — Role-Based Permissions**
- Description: The system shall restrict available actions and views according to the authenticated user's role.
- Preconditions: User is authenticated.
- Actor: Admin, Manager, Operations Staff.
- Trigger: User attempts an action or navigates to a view.
- Expected behavior: The system allows or denies the action/view based on role (see Section 13).
- Business rules: Role definitions per Section 13; final permission details subject to confirmation where marked.
- Priority: Essential.
- Acceptance criteria: Given a user of a given role, when they attempt an action outside their permitted set, then the system prevents the action and indicates it is not permitted.

### User Management

**FR-004 — Administrator Manages Users**
- Description: The system shall allow an Administrator to create, view, update, and deactivate user accounts.
- Preconditions: Administrator is authenticated.
- Actor: Administrator.
- Trigger: Administrator accesses user management.
- Expected behavior: Administrator can perform user account operations; role is assigned per account.
- Business rules: Only Administrators may manage users.
- Priority: Essential.
- Acceptance criteria: Given an authenticated Administrator, when they create a new user with a role, then the account becomes available for login with the assigned role's permissions.

### Location Management

**FR-005 — Manage Locations (Create/View/Update/Delete)**
- Description: The system shall allow an Administrator to create, view, update, and delete locations/cafeterias.
- Preconditions: Administrator is authenticated.
- Actor: Administrator.
- Trigger: Administrator accesses location management.
- Expected behavior: Location records are created/updated/removed and become available for use elsewhere in the system (e.g., forecasts, Planned Quantity entry).
- Business rules: A location in active use (e.g., referenced by existing data) may require confirmation before deletion; exact deletion-safety rule to be finalized at SRS/technical stage.
- Priority: Essential.
- Acceptance criteria: Given an authenticated Administrator, when they add a new location, then it becomes selectable elsewhere in the system.

### Meal-Type Management

**FR-006 — Manage Meal Types (Create/View/Update/Delete)**
- Description: The system shall allow an Administrator to create, view, update, and delete meal types (e.g., Breakfast, Lunch, Dinner).
- Preconditions: Administrator is authenticated.
- Actor: Administrator.
- Trigger: Administrator accesses meal-type management.
- Expected behavior: Meal-type records are created/updated/removed and become available for use elsewhere in the system.
- Business rules: Same deletion-safety consideration as FR-005.
- Priority: Essential.
- Acceptance criteria: Given an authenticated Administrator, when they add a new meal type, then it becomes selectable elsewhere in the system.

### Historical Data

**FR-007 — Upload Historical Data**
- Description: The system shall allow an Administrator to upload historical meal-demand data (date, day of week, meal type, location, Actual Consumed Quantity).
- Preconditions: Administrator is authenticated; locations and meal types exist or are included in the upload.
- Actor: Administrator.
- Trigger: Administrator initiates a data upload.
- Expected behavior: The system accepts the upload and proceeds to validation.
- Business rules: Required fields per Section 10.
- Priority: Essential.
- Acceptance criteria: Given an authenticated Administrator, when they upload a data file, then the system begins the validation process.

**FR-008 — Validate Historical Data**
- Description: The system shall validate uploaded historical data before storing it.
- Preconditions: An upload has been submitted (FR-007).
- Actor: System (triggered by Administrator upload).
- Trigger: Completion of upload.
- Expected behavior: The system checks for required fields, valid formats, and valid values; separates valid from invalid records.
- Business rules: See Section 11 for invalid-data handling.
- Priority: Essential.
- Acceptance criteria: Given an uploaded file, when validation completes, then the system reports how many records are valid and how many are invalid, with reasons for invalid records.

**FR-009 — Store Validated Historical Data**
- Description: The system shall store valid historical records for use in forecasting.
- Preconditions: Validation (FR-008) has completed.
- Actor: System.
- Trigger: Validation produces valid records.
- Expected behavior: Valid records are persisted and become available to the forecasting component.
- Business rules: Invalid records are not stored as historical data.
- Priority: Essential.
- Acceptance criteria: Given valid records from an upload, when storage completes, then those records are available for forecast generation.

**FR-010 — View Import Status**
- Description: The system shall allow the Administrator to view the status/result of a historical data import.
- Preconditions: An upload has been submitted.
- Actor: Administrator.
- Trigger: Administrator views import history/status.
- Expected behavior: The system displays a summary (records processed, valid, invalid, and reasons for invalid records).
- Business rules: None beyond accurate reporting of the validation outcome.
- Priority: Essential.
- Acceptance criteria: Given a completed upload, when the Administrator views import status, then they see a summary of the outcome.

### Forecasting

**FR-011 — Generate/View Forecasted Demand**
- Description: The system shall generate and display a Forecasted Demand value for a selected date, meal type, and location.
- Preconditions: Sufficient historical data exists for the selected location/meal type (see FR-013 for the insufficient-data case).
- Actor: Manager (viewer); system (generator).
- Trigger: User selects date/meal type/location and requests a forecast, or the system generates it on a defined schedule/on-demand basis (exact mechanism to be defined at technical stage).
- Expected behavior: The system returns a Forecasted Demand value for the selected period.
- Business rules: Forecasting model/algorithm is not defined at this stage (see Foundation v1.1, Section 15); no specific accuracy is guaranteed.
- Priority: Essential.
- Acceptance criteria: Given sufficient historical data for a location/meal type, when a Manager requests a forecast for a future date, then the system displays a Forecasted Demand value.

**FR-012 — Select Date/Meal/Location for Forecast**
- Description: The system shall allow the user to select a date, meal type, and location to view the relevant Forecasted Demand.
- Preconditions: Locations and meal types are configured.
- Actor: Manager.
- Trigger: User navigates to the forecast view.
- Expected behavior: The system presents available locations/meal types/dates and returns the corresponding Forecasted Demand.
- Business rules: None beyond valid selection.
- Priority: Essential.
- Acceptance criteria: Given configured locations and meal types, when the Manager selects a valid combination, then the corresponding Forecasted Demand (if available) is shown.

**FR-013 — Handle Insufficient Historical Data**
- Description: The system shall clearly indicate when there is not enough historical data to generate a reliable Forecasted Demand for a selected location/meal type.
- Preconditions: A forecast has been requested for a location/meal type with insufficient historical data.
- Actor: System.
- Trigger: Forecast request where the underlying data does not meet the minimum needed (exact minimum to be defined at technical stage).
- Expected behavior: The system informs the user that a forecast cannot be reliably generated, rather than returning a misleading value.
- Business rules: The exact data-sufficiency threshold is not defined at PRD level.
- Priority: Essential.
- Acceptance criteria: Given insufficient historical data for a selection, when a forecast is requested, then the system displays a clear message instead of a fabricated or misleading forecast value.

### Planned Quantity

**FR-014 — Enter Planned Quantity**
- Description: The system shall allow Operations Staff to enter a Planned Quantity for a given date, meal type, and location.
- Preconditions: User is authenticated as Operations Staff (or a role permitted to enter this data); location and meal type exist.
- Actor: Operations Staff.
- Trigger: User submits a Planned Quantity for a selected period.
- Expected behavior: The system stores the value against the specified date/meal type/location.
- Business rules: Planned Quantity must be a valid, non-negative number (see Section 11).
- Priority: Essential.
- Acceptance criteria: Given an authenticated Operations Staff user, when they enter a valid Planned Quantity for a period, then the system stores it and confirms the save.

**FR-015 — Edit Planned Quantity**
- Description: The system shall allow an authorized user to edit a previously entered Planned Quantity, subject to business rules (e.g., before the meal period occurs).
- Preconditions: A Planned Quantity record exists.
- Actor: Operations Staff.
- Trigger: User edits an existing Planned Quantity.
- Expected behavior: The system updates the stored value.
- Business rules: Exact edit-window rules (e.g., whether editing is blocked after the meal period passes) are not defined at PRD level and are noted as an open product question.
- Priority: Essential.
- Acceptance criteria: Given an existing Planned Quantity, when the user updates it with a valid value, then the system stores the updated value and confirms the change.

**FR-016 — View Planned Quantity**
- Description: The system shall allow authorized users to view Planned Quantity for a given date/meal type/location.
- Preconditions: A Planned Quantity record may or may not exist.
- Actor: Manager, Operations Staff, Administrator (per role permissions).
- Trigger: User navigates to a view showing Planned Quantity.
- Expected behavior: The system displays the stored Planned Quantity, or indicates none has been entered yet.
- Business rules: View access per Section 13.
- Priority: Essential.
- Acceptance criteria: Given a stored Planned Quantity, when an authorized user views the relevant period, then the value is displayed.

**FR-017 — Validate Planned Quantity**
- Description: The system shall validate Planned Quantity input before storing it.
- Preconditions: User submits a Planned Quantity value.
- Actor: System.
- Trigger: Submission of FR-014/FR-015.
- Expected behavior: The system rejects invalid values (e.g., negative, non-numeric, missing) with a clear message.
- Business rules: See Section 11.
- Priority: Essential.
- Acceptance criteria: Given an invalid Planned Quantity (e.g., negative number), when the user attempts to save it, then the system rejects it and displays an explanatory message.

### Forecast Comparison

**FR-018 — Calculate Variance**
- Description: The system shall calculate the variance between Forecasted Demand and Planned Quantity for a given period once both values exist.
- Preconditions: Both Forecasted Demand and Planned Quantity exist for the same date/meal type/location.
- Actor: System.
- Trigger: Both values become available for a period.
- Expected behavior: The system computes the variance per the business rule in Section 9.
- Business rules: See Section 9 (Variance).
- Priority: Essential.
- Acceptance criteria: Given both a Forecasted Demand and a Planned Quantity for a period, when both exist, then the system computes and stores/displays the variance.

**FR-019 — Calculate Variance Percentage**
- Description: The system shall calculate a variance percentage where meaningful (i.e., where Forecasted Demand is non-zero).
- Preconditions: Variance (FR-018) has been calculated.
- Actor: System.
- Trigger: Variance calculation.
- Expected behavior: The system computes a percentage representation of the variance for easier interpretation.
- Business rules: Exact formula/edge-case handling (e.g., zero forecast) to be finalized at technical stage; must not produce a misleading or undefined display.
- Priority: Essential.
- Acceptance criteria: Given a valid Forecasted Demand and Planned Quantity, when variance is calculated, then a variance percentage is also shown where the calculation is meaningful.

**FR-020 — Display Comparison**
- Description: The system shall display Forecasted Demand, Planned Quantity, and the resulting variance together for a given period.
- Preconditions: At least a Forecasted Demand or Planned Quantity exists for the period.
- Actor: Manager, Administrator.
- Trigger: User views the relevant period.
- Expected behavior: The system presents the three values together in a clear, understandable way.
- Business rules: None beyond accurate display.
- Priority: Essential.
- Acceptance criteria: Given both values exist for a period, when the user views it, then Forecasted Demand, Planned Quantity, and variance are all visible together.

### Surplus/Shortage

**FR-021 — Apply Threshold Rule**
- Description: The system shall apply a threshold rule to the variance to classify a period.
- Preconditions: Variance (FR-018) exists.
- Actor: System.
- Trigger: Variance calculation completes.
- Expected behavior: The system applies a defined threshold to determine classification.
- Business rules: The specific numeric threshold is not finalized at PRD level; to be finalized during SRS/technical stage.
- Priority: Essential.
- Acceptance criteria: Given a calculated variance, when the threshold rule is applied, then a classification (Surplus/Shortage/Balanced) is produced.

**FR-022 — Classify Status (Surplus/Shortage/Balanced)**
- Description: The system shall classify each period as Surplus, Shortage, or Balanced based on the threshold rule.
- Preconditions: FR-021 has been applied.
- Actor: System.
- Trigger: Threshold rule application.
- Expected behavior: The system assigns and stores a classification for the period.
- Business rules: See Section 9 (Classification).
- Priority: Essential.
- Acceptance criteria: Given a variance beyond the surplus threshold, when classification runs, then the period is marked Surplus (and analogously for Shortage/Balanced).

**FR-023 — Display Alert/Status**
- Description: The system shall display the surplus/shortage/balanced status clearly to the Manager (and Administrator, per permissions).
- Preconditions: FR-022 has been completed for a period.
- Actor: Manager, Administrator.
- Trigger: User views the dashboard or relevant period.
- Expected behavior: Status is visibly indicated (e.g., as a label or flag) alongside the relevant period's data.
- Business rules: None beyond accurate, clearly visible status display.
- Priority: Essential.
- Acceptance criteria: Given a classified period, when the Manager views the dashboard, then the status is clearly visible.

### Redistribution Recommendation

**FR-024 — Generate Rule-Based Recommendation**
- Description: The system shall generate a rule-based redistribution recommendation when a period is classified as Surplus.
- Preconditions: A period is classified as Surplus (FR-022).
- Actor: System.
- Trigger: Surplus classification.
- Expected behavior: The system produces a recommendation using predefined rules (see Section 9).
- Business rules: Rule-based only; no optimization, routing, or matching logic (see Section 18).
- Priority: Essential.
- Acceptance criteria: Given a period classified as Surplus, when classification completes, then a recommendation is generated for that period.

**FR-025 — Display Estimated Surplus**
- Description: The system shall display the estimated surplus quantity as part of the recommendation.
- Preconditions: FR-024 has produced a recommendation.
- Actor: Manager.
- Trigger: User views the recommendation.
- Expected behavior: The estimated surplus quantity (per Section 9's formula) is shown alongside the recommendation text.
- Business rules: None beyond accurate calculation display.
- Priority: Essential.
- Acceptance criteria: Given a surplus recommendation, when the Manager views it, then the estimated surplus quantity is displayed.

**FR-026 — Display Recommendation/Action**
- Description: The system shall display the recommended action text to the Manager.
- Preconditions: FR-024 has produced a recommendation.
- Actor: Manager.
- Trigger: User views the recommendation.
- Expected behavior: A short, human-readable recommendation is shown (e.g., suggested reduction and/or redirection to a configured secondary location, if applicable).
- Business rules: See Section 9.
- Priority: Essential.
- Acceptance criteria: Given a surplus recommendation, when the Manager views it, then readable recommendation text is displayed.

**FR-027 — Indicate Advisory Nature of Recommendation**
- Description: The system shall clearly indicate that the redistribution recommendation is advisory, not an automated or authoritative action.
- Preconditions: A recommendation is displayed.
- Actor: Manager.
- Trigger: User views a recommendation.
- Expected behavior: The interface clearly communicates that the recommendation requires human review/decision and does not trigger any automated action.
- Business rules: The system must not imply that any redistribution action has occurred automatically.
- Priority: Essential.
- Acceptance criteria: Given a displayed recommendation, when the Manager views it, then it is clearly marked as advisory/for review, not as an executed action.

### Dashboard

**FR-028 — Dashboard Summary Display**
- Description: The system shall display a dashboard summarizing Forecasted Demand, Planned Quantity, variance, surplus/shortage status, and recommendations.
- Preconditions: User is authenticated as Manager or Administrator (per permissions).
- Actor: Manager, Administrator.
- Trigger: User navigates to the dashboard.
- Expected behavior: The dashboard presents the relevant summary information for the current/upcoming periods.
- Business rules: Content shown is scoped by role permissions (Section 13).
- Priority: Essential.
- Acceptance criteria: Given an authenticated Manager, when they open the dashboard, then Forecasted Demand, Planned Quantity, variance, status, and any recommendations are visible.

**FR-029 — Dashboard Filtering by Location/Meal/Date**
- Description: The system shall allow users to filter dashboard information by location, meal type, and/or date where supported.
- Preconditions: Locations, meal types, and relevant data exist.
- Actor: Manager, Administrator.
- Trigger: User applies a filter.
- Expected behavior: The dashboard updates to reflect the filtered selection.
- Business rules: None beyond accurate filtering.
- Priority: Essential.
- Acceptance criteria: Given multiple locations/meal types, when a user applies a filter, then only matching data is displayed.

### Reports

**FR-030 — View Historical Report**
- Description: The system shall allow users to view a historical report of Forecasted Demand vs. Planned Quantity (and resulting status) over a selected period.
- Preconditions: Historical Forecasted Demand and Planned Quantity data exist.
- Actor: Manager, Administrator.
- Trigger: User navigates to the reports view.
- Expected behavior: The system displays historical data in table/chart form.
- Business rules: Access per Section 13.
- Priority: Essential.
- Acceptance criteria: Given historical data exists, when a user opens the reports view, then that data is displayed.

**FR-031 — Filter Reports by Date/Location/Meal Type**
- Description: The system shall allow users to filter historical reports by date range, location, and meal type.
- Preconditions: FR-030 view is available.
- Actor: Manager, Administrator.
- Trigger: User applies filters to the report view.
- Expected behavior: The report updates to reflect the selected filters.
- Business rules: None beyond accurate filtering.
- Priority: Essential.
- Acceptance criteria: Given a date range/location/meal-type filter, when applied, then the report shows only matching records.

---

## 9. Business Rules

### Variance

To avoid ambiguity, the sign convention is defined explicitly:

- **Potential Surplus = Planned Quantity − Forecasted Demand** (positive value indicates a likely surplus — more is planned than is forecast to be needed)
- **Potential Shortage = Forecasted Demand − Planned Quantity** (positive value indicates a likely shortage — more is forecast to be needed than is planned)

Only one of these will typically be relevant/positive for a given period, depending on which quantity is larger.

### Classification

Each period is classified as one of:
- **Surplus** — Planned Quantity exceeds Forecasted Demand by more than a defined threshold.
- **Shortage** — Forecasted Demand exceeds Planned Quantity by more than a defined threshold.
- **Balanced** — the variance between the two is within the defined threshold.

*The specific numeric threshold value will be finalized during the SRS/technical stage. It is not defined in this PRD.*

### Redistribution Recommendation

The recommendation logic is:
- **Advisory only** — it informs the Manager; it does not execute or authorize any action.
- **Rule-based** — derived from simple, predefined rules (e.g., estimated surplus quantity, a configured secondary location if available, a predefined priority/action template).
- **Not a logistics optimization engine.**
- **No transportation routing.**
- **No donor/recipient matching.**
- **No external logistics or donation-platform integration.**

---

## 10. Data Requirements

The following are the core business data concepts referenced by this PRD (business meaning only — no schema, tables, or database technology are defined here):

- **User** — an account with a Role, used for authentication and permission scoping.
- **Role** — Administrator, Manager, or Operations Staff.
- **Location** — a cafeteria/food-service site.
- **Meal Type** — a category such as Breakfast, Lunch, or Dinner (configurable).
- **Historical Consumed Quantity** — historical Actual Consumed Quantity records (date, day of week, meal type, location, quantity), used to inform forecasting.
- **Forecasted Demand** — the system-generated predicted quantity for a future date/meal type/location.
- **Planned Quantity** — the quantity staff intend to prepare for a future date/meal type/location.
- **Surplus/Shortage Status** — the classification (Surplus/Shortage/Balanced) resulting from comparing Forecasted Demand and Planned Quantity.
- **Redistribution Recommendation** — the rule-based, advisory recommendation text and estimated surplus quantity associated with a Surplus-classified period.

*(Actual Prepared Quantity and forward-looking Actual Consumed Quantity are optional/future data concepts, not required for the MVP data set.)*

---

## 11. Validation and Error Handling Requirements

At the product level, the system is expected to behave as follows:

- **Invalid login:** The system denies access and shows a clear, non-specific error (does not reveal whether the username or password was incorrect).
- **Invalid data upload (format/structure):** The system rejects the malformed portion of the file and reports the issue to the Administrator.
- **Missing required fields:** The system flags the specific record(s) as invalid and does not store them as valid historical data; the Administrator is informed which records failed and why.
- **Negative quantities:** The system rejects negative values for Planned Quantity or historical consumed quantity, with a clear message.
- **Invalid dates:** The system rejects records with malformed or logically invalid dates (e.g., non-calendar dates).
- **Duplicate records:** The system flags likely duplicate historical records (e.g., same date/meal type/location appearing twice) for Administrator review; exact duplicate-handling rule (reject vs. merge vs. flag) to be finalized at technical stage.
- **Unavailable forecast:** If a forecast cannot be produced, the system communicates this clearly rather than showing a blank or misleading value (see FR-013).
- **Insufficient historical data:** Handled per FR-013.
- **Invalid Planned Quantity:** Rejected at entry with a clear message (see FR-017).
- **Forecast generation failure:** If the forecasting component fails to produce a result (e.g., due to a system/technical issue rather than insufficient data), the system informs the user that the forecast is temporarily unavailable, rather than displaying an error state that resembles valid data.

*(Exact wording, retry mechanisms, and logging behavior are technical-stage decisions, not defined here.)*

---

## 12. Dashboard and Reporting Requirements

**Dashboard** shall present, at minimum:
- Forecasted Demand
- Planned Quantity
- Variance (and variance percentage where meaningful)
- Surplus / Shortage / Balanced status
- Relevant alerts (i.e., periods flagged as Surplus or Shortage)
- Redistribution recommendations, clearly marked as advisory
- Summary information sufficient to give the Manager an at-a-glance operational picture
- Historical trend information where reasonably supported by the underlying reporting data (not a dedicated analytics/trend-tracking feature — that is Optional/Future per Section 7)

**Reports** shall support:
- Viewing historical Forecasted Demand vs. Planned Quantity records
- Filtering by date range
- Filtering by location
- Filtering by meal type

*(No visual layout, chart types, or UI design are specified here — that is a later-stage design decision.)*

---

## 13. Role and Permission Matrix

| Capability | Admin | Manager | Operations Staff |
|---|---|---|---|
| Login | ✓ | ✓ | ✓ |
| Manage Users | ✓ | — | — |
| Manage Locations | ✓ | View | View |
| Manage Meal Types | ✓ | View | View |
| Upload Historical Data | ✓ | — | — |
| View Forecasted Demand | ✓ | ✓ | View *(confirmation needed)* |
| Enter Planned Quantity | *(confirmation needed)* | *(confirmation needed)* | ✓ |
| View Surplus/Shortage Alerts | ✓ | ✓ | View *(confirmation needed)* |
| View Redistribution Recommendations | ✓ | ✓ | — *(confirmation needed)* |
| View Reports | ✓ | ✓ | Limited *(confirmation needed)* |

**Note:** The Foundation v1.1 establishes the three roles and their general responsibilities, but does not specify every permission at this level of granularity. Cells marked *(confirmation needed)* are product decisions that should be explicitly confirmed before or during the SRS stage — they are not invented requirements, but reasonable placeholders consistent with each role's described responsibilities in Foundation v1.1, Section 7–8.

---

## 14. Acceptance Criteria

**Feature: Historical Data Import**
- Given an authenticated Administrator, when they upload a valid historical data file, then the system validates it, stores the valid records, and reports the import outcome.

**Feature: Forecasted Demand Generation**
- Given sufficient historical data for a location/meal type, when a Manager requests a forecast for a future date, then the system displays a Forecasted Demand value.
- Given insufficient historical data, when a forecast is requested, then the system clearly indicates that a reliable forecast is not available.

**Feature: Planned Quantity Entry**
- Given an authenticated Operations Staff user, when the user enters a valid Planned Quantity, then the system stores the quantity against the selected date, location, and meal type, and confirms the save.
- Given an invalid Planned Quantity (e.g., negative), when the user attempts to save it, then the system rejects it with a clear message.

**Feature: Forecasted Demand vs Planned Quantity Comparison**
- Given both a Forecasted Demand and a Planned Quantity exist for a period, when the user views that period, then the variance (and percentage, where meaningful) is displayed alongside both values.

**Feature: Surplus/Shortage Detection & Alert**
- Given a variance beyond the defined threshold, when classification runs, then the period is marked Surplus or Shortage accordingly, and the status is visibly displayed to the Manager.
- Given a variance within the threshold, when classification runs, then the period is marked Balanced.

**Feature: Redistribution Recommendation**
- Given a period classified as Surplus, when the Manager views that period, then an estimated surplus quantity and a rule-based, advisory recommendation are displayed.

**Feature: Dashboard**
- Given an authenticated Manager, when they open the dashboard, then Forecasted Demand, Planned Quantity, variance, status, and recommendations for relevant periods are visible.

**Feature: Historical Reports**
- Given historical data exists, when a user applies a date/location/meal-type filter to the reports view, then only matching records are displayed.

**Feature: User Roles & Authentication**
- Given valid credentials, when a user logs in, then they are granted access scoped to their role.
- Given an attempted action outside a user's role permissions, when attempted, then the system prevents it.

**Feature: Location & Meal-Type Management**
- Given an authenticated Administrator, when they add a location or meal type, then it becomes available for selection elsewhere in the system.

---

## 15. Non-Functional Product Requirements

- **Usability:** The interface should be understandable by non-technical food-service staff without extensive training.
- **Basic security:** Authentication is required for all system access; role-based access control governs available actions (see Section 13).
- **Reliability:** The core pipeline (forecast → comparison → classification → recommendation → dashboard) should behave consistently for demo/testing purposes.
- **Maintainability:** Not directly a product requirement, but the product should be organized (from a user-facing structure standpoint) in a way that supports future extension (e.g., adding Actual Prepared/Consumed capture later) without redesign.
- **Performance expectations for MVP-scale data:** The system should perform acceptably for dataset sizes typical of a single institution's historical records (exact numeric performance targets are not defined at PRD level).
- **Responsive web experience:** The system should be usable on standard desktop and reasonably sized tablet/mobile browser windows; it is a responsive web application, not a native mobile app (see Section 7, Out of Scope).
- **Accessibility considerations:** Basic accessibility practices (e.g., readable contrast, clear labeling) should be followed where reasonable; no formal accessibility compliance standard is mandated at this stage.

*(No specific infrastructure-level SLAs, uptime targets, or load figures are defined, as none have been confirmed.)*

---

## 16. Success Criteria

The MVP succeeds when:
- Historical data can be ingested (uploaded, validated, and stored).
- Forecasted Demand is produced by a real, functioning ML forecasting component for a given date/meal type/location.
- Planned Quantity can be entered, edited, and viewed.
- Variance between Forecasted Demand and Planned Quantity is correctly calculated.
- Surplus/Shortage/Balanced status is correctly classified using the defined threshold rule.
- Rule-based redistribution recommendations are generated for Surplus-classified periods.
- The dashboard displays the required summary information.
- The end-to-end workflow (data → forecast → comparison → classification → recommendation → dashboard/reports) functions without manual intervention.
- The forecasting component is demonstrably real, not hardcoded or mocked.

*(No specific forecasting accuracy percentage is required for MVP success.)*

---

## 17. Dependencies, Assumptions, and Open Questions

### Confirmed Scope
- The MVP features listed in Section 7 (In Scope) are approved, per Foundation v1.1.
- The three roles (Administrator, Manager, Operations Staff) are approved and final for MVP.
- Redistribution recommendation logic is confirmed as rule-based and advisory only.
- Terminology (Forecasted Demand, Planned Quantity, Actual Prepared/Consumed Quantity) is confirmed and used consistently.

### Working Assumptions
1. Development team is solo or small, not a large team.
2. Meal types will be configurable by the Administrator rather than hardcoded.
3. Exact deployment/hosting environment is not yet determined and will be proposed later.
4. No specific regulatory/food-safety/compliance requirements apply.
5. Actual Prepared/Consumed Quantity capture is optional for MVP but should not be architecturally precluded later.
6. "Surplus redistribution" means a system-generated recommendation only, not an integration with external partners.
7. No specific forecast-accuracy target is required for MVP success; a working, demonstrable pipeline is the bar.

### External Dependencies
- Availability of real historical company data (currently unconfirmed — synthetic/sample data is the fallback).
- Any company-specific requirements not yet communicated by SensorSpine.
- Technology/infrastructure constraints, if any exist within SensorSpine, that have not yet been specified.

### Must-Clarify Questions (carried from Foundation v1.1)
1. Will SensorSpine provide real historical data, or should the project proceed entirely on synthetic/sample data?
2. Is the MVP expected to target a single location/cafeteria, or multiple locations?
3. Does SensorSpine have a mandated or preferred technology stack, or is this open to propose?
4. Should redistribution remain strictly a recommendation-only feature, or does SensorSpine expect any conceptual routing/logistics element even at a basic level?
5. Is there an existing system this needs to integrate with, or is this a fully standalone application?
6. What is the actual internship/project timeline, if it should influence how ambitious the MVP can be?

---

## 18. Scope-Creep Protection

The following are explicitly excluded from this product and must not be added without explicit approval:
- IoT hardware or sensor integration
- Computer vision-based food/quantity measurement
- Blockchain-based tracking
- Advanced/academic-level optimization research
- Transportation routing logic
- Donor/recipient matching logic
- External logistics or donation-platform integration
- Native mobile applications
- Payment or billing functionality
- Unnecessary microservices architecture
- Complex multi-organization enterprise architecture

---

## 19. Requirements Traceability

| Foundation Scope (Feature) | PRD Requirement IDs | Acceptance Criteria (Section 14) |
|---|---|---|
| Historical Data Import/Seed | FR-007, FR-008, FR-009, FR-010 | Historical Data Import |
| Forecasted Demand Generation | FR-011, FR-012, FR-013 | Forecasted Demand Generation |
| Planned Quantity Entry | FR-014, FR-015, FR-016, FR-017 | Planned Quantity Entry |
| Forecasted Demand vs Planned Quantity Comparison | FR-018, FR-019, FR-020 | Forecasted Demand vs Planned Quantity Comparison |
| Surplus/Shortage Detection & Alert | FR-021, FR-022, FR-023 | Surplus/Shortage Detection & Alert |
| Rule-Based Redistribution Recommendation | FR-024, FR-025, FR-026, FR-027 | Redistribution Recommendation |
| Dashboard | FR-028, FR-029 | Dashboard |
| Basic Historical Reports | FR-030, FR-031 | Historical Reports |
| User Roles & Basic Authentication | FR-001, FR-002, FR-003 | User Roles & Authentication |
| Location & Meal-Type Management | FR-004, FR-005, FR-006 | Location & Meal-Type Management |

*(SRS, technical design, and test artifacts are not created here — this table only demonstrates that every MVP feature has corresponding PRD requirements.)*

---

## 20. Product Risks

- **Insufficient historical data:** May limit forecast reliability or delay meaningful demonstration of the forecasting component.
- **Poor data quality:** Inconsistent or incomplete historical records could affect forecast usefulness.
- **Forecast limitations:** As no accuracy target is set, forecasts may be imprecise, especially with limited or synthetic data; this is expected and acceptable at MVP level but should be communicated to reviewers.
- **Ambiguous thresholds:** Undefined surplus/shortage thresholds could lead to inconsistent expectations if not finalized before the SRS stage.
- **Scope creep:** Pressure to add "impressive" features (routing, optimization, external integrations) could compromise the internship-appropriate scope.
- **User adoption/usability:** If data entry (e.g., Planned Quantity) is not fast and simple, Operations Staff may under-use the system.
- **Unclear company requirements:** Several Must-Clarify Questions remain open; proceeding without answers means some product decisions rely on Working Assumptions that may need revision later.

---

## 21. Final MVP Definition

The MVP is a role-based web application that: ingests historical Actual Consumed Quantity data (synthetic or provided); generates Forecasted Demand per date/meal type/location using a real ML forecasting component (algorithm to be selected at a later stage); allows Operations Staff to enter Planned Quantity; automatically compares Forecasted Demand to Planned Quantity; classifies each period as Surplus, Shortage, or Balanced using a threshold rule (to be finalized later); generates a simple, rule-based, advisory redistribution recommendation when a Surplus is detected; and presents all of this through a dashboard and basic historical reports — with authentication and role-based access across Administrator, Manager, and Operations Staff.

Actual Prepared Quantity and forward-looking Actual Consumed Quantity capture, along with all items in Section 7 (Optional/Future and Out of Scope), remain excluded from this MVP definition.

---

## PRD REVIEW SUMMARY

- **Total functional requirements defined:** 31 (FR-001 through FR-031)
- **MVP features covered:** 10 of 10 approved MVP features from Foundation v1.1 (see Section 19 traceability table)
- **Unresolved product decisions:**
  - Exact numeric threshold for Surplus/Shortage/Balanced classification (deferred to SRS/technical stage, as instructed)
  - Full granularity of the Manager/Operations Staff permission cells marked "confirmation needed" in Section 13
  - Exact edit-window rule for Planned Quantity (FR-015)
  - Duplicate historical record handling policy (reject vs. merge vs. flag)
- **Contradictions discovered in the Foundation:** None identified. Foundation v1.1's terminology, MVP feature list, and scope boundaries were internally consistent and could be translated directly into requirements without conflict.
- **Requirements recommended for mentor review:**
  - FR-013 (insufficient historical data handling) — worth confirming expected messaging/behavior with mentor early, since it affects perceived forecast reliability.
  - FR-021/FR-022 (threshold-based classification) — mentor input may help set a sensible placeholder threshold for demonstration purposes.
  - Section 13 permission matrix — the "confirmation needed" cells should be resolved with the mentor or SensorSpine before SRS, so downstream documents don't need rework.

**Next planned document: SRS**

*(The SRS has not been created. No technical design, database schema, API specification, ML model selection, or code has been produced at this stage.)*
