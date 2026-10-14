# Project Foundation & Scope Definition v1.1
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality
### SensorSpine Private Limited — Internship Project

**Document status:** Revised baseline, pending approval
**Supersedes:** Project Foundation & Scope Definition v1.0
**Document purpose:** Establish the agreed scope boundary before PRD/SRS/TRD creation

---

## 1. Project Title

**Food-Service Demand Forecasting and Surplus Redistribution System** (working title; short name: **FoodFlow** — placeholder, to be confirmed)

---

## 2. Project Overview

This project builds a software system that helps food-service operations (campus cafeterias, hostels, hospitality kitchens) predict how much food will be needed for upcoming meal periods, compare that prediction against what staff intend to prepare, and flag mismatches — particularly potential surplus — early enough that something useful can be done about it (e.g., reduce prep, redirect surplus, notify staff).

The system combines a standard web application (frontend + backend + database) with a lightweight AI/ML forecasting component, and presents insights through a dashboard.

This is an **internship-level MVP**, not a production enterprise platform. Scope is deliberately constrained to something buildable, testable, and demonstrable within an internship timeframe.

---

## 3. Problem Statement

Campus and hospitality food-service operations often decide how much to prepare based on manual estimation, habit, or static planning rather than data-driven forecasts. Because there is no structured way to compare a data-driven forecast against the planned quantity before a meal period, two recurring problems go undetected until it's too late:

- **Overproduction** → food surplus, waste, avoidable cost
- **Underproduction** → shortages, dissatisfied consumers, last-minute scrambling

There is typically no lightweight, easy-to-use tool that lets a food-service manager see a demand forecast, compare it against the planned quantity, and get a simple, actionable recommendation when a surplus is likely.

---

## 4. Business Problem

From a business perspective, food waste and shortages both represent avoidable cost and inefficiency:
- Waste = wasted raw material cost, wasted labor, and (where applicable) disposal cost
- Shortage = dissatisfied consumers, potential reputational impact, rushed reactive decisions

A tool that improves the accuracy of demand planning — even modestly — provides measurable value: less waste, fewer shortages, and better-informed operational decisions.

*(Note: specific cost figures, waste percentages, or ROI claims are not asserted here, since no confirmed operational data has been provided by SensorSpine. See Section 18 — Working Assumptions.)*

---

## 5. Proposed Solution

A web-based system where:
1. Historical **consumed-quantity** data is loaded/imported (synthetic/sample data for MVP unless real data is provided) and used to train a forecasting model.
2. The forecasting model predicts **Forecasted Demand** for upcoming meal periods (by date, meal type, and location).
3. Staff enter the **Planned Quantity** they intend to prepare for those same periods.
4. The system compares **Forecasted Demand** against **Planned Quantity** and flags potential surplus or shortage.
5. When a surplus is flagged, the system provides a **practical, rule-based redistribution recommendation** (e.g., suggested action, estimated quantity, and simple next step).
6. Optionally, staff may later record **Actual Prepared Quantity** and **Actual Consumed Quantity** to support retrospective analysis and forecast evaluation (see Section 6 for MVP status of this capability).
7. All of this is presented through a dashboard with visualizations and basic reports.

---

## 6. Project Objectives

1. Demonstrate a working, end-to-end forecasting-to-action pipeline (historical data → forecast → comparison against planned quantity → recommendation → dashboard).
2. Provide a usable interface for non-technical food-service staff.
3. Apply a real, demonstrable ML forecasting component (not a placeholder), with the specific algorithm decided later once dataset characteristics are understood.
4. Keep the system simple enough to build, test, and explain within an internship timeline.
5. Clearly distinguish forecasted, planned, and actual quantities so the system's logic is unambiguous.
6. Produce a system that is realistically extensible (without requiring that extension to be built now).

---

## 7. Target Users

| Role | Description |
|---|---|
| **Cafeteria / Food-Service Manager** | Primary user. Views forecasts, compares Forecasted Demand against Planned Quantity, reviews surplus/shortage alerts and redistribution recommendations, makes decisions. |
| **Kitchen / Operations Staff** | Enters/updates Planned Quantity (and optionally Actual Prepared/Consumed Quantity); views day-to-day operational dashboard. |
| **Administrator** | Manages system data (locations, meal types, historical data uploads), manages users, oversees configuration. |

No additional roles (e.g., "surplus recipient organizations," "district-level supervisors," "auditors") are included in MVP. See Section 21.

---

## 8. Primary User Needs

- **Manager:** "I want to know, before the meal period, whether the Planned Quantity is likely to exceed or fall short of Forecasted Demand — and what to do about it."
- **Operations Staff:** "I want a simple way to record what is planned (and optionally what was actually prepared/consumed) without extra work."
- **Administrator:** "I want to manage locations, meal types, and historical data without needing developer help."

---

## 9. Core User Workflow

```
Historical Consumed-Quantity Data (upload/seed)
        ↓
Data Processing (cleaning, aggregation)
        ↓
Forecasted Demand Generation (per date, meal type, location)
        ↓
Staff Enters Planned Quantity
        ↓
System Compares Forecasted Demand vs Planned Quantity
        ↓
Surplus / Shortage Detected & Flagged
        ↓
Redistribution Recommendation Generated (if surplus)
        ↓
Dashboard & Reports (visibility for Manager/Admin)

(Optional, non-blocking path:)
Actual Prepared / Actual Consumed Quantity recorded
        ↓
Used for retrospective analysis & future forecast evaluation
```

This mirrors the flow approved in v1.0; the terminology has been made precise per Revision 1, and the optional retrospective path has been made explicit so it is not confused with the core MVP loop.

---

## 10. MVP Feature List

| # | Feature | Purpose | Primary User | Priority |
|---|---|---|---|---|
| 1 | Historical Data Import/Seed | Load past consumed-quantity data (CSV upload or seeded sample dataset) | Administrator | Essential |
| 2 | Forecasted Demand Generation | Predict expected meal demand per date/meal-type/location | Manager | Essential |
| 3 | Planned Quantity Entry | Let staff record what they intend to prepare | Operations Staff | Essential |
| 4 | Forecasted Demand vs Planned Quantity Comparison | Compare the two values, compute variance | Manager | Essential |
| 5 | Surplus/Shortage Detection & Alert | Flag meal periods with significant variance | Manager | Essential |
| 6 | Redistribution Recommendation | Suggest a practical, rule-based action when surplus is detected | Manager | Essential |
| 7 | Dashboard (Overview) | Visual summary: forecast vs planned, trends, alerts | Manager, Admin | Essential |
| 8 | Basic Reports (historical view) | View past forecast-vs-planned history and surplus/shortage history | Manager, Admin | Essential |
| 9 | User Roles & Basic Auth | Login, role-based access (Manager/Staff/Admin) | All | Essential |
| 10 | Location & Meal-Type Management | Admin manages cafeterias/locations and meal types | Administrator | Essential |
| 11 | Actual Prepared/Consumed Quantity Entry | Capture what actually happened, for later evaluation | Operations Staff | Optional/Future |
| 12 | Forecast Accuracy Tracking | Compare Forecasted Demand to Actual Consumed Quantity over time | Manager | Optional/Future |
| 13 | Notification (in-app only) | In-app alert when surplus/shortage is flagged | Manager | Optional/Future |
| 14 | Export Reports (PDF/CSV) | Download reports for offline use | Manager, Admin | Optional/Future |

---

### Feature Details

**1. Historical Data Import/Seed**
- Purpose: Provide the data foundation for forecasting.
- Primary user: Administrator
- Workflow: Admin uploads a CSV (or system uses a pre-seeded sample dataset) containing date, day of week, meal type, location, and historical **Actual Consumed Quantity** (the field used to train/inform the forecast).
- Expected output: Clean, stored historical dataset available for model training/inference.
- Priority: Essential

**2. Forecasted Demand Generation**
- Purpose: Predict expected meal demand for upcoming periods.
- Primary user: Manager (consumer of output); system-generated.
- Workflow: System runs the forecasting model against historical consumed-quantity data for a given date/meal-type/location; returns a predicted quantity — the **Forecasted Demand**.
- Expected output: A numeric Forecasted Demand value per date/meal-type/location, viewable on dashboard.
- Priority: Essential

**3. Planned Quantity Entry**
- Purpose: Capture the quantity staff intend to prepare, to compare against the forecast.
- Primary user: Operations Staff
- Workflow: Staff enters the **Planned Quantity** for a given date/meal-type/location via a simple form.
- Expected output: Stored Planned Quantity value tied to that meal period.
- Priority: Essential

**4. Forecasted Demand vs Planned Quantity Comparison**
- Purpose: Quantify the gap between prediction and plan.
- Primary user: Manager
- Workflow: System automatically computes variance (Forecasted Demand − Planned Quantity) once both values exist for a period.
- Expected output: Variance value and percentage, shown per meal period.
- Priority: Essential

**5. Surplus/Shortage Detection & Alert**
- Purpose: Flag meal periods likely to result in a meaningful surplus or shortage.
- Primary user: Manager
- Workflow: System applies a threshold rule (e.g., variance beyond X%) to classify a period as Surplus / Shortage / Balanced, based on the Forecasted Demand vs. Planned Quantity comparison.
- Expected output: Status label + flag visible on dashboard.
- Priority: Essential

**6. Redistribution Recommendation**
- Purpose: Turn a surplus flag into a practical next step.
- Primary user: Manager
- Workflow: When a surplus is flagged (Planned Quantity meaningfully exceeds Forecasted Demand), the system applies a simple rule set to generate a recommendation — e.g., estimated surplus quantity, an available destination/secondary location if configured, and a predefined priority/action.
  - Example: Forecasted Demand = 450, Planned Quantity = 520, potential surplus = 70 → *"Potential surplus of 70 meals. Consider reducing the next preparation batch and redirecting available surplus to an approved secondary location."*
- Expected output: A short, actionable recommendation text tied to the flagged period.
- Priority: Essential
- Note: This remains explicitly **rule-based/logic-based**, not a second ML model, and not a logistics optimization, routing, matching, or marketplace system. The final rule design is deferred to later technical documentation, not decided here.

**7. Dashboard (Overview)**
- Purpose: Central visibility for decision-making.
- Primary user: Manager, Administrator
- Workflow: User logs in, sees Forecasted Demand vs. Planned Quantity charts, current alerts, and quick status per location/meal type.
- Expected output: Visual dashboard (charts + summary cards).
- Priority: Essential

**8. Basic Reports (historical view)**
- Purpose: Let users review past performance, not just today.
- Primary user: Manager, Administrator
- Workflow: User selects a date range/location and views historical Forecasted Demand vs. Planned Quantity data (and, if available, Actual Prepared/Consumed data) in table/chart form.
- Expected output: Historical report view within the app.
- Priority: Essential

**9. User Roles & Basic Auth**
- Purpose: Separate access appropriately, keep data integrity.
- Primary user: All
- Workflow: Login with role (Manager/Staff/Admin); role determines available actions.
- Expected output: Authenticated, role-scoped access.
- Priority: Essential

**10. Location & Meal-Type Management**
- Purpose: Keep the system configurable without code changes.
- Primary user: Administrator
- Workflow: Admin adds/edits locations and meal types used across the system.
- Expected output: Configurable list of locations/meal types used elsewhere in the app.
- Priority: Essential

**11. Actual Prepared/Consumed Quantity Entry** *(Optional/Future)*
- Purpose: Capture what actually happened operationally, distinct from what was planned.
- Primary user: Operations Staff
- Workflow: Staff optionally records Actual Prepared Quantity and/or Actual Consumed Quantity after a meal period.
- Expected output: Stored actual values, available for retrospective analysis.
- Priority: Optional/Future — not required for the core MVP loop, but data model should not preclude adding it later.

**12. Forecast Accuracy Tracking** *(Optional/Future)*
- Purpose: Evaluate how close Forecasted Demand was to Actual Consumed Quantity over time.
- Primary user: Manager
- Workflow: System compares historical Forecasted Demand to Actual Consumed Quantity once both exist.
- Expected output: Accuracy trend view.
- Priority: Optional/Future

---

## 11. Feature Classification

**A. Essential (MVP):**
Historical Data Import/Seed, Forecasted Demand Generation, Planned Quantity Entry, Forecasted Demand vs Planned Quantity Comparison, Surplus/Shortage Detection & Alert, Redistribution Recommendation, Dashboard, Basic Reports, User Roles & Auth, Location & Meal-Type Management.

**B. Useful but Optional (Future):**
Actual Prepared/Consumed Quantity Entry, Forecast Accuracy Tracking, in-app notifications beyond dashboard flags, PDF/CSV export of reports, configurable alert thresholds per location, simple email digest.

**C. Out of Scope (for this project entirely, not just MVP):**
See Section 21.

---

## 12. Functional Scope

In scope for MVP:
- CRUD for locations, meal types, historical records
- Forecasted Demand generation (batch or on-demand, not real-time streaming)
- Manual entry of Planned Quantity
- Automated variance calculation between Forecasted Demand and Planned Quantity
- Rule-based surplus/shortage flagging
- Rule/logic-based redistribution recommendation text
- Dashboard visualization (charts, summary cards, alerts list)
- Historical reporting view
- Basic authentication and role-based access (Manager, Staff, Admin)

Optional, non-blocking for MVP:
- Actual Prepared Quantity / Actual Consumed Quantity capture, for retrospective use only

---

## 13. Non-Functional Scope (High Level)

- **Usability:** Simple, clean UI understandable by non-technical staff.
- **Performance:** Should comfortably handle sample/synthetic dataset sizes typical of a single institution (not big-data scale).
- **Reliability:** Core flow (Forecasted Demand → comparison → alert) should work consistently for demo/testing purposes.
- **Maintainability:** Codebase should be organized clearly enough for a mentor/reviewer to follow.
- **Security:** Basic authentication and role separation; no claim of enterprise-grade security hardening for MVP.
- **Portability/Deployment:** Should be runnable in a standard dev/demo environment (exact hosting/infra approach to be defined later — not yet confirmed).

---

## 14. Data Scope

**Core fields used across the MVP, with precise terminology:**
- Date
- Day of week
- Meal type
- Location/cafeteria
- **Actual Consumed Quantity** *(historical — used to train/inform the forecast)*
- **Forecasted Demand** *(system-generated output)*
- **Planned Quantity** *(entered by staff — compared against Forecasted Demand)*
- **Actual Prepared Quantity** *(optional/future — operational record)*
- **Actual Consumed Quantity, forward-looking** *(optional/future — used for retrospective forecast evaluation)*

**Data source for MVP:** Synthetic or sample dataset, unless/until SensorSpine explicitly provides real operational data.

**Explicitly noted:** No claim is made that SensorSpine has provided real operational data. This is a working assumption (see Section 18) pending confirmation (see Section 17/Must-Clarify Questions).

---

## 15. AI/ML Scope

**What is being predicted:** **Forecasted Demand** — the expected quantity of meals needed for a given future date, meal type, and location.

**What data may be used:** Historical **Actual Consumed Quantity**, along with date, day of week, meal type, and location, as the basis for learning demand patterns. Historical Planned/Prepared Quantity may also be explored as supporting signal, but Actual Consumed Quantity is the primary target variable.

**Why forecasting is needed:** To give staff an independent, data-driven reference point before they finalize the Planned Quantity, so mismatches can be caught proactively rather than discovered after the fact.

**What the prediction is used for:** Compared against the **Planned Quantity** entered by staff, to detect likely surplus or shortage before (or shortly after) the meal period occurs.

**What happens after prediction:**
1. Forecasted Demand is stored and displayed.
2. Once a Planned Quantity exists for the same period, the system computes variance.
3. Variance beyond a defined threshold triggers a surplus or shortage flag.
4. A surplus flag triggers a rule-based redistribution recommendation.
5. *(Optional/future)* If Actual Consumed Quantity is later recorded for that period, it can be used to evaluate forecast accuracy retrospectively.

**How surplus/shortage is determined:** Via a threshold-based comparison rule (e.g., variance percentage beyond a configurable limit) applied to Forecasted Demand vs. Planned Quantity. Exact thresholds and rules are not finalized here — to be defined in later technical documentation.

**Model selection:** Intentionally not decided at this stage. No specific algorithm (e.g., regression-based methods, tree-based methods, time-series-specific methods, or neural approaches) is selected here. The final model will be chosen after dataset characteristics are understood, in the ML/technical documentation stage. No specific forecast-accuracy percentage is promised at this stage.

---

## 16. Expected Outputs

- A working web application (frontend + backend + database)
- A functioning forecasting model producing real Forecasted Demand values from real or synthetic historical data
- A dashboard showing Forecasted Demand vs. Planned Quantity, surplus/shortage status, and recommendations
- Historical reporting view
- Basic documentation of how the system works (to follow this foundation document)

---

## 17. Success Criteria

For MVP purposes, the project can be considered successful if:
1. The system ingests historical consumed-quantity data and produces a **Forecasted Demand** for a given date/meal-type/location.
2. Staff can enter **Planned Quantity** through the UI.
3. The system correctly computes variance between Forecasted Demand and Planned Quantity, and flags surplus/shortage per defined rules.
4. Surplus periods generate a readable, practical, rule-based recommendation.
5. The dashboard clearly displays Forecasted Demand, Planned Quantity, variance, and status.
6. The system runs end-to-end (frontend → backend → DB → ML component → back to frontend) without manual intervention.
7. The forecasting component is demonstrably functioning (not hardcoded/mocked).

*(No specific numeric accuracy target, e.g., "forecast must be within X% accuracy," is set here, since dataset and model have not yet been evaluated. See Must-Clarify Questions.)*

---

## 18. Working Assumptions

*(Formerly "Key Assumptions" — retained and expanded per Revision 4; see Section B at the end for the consolidated list used for PRD planning.)*

- Real operational data from SensorSpine has **not** been confirmed as available; synthetic/sample data will be used unless stated otherwise.
- "Surplus redistribution" for MVP means generating a **rule-based recommendation**, not integrating with external donation/logistics organizations or systems.
- A single or small number of locations is sufficient for MVP demonstration (not a large multi-site enterprise deployment).
- The internship timeline is limited, so architecture and scope favor simplicity over completeness.
- No specific regulatory, food-safety, or compliance requirements have been provided, so none are assumed.
- No specific technology stack has been mandated by SensorSpine; a stack will be proposed in the technical documentation stage unless SensorSpine specifies one.
- Actual Prepared/Consumed Quantity capture is treated as optional for MVP; the data model should not preclude adding it later.

---

## 19. Constraints

- Internship-level time and resource constraints.
- Likely solo or small-team development (team size not confirmed — see Must-Clarify Questions).
- No confirmed access to real operational/live data at this stage.
- No confirmed infrastructure/hosting environment at this stage.

---

## 20. Risks and Scope-Creep Risks

| Risk | Type | Mitigation |
|---|---|---|
| Attempting to build a highly accurate/production-grade ML model | Scope creep | Keep model "good enough to demonstrate the pipeline," not research-grade |
| Adding real-time/IoT data feeds | Scope creep | Explicitly out of scope (Section 21) |
| Expanding redistribution into a full logistics/marketplace feature | Scope creep | Keep as a rule-based recommendation/message only for MVP |
| Adding many user roles (donors, auditors, multi-org admins) | Scope creep | Restrict to 3 roles defined in Section 7 |
| Lack of real data delaying development | Data risk | Use synthetic/sample data as fallback (already planned) |
| Unclear thresholds for surplus/shortage | Ambiguity risk | Define configurable threshold in technical docs; flag as a Must-Clarify item |
| Trying to build native mobile apps | Scope creep | Web-based, responsive UI only for MVP |
| Blurring Forecasted Demand, Planned Quantity, and Actual values | Conceptual/data risk | Explicit terminology defined in Sections 5, 9, 14, 15 and used consistently throughout |

---

## 21. Explicit Out-of-Scope Items

The following are **explicitly excluded**, per the approved project direction and general MVP discipline:
- Real-time IoT hardware integration (e.g., smart scales, sensors)
- Computer vision for food/quantity measurement
- Blockchain-based tracking
- Advanced/academic-level optimization research
- Real-time fraud or security monitoring systems
- Native mobile applications (iOS/Android)
- Microservices architecture (unless a genuine, justified need emerges later)
- Complex multi-organization enterprise architecture
- Integration with external donation/NGO logistics platforms
- Payment processing of any kind
- Multi-language/localization support
- Automated external notifications (SMS/email/push) — in-app alerts only for MVP
- Any transportation routing or donor-matching logic

---

## 22. Future Enhancement Ideas

(Not part of MVP; listed only for context and future roadmap discussion)
- Actual Prepared/Consumed Quantity capture and forecast accuracy tracking over time
- Configurable, per-location alert thresholds
- Export reports (PDF/CSV)
- Email/SMS notifications
- Integration with external food-donation/redistribution partners
- Multi-location comparative analytics
- Mobile-responsive PWA (still not a native app)
- More advanced forecasting model(s) once baseline is validated

---

## 23. Final MVP Definition

The MVP is a role-based web application that: ingests historical consumed-quantity data (synthetic or provided); generates **Forecasted Demand** per date/meal-type/location using a real ML forecasting component (algorithm to be selected later); allows staff to enter **Planned Quantity**; automatically compares Forecasted Demand to Planned Quantity; flags surplus or shortage using a threshold rule; generates a simple, rule-based redistribution recommendation when surplus is detected; and presents all of this through a dashboard and basic historical reports — with authentication and role separation across Manager, Operations Staff, and Administrator.

Capturing **Actual Prepared Quantity** and **Actual Consumed Quantity** for retrospective analysis is explicitly optional/future, not required for the core MVP loop.

Everything in Section 21 is excluded. Everything in Section 22 is deferred.

---

## A. APPROVED MVP AT A GLANCE

| Feature | Priority |
|---|---|
| Historical Data Import/Seed | Essential |
| Forecasted Demand Generation | Essential |
| Planned Quantity Entry | Essential |
| Forecasted Demand vs Planned Quantity Comparison | Essential |
| Surplus/Shortage Detection & Alert | Essential |
| Redistribution Recommendation (rule-based) | Essential |
| Dashboard (Overview) | Essential |
| Basic Reports (Historical) | Essential |
| User Roles & Basic Auth | Essential |
| Location & Meal-Type Management | Essential |

---

## B. MUST-CLARIFY QUESTIONS BEFORE PRD

1. Will SensorSpine provide real historical data, or should the project proceed entirely on synthetic/sample data?
2. Is the MVP expected to target a single location/cafeteria, or multiple locations?
3. Does SensorSpine have a mandated or preferred technology stack (frontend framework, backend language, database, hosting), or is this open to propose?
4. Should redistribution remain strictly a recommendation-only feature, or does SensorSpine expect any conceptual routing/logistics element even at a basic level?
5. Is there an existing system this needs to integrate with, or is this a fully standalone application?
6. What is the actual internship/project timeline, if it should influence how ambitious the MVP can be?

---

## C. WORKING ASSUMPTIONS

*(Safe to use while preparing the PRD, unless SensorSpine states otherwise. Clearly labeled as assumptions, not confirmed requirements.)*

1. Development team is solo or small, not a large team.
2. Meal types (e.g., Breakfast/Lunch/Dinner) will be configurable by the Administrator rather than hardcoded.
3. Exact deployment/hosting environment is not yet determined and will be proposed later.
4. No specific regulatory/food-safety/compliance requirements apply.
5. Actual Prepared/Consumed Quantity capture is optional for MVP but should not be architecturally precluded.
6. "Surplus redistribution" means a system-generated recommendation only, not an integration with external partners.
7. No specific forecast-accuracy target is required for MVP success; a working, demonstrable pipeline is the bar.

---

## D. SCOPE-CREEP WARNING

The following should **not** be added without explicit approval, even if they seem like natural extensions:
- Any real-time hardware/IoT data ingestion
- Any computer-vision-based food quantity estimation
- Any blockchain/ledger-based tracking of food or transactions
- Any external donation/NGO/logistics platform integration
- Any native mobile app development
- Any expansion into a multi-organization/enterprise-wide platform
- Any payment or billing functionality
- Any move toward microservices without a clearly demonstrated need
- Any transportation routing or donor-matching algorithm
- Any promise of specific forecast accuracy percentages before the model has been built and evaluated
- Making Actual Prepared/Consumed Quantity entry mandatory in the core MVP loop without explicit approval

---

## E. REVISION SUMMARY (v1.0 → v1.1)

1. **Terminology clarified:** Introduced and consistently applied four distinct concepts — **Forecasted Demand**, **Planned Quantity**, **Actual Prepared Quantity**, and **Actual Consumed Quantity** — replacing looser terms like "actual," "planned/prepared," and "forecast vs actual" used in v1.0.
2. **MVP inputs narrowed:** Only historical Actual Consumed Quantity (for training) and Planned Quantity (for comparison) are required in the core MVP loop; Actual Prepared/Consumed Quantity capture going forward is reclassified as Optional/Future.
3. **Redistribution logic reaffirmed:** Explicitly restated as rule-based/logic-based only, with the worked example retained, and additional scope-creep guardrails added (no routing, no matching, no optimization engine).
4. **ML algorithm selection reaffirmed as open:** No algorithm is named; model selection is explicitly deferred to later ML/technical documentation.
5. **Open Questions reorganized:** Split into "Must-Clarify Questions Before PRD" (Section B) and "Working Assumptions" (Section C), per Revision 4.
6. **Consistency pass:** Updated Core User Workflow, Feature List, Feature Details, Data Scope, AI/ML Scope, Success Criteria, Assumptions, Risks, and Final MVP Definition to use the new terminology and reflect the narrowed MVP input scope. Sections not affected by these changes (e.g., Project Title, Target Users, Out-of-Scope list) were left structurally unchanged.

---

## F. NEXT STEP

Once this **Project Foundation & Scope Definition v1.1** is reviewed and approved (with the Must-Clarify Questions in Section B addressed or explicitly deferred), the next document will be the **Product Requirements Document (PRD)**.

**The PRD has not been created yet — this v1.1 document is pending your review first.**
