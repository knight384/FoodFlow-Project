# ML & Testing Plan v1.0
## Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality

---

## 1. Document Control

- **Document title:** ML & Testing Plan
- **Project name:** Food-Service Demand Forecasting and Surplus Redistribution System (working title: FoodFlow — placeholder, to be confirmed)
- **Version:** 1.0
- **Status:** Draft, pending review
- **Purpose:** Define the forecasting/ML approach at a planning and evaluation level, and the overall software testing strategy, sufficient to guide implementation without prescribing source code or a final algorithm.
- **Source documents:** Project Foundation & Scope Definition v1.1; PRD v1.0; SRS v1.0; TRD v1.0; Database Specification v1.0; API Specification v1.0 — all approved.
- **Intended audience:** Project/Product Mentor, ML/Backend Developer (implementer), QA/Testers, Technical Reviewers.

*(No author names or approval dates are stated, as none have been provided.)*

---

## 2. Objectives of This Document

This document defines, at a planning/evaluation level (not implementation level):
1. The forecasting/ML approach — what is predicted, from what data, and how.
2. The dataset and preprocessing strategy.
3. How candidate models will be evaluated and selected, without selecting one now.
4. How insufficient historical data will be detected and handled.
5. How forecasting output connects to the rest of the product workflow.
6. The overall software testing strategy across all layers (unit, integration, API, frontend, end-to-end).
7. How the 31 SRS requirements will be validated.
8. How ML behavior specifically will be evaluated (distinct from general software testing).
9. How overall MVP readiness will be demonstrated to the mentor.

Consistent with the project's internship-level, non-research-grade objective (Foundation v1.1): the goal is a **real, functioning, measurable ML forecasting pipeline integrated into a working software system** — not a research contribution.

---

## 3. Forecasting Approach — Planning Level

### 3.1 What is predicted
**Forecasted Demand** — the predicted quantity of meals needed for a given future (date, meal type, location) combination, per PRD v1.0 Section 15 and SRS v1.0 Section 11.

### 3.2 Primary input
Historical **Actual Consumed Quantity**, stored in `historical_consumption` (Database Specification v1.0 Section 6.5), keyed by date, location, and meal type.

### 3.3 Potential supporting signals
- Date (already required)
- Day of week — **derived at query/preprocessing time from date**, not stored (Database Specification v1.0 Section 6.5) — consistent with that decision, day-of-week is computed during preprocessing (Section 5.2 below), not read from a persisted column.
- Meal type
- Location
- Other signals (e.g., seasonality, holidays, term/semester calendars) **only if justified by the dataset actually available** — none are assumed or required at this planning stage, consistent with Foundation v1.1's instruction not to invent company-specific data not provided.

### 3.4 What the model output feeds into
```text
Historical Consumed Quantity (historical_consumption)
        ↓
Data preparation (Section 5)
        ↓
Forecasting model (Section 6 — candidate approach, not selected)
        ↓
Forecasted Demand (persisted to forecasted_demand, per Database Spec Section 6.8;
                    exposed via POST/GET /forecasts, per API Spec Section 15)
        ↓
Compare with Planned Quantity (GET /comparisons — computed dynamically, API Spec Section 17)
        ↓
Surplus / Shortage / Balanced (GET /classifications — computed dynamically, API Spec Section 18)
        ↓
Rule-based recommendation (redistribution_recommendation, GET /recommendations)
        ↓
Dashboard / Reports (GET /dashboard, GET /reports)
```

This is the same end-to-end flow already established across the TRD, Database Specification, and API Specification — this document does not alter it, only elaborates the ML-specific portion.

### 3.5 What this document does NOT do
- Does not select a final forecasting algorithm.
- Does not define model training code, architecture, or hyperparameters.
- Does not define feature-engineering implementation.
- Does not define model-artifact storage implementation.

These remain deferred to the ML implementation stage, consistent with Foundation v1.1 Section 15, PRD v1.0 Section 15, SRS v1.0 Section 11, and TRD v1.0 Section 12 — all of which explicitly leave algorithm selection open until dataset characteristics are understood.

---

## 4. Dataset Strategy

### 4.1 Data source
Per Foundation v1.1 (Working Assumption) and Database Specification v1.0 Section 26: **synthetic/sample data is the working assumption**, since real SensorSpine operational data availability remains an open (Must-Clarify) question across every prior document. This plan does not assume real data will be provided.

### 4.2 Dataset shape
Each historical record: date, location, meal type, Actual Consumed Quantity (Database Specification v1.0 Section 6.5). No additional fields are assumed.

### 4.3 Synthetic dataset design principles (for development/evaluation, not production claims)
- Should span enough calendar time to allow meaningful day-of-week and (if used) seasonal pattern learning — an exact minimum duration is **not fixed here**, since it depends on the eventual model choice (Section 6) and is explicitly one of the open items carried forward (Section 12, item 3 — minimum historical-data sufficiency threshold).
- Should cover multiple locations and meal types if the MVP is confirmed to target more than one location (still an open Must-Clarify Question per Foundation v1.1/PRD/SRS/TRD/Database Spec/API Spec).
- Should include plausible variation (not perfectly uniform quantities) so evaluation is meaningful — exact generation method (e.g., randomized within a plausible range, with day-of-week patterns) is an implementation detail, not specified here.
- **All synthetic/demo data must be clearly labeled as such** — no real SensorSpine data is fabricated or implied, consistent with every prior document's instruction.

### 4.4 Data quality dependency
This plan explicitly depends on the Historical Data validation already defined in SRS v1.0 (Section 10) and Database Specification v1.0 (Section 21) — required fields, valid dates, non-negative quantities, valid location/meal-type references. The ML pipeline consumes only records that have already passed this validation (i.e., rows stored in `historical_consumption`), not raw uploaded data.

---

## 5. Data Preparation / Preprocessing Strategy

### 5.1 Scope
Preprocessing operates on validated `historical_consumption` records already stored in PostgreSQL (Database Specification v1.0 Section 6.5) — it does not re-validate data (that is the Historical Data module's responsibility, SRS-FR-008) or touch raw uploaded files directly.

### 5.2 Preprocessing steps (conceptual, not implementation)
1. **Retrieval:** Query historical records for the relevant location/meal-type scope needed for training/inference.
2. **Day-of-week derivation:** Compute day-of-week from `record_date` at this stage (not stored, per Database Spec Section 6.5) — this is the one place in the pipeline where that derivation concretely happens.
3. **Structuring:** Organize records into a form usable for forecasting — e.g., a time-ordered series per (location, meal type) combination. Exact structuring (e.g., a table indexed by date vs. a long-format series) is an implementation detail.
4. **Handling missing periods:** Historical data may have gaps (e.g., a closed day, a missed upload). This plan does not prescribe a specific imputation strategy at this stage — that is an implementation decision to be made once actual data patterns are understood, consistent with not locking model-specific choices prematurely.
5. **Feature preparation (if the eventual model needs explicit features):** Day-of-week, and potentially other derivable signals (Section 3.3), may be prepared as features — exact feature set deferred to the model-selection stage (Section 6), since it is algorithm-dependent.

### 5.3 What is explicitly not decided here
- Imputation strategy for missing historical periods.
- Exact feature engineering (beyond noting day-of-week as a candidate).
- Normalization/scaling approach (relevant only for certain model families — deferred).

---

## 6. Candidate Model Evaluation and Selection Approach

**No final algorithm is selected in this document.** This section defines *how* a model will be chosen, not *which* one.

### 6.1 Candidate approach categories (for consideration, not commitment)
Consistent with TRD v1.0 Section 12's explicit deferral, and Foundation v1.1's instruction not to lock in Random Forest, XGBoost, ARIMA, Prophet, LSTM, or any other specific algorithm, this plan frames candidates only by **category**, to be narrowed once actual dataset characteristics (volume, seasonality, noise) are known:
- **Simple statistical baselines** (e.g., a naive/seasonal-naive approach, a moving average) — useful as a correctness/sanity baseline regardless of which "real" model is eventually chosen.
- **Regression-based approaches** (e.g., using day-of-week and other derived features as predictors).
- **Time-series-specific approaches** (e.g., classical time-series decomposition/forecasting methods).
- **Tree-based approaches** (e.g., ensemble methods suited to tabular/feature-based data).

This plan does not rank or pre-select among these — the selection process (Section 6.3) determines the outcome from actual data.

### 6.2 Evaluation principle
**A baseline model must always be established first.** Whatever "real" model is eventually chosen, it is only meaningful relative to a simple baseline (e.g., "predict the same as last week's same day/meal/location," or "predict the historical average for that day-of-week"). This directly supports the project's "correctness" and "explainability" priorities (Section 2/Foundation v1.1) over sophistication.

### 6.3 Selection process (conceptual)
1. Establish the baseline (Section 6.2).
2. Prepare the dataset (Section 5).
3. Split historical data into a training portion and a held-out evaluation portion (a simple time-based split — training on earlier data, evaluating on later data — is recommended over a random split, since forecasting is inherently time-ordered; exact split ratio is an implementation detail).
4. Train/fit one or more candidate approaches (Section 6.1) on the training portion.
5. Evaluate each candidate against the held-out portion using the metrics in Section 7.
6. Select the candidate that performs best against the baseline **while remaining simple and explainable** — a marginal accuracy gain from a substantially more complex approach is not automatically preferred, consistent with the project's stated priorities.
7. Document the selected approach and its evaluation results as part of the ML implementation stage deliverable (not this document).

### 6.4 What is explicitly deferred
- The final selected algorithm.
- Hyperparameter values.
- Exact train/evaluation split ratio and methodology details.
- Model retraining cadence (TRD v1.0 Section 12 notes this as an implementation decision).

---

## 7. Evaluation Metrics

### 7.1 Principle
Per PRD v1.0 Section 16 and SRS v1.0 Section 17: **no specific forecast-accuracy percentage is required for MVP success.** This plan therefore defines metrics for **internal comparison and demonstration purposes**, not as a pass/fail gate against a mandated number.

### 7.2 Candidate metrics (to compute during model selection, Section 6.3)
- **Mean Absolute Error (MAE)** — average absolute difference between predicted and actual consumed quantity; simple, explainable in "meals" units, aligns with the project's explainability priority.
- **Mean Absolute Percentage Error (MAPE)** — useful for relative comparison across locations/meal types with different typical volumes, with the caveat that it is undefined/unstable when actual values are near zero (a known limitation to note, not solve, here).
- **Comparison against baseline (Section 6.2)** — the selected model's MAE/MAPE should be reported alongside the baseline's, so the improvement (if any) is demonstrable to the mentor.

### 7.3 What this plan does not do
- Does not mandate a target MAE/MAPE value.
- Does not claim the eventual model will achieve any specific accuracy.
- Does not require statistical significance testing or academic-level rigor — internship-appropriate, demonstrable comparison is sufficient.

---

## 8. Handling Insufficient Historical Data

### 8.1 Requirement basis
SRS-FR-013 and API Specification v1.0 Section 15 both require that the system clearly indicate when a forecast cannot be reliably generated, rather than fabricating a value.

### 8.2 Conceptual approach
- The forecasting component must be able to assess, for a given (location, meal type) combination, whether enough historical data exists to produce a reasonable forecast.
- **The exact minimum-data threshold (e.g., a minimum number of historical periods) is not defined in this document** — this is explicitly carried forward as an open/deferred decision from every prior document (TRD Section 29, Database Spec Section 29, API Spec Section 29) and remains so here (Section 12, item 3).
- When the threshold is not met, the forecasting component returns a clear "insufficient data" signal (not a fabricated numeric forecast) through its internal interface to the backend's `forecasting` module (TRD v1.0 Section 12), which the API surfaces as a `FORECAST_UNAVAILABLE` error (API Specification v1.0 Section 15, Section 28).

### 8.3 Testing implication
This behavior is directly testable (Section 10.6) — e.g., requesting a forecast for a (location, meal type) combination with zero or very few historical records should reliably produce the "insufficient data" response, never a numeric value.

---

## 9. Model Artifact and Inference Concept

Consistent with TRD v1.0 Section 12, and elaborating only at the planning level:
- **Training vs. inference separation:** A conceptual "training" step (learning from historical data) is distinct from an "inference" step (producing a Forecasted Demand for a specific requested period). This plan does not define their cadence (TRD explicitly defers this).
- **Model artifact:** Whatever model is chosen should produce a reusable trained state, avoiding retraining from scratch on every forecast request — exact storage mechanism remains undefined (TRD Section 12), consistent here.
- **Model version reference:** The Database Specification's optional `forecasted_demand.model_version` field (Section 6.8) exists for traceability; this plan does not mandate populating it with any particular scheme, only notes it as available if useful during evaluation record-keeping.
- **Future replaceability:** Because the forecasting module exposes a narrow interface (date/meal-type/location → Forecasted Demand or an insufficient-data signal — TRD Section 12), the selection process in Section 6 can be revisited later without requiring changes to the backend's other modules, the database schema, or the API contract.

No model registry, MLOps platform, or distributed training infrastructure is introduced — explicitly out of scope per this project's guardrails (Section 2).

---

## 10. Software Testing Strategy

This section defines the testing *layers* and what each validates — not detailed executable test cases (explicitly excluded from this document per the process rule).

### 10.1 Unit Testing
**Highest-priority target: business logic functions** — variance calculation, classification threshold logic, and recommendation rule application (TRD v1.0 Section 9, Section 25) — since these are pure, deterministic functions well-suited to unit testing.
- Variance: verify `potentialSurplus = plannedQuantity - forecastedDemand` and `potentialShortage = forecastedDemand - plannedQuantity` compute correctly for a range of inputs, including edge cases (equal values, zero forecast — noting the zero-forecast percentage edge case remains open, Section 12 item 6).
- Classification: verify Surplus/Shortage/Balanced assignment is directionally correct relative to a given (test-configured) threshold value — since the real threshold is unresolved (Section 12, item 5), unit tests should use a placeholder/configurable threshold rather than assuming a specific number.
- Recommendation: verify recommendation generation only triggers for Surplus classifications, and that generated text/estimated-surplus values are consistent with the input variance.
- Validation functions: non-negative quantity checks, valid-date checks, and other field-level validation rules (SRS Section 18, Database Spec Section 21, API Spec Section 23).

### 10.2 Integration Testing
Verifies backend modules interact correctly end-to-end within the application (TRD v1.0 Section 25):
- A historical data upload correctly flows into stored `historical_consumption` records, which then become available as forecasting input.
- A Planned Quantity entry, once a matching Forecasted Demand exists for the same period, correctly triggers a computable comparison.
- A Surplus classification correctly and automatically results in a `redistribution_recommendation` record (no manual trigger, per API Specification v1.0 Section 19).
- An import job's summary counts (`total_records`, `valid_records`, `invalid_records`) remain consistent with the actual resulting `historical_consumption` and `import_record_error` rows (Database Specification v1.0 Section 20).

### 10.3 API Testing
Verifies each endpoint in the API Specification (Section 9 there) behaves as contracted:
- Authentication/authorization enforcement — valid vs. invalid credentials (AUTH-001), protected endpoints reject unauthenticated requests, role checks reject out-of-scope actions.
- Request validation — each rule in API Specification v1.0 Section 23 (non-negative quantities, required fields, valid date formats, valid ID references) is exercised with both valid and invalid inputs.
- Response shape correctness — collection envelopes include pagination metadata; single-resource responses match the documented shape; error responses match the standard error model (API Specification v1.0 Section 8).
- Forecast unavailability — requesting a forecast for a period with insufficient historical data returns `FORECAST_UNAVAILABLE`, never a fabricated value (Section 8.3 above).
- Comparison/Classification endpoints — verify these remain read-only (no `POST`/`PATCH`/`DELETE` exists) and correctly reflect the underlying `forecasted_demand`/`planned_quantity` data dynamically (no stale/cached values, since neither is persisted — Database Specification v1.0 Sections 12–13).

### 10.4 Frontend/Component Testing
Verifies key UI components (TRD v1.0 Section 25):
- Planned Quantity entry form — valid/invalid input handling, save confirmation.
- Status badges — correctly render Surplus/Shortage/Balanced/Unavailable states.
- Recommendation display — correctly renders as advisory (never implying an executed action, per SRS-FR-027).
- Loading and error states — components correctly reflect API loading/error responses (API Specification v1.0 Section 8).

### 10.5 End-to-End Testing
Verifies the core user journeys (PRD v1.0 Section 6) work correctly across the full stack:
- **Journey A:** Administrator uploads historical data → sees import status with valid/invalid counts.
- **Journey B:** Manager requests/views a Forecasted Demand for a period.
- **Journey C:** Operations Staff enters a Planned Quantity → receives save confirmation.
- **Journey D:** System (automatically) computes variance and classifies a period once both Forecasted Demand and Planned Quantity exist.
- **Journey E:** For a Surplus-classified period, a recommendation is generated and visible to the Manager, clearly marked advisory.
- A combined scenario exercising all five journeys in sequence, to demonstrate the complete approved MVP workflow end-to-end (Section 11.1).

### 10.6 ML-Specific Evaluation (distinct from general software testing)
While general software testing (Sections 10.1–10.5) verifies *code correctness* (does the system behave as specified), ML evaluation (this section, elaborating Sections 6–8) verifies *model quality* — a different concern:
- **Baseline-vs-candidate comparison** (Section 6.2–6.3), reported with MAE/MAPE (Section 7).
- **Insufficient-data behavior verification** (Section 8.3) — treated as a testable software behavior (part of Section 10.3's API testing) even though it originates from an ML-layer decision.
- **Reproducibility check:** Given the same historical dataset and the same selected model/parameters, forecast generation should produce consistent results — this is a basic sanity check appropriate for an internship MVP, not a claim of formal reproducibility research rigor.

---

## 11. Requirements Validation Strategy

### 11.1 SRS Requirement Coverage
Every one of the 31 SRS requirements (FR-001–FR-031) must have a corresponding test at the appropriate layer (Section 10). The mapping principle:
- Authentication/Authorization (SRS-FR-001–003) → API testing + integration testing.
- User/Location/Meal-Type management (SRS-FR-004–006) → API testing + unit testing (validation rules).
- Historical Data (SRS-FR-007–010) → Integration testing (upload → validate → store flow) + API testing (import status endpoint).
- Forecasting (SRS-FR-011–013) → ML-specific evaluation (Section 10.6) + API testing (insufficient-data behavior) + end-to-end testing (Journey B).
- Planned Quantity (SRS-FR-014–017) → Unit testing (validation) + API testing + end-to-end testing (Journey C).
- Comparison (SRS-FR-018–020) → Unit testing (variance formulas) + API testing (`/comparisons` read-only behavior).
- Classification (SRS-FR-021–023) → Unit testing (threshold logic, with placeholder threshold) + API testing (`/classifications`).
- Recommendation (SRS-FR-024–027) → Unit testing (rule application) + integration testing (auto-generation on Surplus) + end-to-end testing (Journey E).
- Dashboard (SRS-FR-028–029) → API testing (`/dashboard` aggregation) + frontend/component testing.
- Reports (SRS-FR-030–031) → API testing (`/reports` filtering) + frontend/component testing.

This mapping does not repeat the full traceability matrices already produced in the PRD (Section 19), SRS (Section 24), Database Specification (Section 30), and API Specification (Section 26) — it instead assigns each requirement group to the testing layer(s) responsible for validating it.

### 11.2 Acceptance Criteria Validation
The Given/When/Then acceptance criteria already defined in PRD v1.0 Section 14 and echoed in SRS v1.0 Section 25 serve as the source for end-to-end and API test scenarios (Sections 10.3, 10.5) — this plan does not redefine them, only confirms they are the basis for test-scenario derivation.

---

## 12. Open and Deferred Items Relevant to ML & Testing

The following are **not resolved** in this document, consistent with every prior document's treatment of them:
1. Final forecasting algorithm (Section 6).
2. Exact evaluation metric target/threshold, if any is ever mandated beyond the "no target required" position (Section 7).
3. Minimum historical-data sufficiency threshold (Section 8).
4. Model retraining cadence (Section 9).
5. Numeric surplus/shortage classification threshold — used only as a placeholder/configurable value in unit tests (Section 10.1), never a real number.
6. Zero-forecast variance-percentage edge-case behavior — noted as a test case to define once the behavior itself is confirmed (Section 10.1), not resolved here.
7. Duplicate historical-record handling policy — affects what "clean" test data looks like for ML evaluation and Historical Data integration testing, but the policy itself remains undefined (carried from Database Spec/API Spec Section 29).
8. Planned Quantity edit-window rule — affects Journey C/E test scope once confirmed; untested until then.
9. Location/meal-type deletion-safety strategy — affects integration-test setup/teardown assumptions; undefined until confirmed.
10. Real vs. synthetic dataset availability — directly affects whether ML evaluation (Section 6–7) uses real or synthetic data; synthetic is the working assumption throughout this document.
11. Final deployment/hosting target — affects where automated tests run (e.g., CI environment), not the test content itself; undefined.
12. Unresolved role-permission cells — affect which roles' API/end-to-end test scenarios can be fully defined now vs. later (Section 10.3, 10.5).

None of these are guessed at or silently resolved by this document.

---

## 13. MVP Readiness Demonstration Plan

To demonstrate the MVP to the mentor, per PRD v1.0 Section 17 (Success Criteria) and SRS v1.0 Section 26:

1. **Data ingestion demonstration:** Upload a synthetic historical dataset; show the import status (valid/invalid counts, reasons).
2. **Forecast demonstration:** Request a Forecasted Demand for a period with sufficient synthetic historical data; show a real (non-fabricated, non-hardcoded) predicted value; separately demonstrate the insufficient-data path for a period with too little data.
3. **Planned Quantity demonstration:** Enter and edit a Planned Quantity for a period.
4. **Comparison/classification demonstration:** Show the dynamically computed variance and resulting Surplus/Shortage/Balanced status for a period where both values exist (using a placeholder threshold, clearly labeled as such, if the real threshold is still unconfirmed at demo time).
5. **Recommendation demonstration:** For a Surplus-classified period, show the automatically generated, clearly-advisory recommendation.
6. **Dashboard/reports demonstration:** Show the aggregated dashboard view and a filtered historical report.
7. **Baseline-vs-model comparison demonstration (Section 6–7):** Show the selected forecasting approach's MAE/MAPE against the simple baseline, on the held-out evaluation portion of the synthetic dataset, to demonstrate the forecasting component is real and measurably informative (even without a mandated accuracy target).

This demonstration plan directly exercises the full approved workflow (Section 3.4) and the core success criteria already defined in the PRD, without requiring any of the Section 12 open items to be resolved first — each open item is either demonstrated with a clearly-labeled placeholder (e.g., threshold) or demonstrated via its "not yet available" path (e.g., insufficient data).

---

## 14. Final ML & Testing Summary

### ML Capability Summary
The MVP's forecasting component must ingest validated historical Actual Consumed Quantity data, prepare it (including deriving day-of-week), evaluate at least one candidate forecasting approach against a simple baseline using MAE/MAPE, and produce a real, storable Forecasted Demand value per (date, meal type, location) — or a clear "insufficient data" signal when appropriate. No specific algorithm, accuracy target, or retraining cadence is fixed by this document.

### Testing Coverage Summary
All 31 SRS requirements are mapped to at least one testing layer (Section 11.1): unit, integration, API, frontend/component, or end-to-end testing, plus ML-specific evaluation for the forecasting-related requirements. No requirement is left without a defined validation approach at the planning level.

### Outstanding Decisions
The 12 items in Section 12 — spanning the final algorithm, evaluation targets, data-sufficiency threshold, retraining cadence, classification threshold, several edge cases, duplicate-handling policy, edit-window rule, deletion strategy, dataset availability, deployment target, and unresolved role permissions — remain open and should be tracked through implementation rather than resolved silently.

### Readiness
This ML & Testing Plan is ready to guide the ML implementation and the test-writing stage, provided the Section 12 open items are tracked and addressed as they are encountered, consistent with how every prior document in this series has handled its own open items.

**Next planned stage:** Implementation (ML model development, FastAPI backend, Next.js frontend, and the detailed executable test suite), guided by the TRD, Database Specification, API Specification, and this ML & Testing Plan together.

*(No ML training code, model implementation, FastAPI implementation, frontend implementation, database migrations, SQL, or detailed executable test-case files have been produced at this stage.)*
