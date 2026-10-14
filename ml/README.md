# FoodFlow ML / Forecasting Module

**Phase 5 status: implemented — but the runtime code lives inside
`backend/app/modules/forecasting/`, not in this directory.** See
"Where the implementation actually lives" below for why.

## Architecture note

Per TRD v1.0 Section 5 and Section 12, the forecasting component is
designed to run as an **internal Python module integrated with the
FastAPI backend process** — not a separate network service — consistent
with the approved modular-monolith architecture.

## Where the implementation actually lives

During Phase 5, the actual preprocessing/algorithm/evaluation/prediction
code was placed directly inside the existing backend module,
`backend/app/modules/forecasting/`, rather than here:

```text
backend/app/modules/forecasting/
├── preprocessing.py   # historical series retrieval (no data leakage)
├── algorithm.py         # baseline + candidate algorithms, and the
│                          evidence-based model-selection rationale
├── evaluation.py           # MAE/MAPE evaluation harness (time-based split)
├── interface.py               # narrow prediction interface (TRD v1.0 Section 12)
├── service.py                   # single-active-forecast persistence logic
├── schemas.py                     # request/response shapes
└── router.py                        # FC-001..003
```

**Why here instead of this directory:** keeping the runtime forecasting
code inside the backend's own package tree avoids a cross-directory
import dependency (`ml` is a sibling of `backend`, not a subpackage of
it) that would otherwise require either a `sys.path` manipulation hack
or an extra local-package `pip install` step just to make `ml.*`
importable from `backend/app`. Since Phase 5's own instructions require
"the forecasting component must remain an internal module of the
existing modular monolith," placing the code directly inside
`app/modules/forecasting/` is the most literal, lowest-risk way to
satisfy that — no path hacks, no second install step, and it matches
exactly how every other business module (locations, planned quantities,
etc.) is already structured.

This directory (`ml/`) remains reserved, per the repository structure
TRD v1.0 Section 24 anticipated, for genuinely standalone, offline
data-science work — e.g., a data scientist re-running the baseline-vs-
candidate evaluation against a larger or real dataset outside the
running application, without needing the full backend/database stack.
No such standalone script exists yet; `backend/app/modules/forecasting/evaluation.py`
is fully reusable for that purpose already (it takes plain Python data
structures, not database sessions, as input) if one is written later.

## What Phase 5 implemented (in `backend/app/modules/forecasting/`)

- **Data preparation**: retrieves already-validated `historical_consumption`
  records strictly before the requested forecast date (no data leakage);
  day-of-week is derived at this stage, never persisted (Database
  Specification v1.0 Section 6.5).
- **Baseline**: recent-period mean (last N records).
- **Candidate**: day-of-week seasonal mean, with a fallback to the
  baseline when too few same-weekday observations exist.
- **Evaluation**: MAE/MAPE via a time-based train/holdout split,
  matching ML & Testing Plan v1.0 Sections 6–7.
- **Selected model: the baseline.** Evaluated against the synthetic
  demo dataset (`backend/scripts/seed_demo_data.py`, RNG seed 42): the
  candidate did NOT outperform the baseline (aggregate MAE 17.89 vs.
  16.50; MAPE 9.38% vs. 8.65%) — consistent with that synthetic data
  having no deliberately-built day-of-week pattern. This is an
  evidence-based selection, not a default; see `algorithm.py`'s module
  docstring for the full reasoning, and `docs/phase-5-verification.md`
  for the complete write-up including how to reproduce this result.
- **Insufficient-data handling**: a clear `FORECAST_UNAVAILABLE` (422)
  response — never a fabricated value — when fewer than
  `MIN_HISTORICAL_RECORDS_FOR_FORECAST` (provisional, default 7) records
  exist for the requested (location, meal type).
- **Persistence**: single-active-forecast model (one row per location/
  meal type/date, per Database Specification v1.0 Section 6.8/17 — a
  proposed, not confirmed, decision).
- **API**: `POST/GET /forecasts`, `GET /forecasts/{id}` (FC-001..003).

## What remains explicitly open (not resolved by Phase 5)

- The minimum historical-data sufficiency threshold (provisional value only).
- Model retraining/re-evaluation cadence.
- Whether this selection holds once real (non-synthetic) operational
  data is available — every planning document treats real-data
  availability as an open Must-Clarify question.
- Forecast versioning beyond the single-active-forecast model already
  established in Phase 2's schema.

## Local setup (this directory's own dependencies, if a standalone script is added later)

```bash
cd ml
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Note: `backend/app/modules/forecasting/` does not depend on anything in
`ml/requirements.txt` — its implementation uses only the Python standard
library (`statistics`, `datetime`), deliberately, for simplicity and to
avoid adding a pandas/numpy runtime dependency to the backend for what
is, at this data scale, simple arithmetic over short in-memory lists.
