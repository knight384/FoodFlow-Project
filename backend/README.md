# FoodFlow Backend (FastAPI)

Phase 1 status: repository & development environment setup only. No business
endpoints are implemented yet (see API Specification v1.0 for the planned
full contract, and `../docs/planning/` for all approved planning documents).

## Prerequisites

- Python 3.12+
- A running PostgreSQL instance (see `../docker-compose.yml` for a local dev option)

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then edit .env if your local DB settings differ
```

## Run the development server

```bash
uvicorn app.main:app --reload --port 8000
```

Then visit:
- `http://localhost:8000/health` — liveness check
- `http://localhost:8000/health/db` — PostgreSQL connectivity check
- `http://localhost:8000/docs` — auto-generated interactive API docs (FastAPI/Swagger)

## Database schema (Phase 2: Database Implementation)

The full schema (10 tables per Database Specification v1.0) is defined as
SQLAlchemy ORM models under `app/modules/*/models.py`, and as a single
Alembic migration (`migrations/versions/0001_initial_schema.py`).

Apply the schema to your local database (after `docker compose up -d` from
the repo root, and after installing dependencies above):

```bash
alembic upgrade head
```

Then seed mandatory reference data (the three approved roles):

```bash
python3 -m scripts.seed_reference_data
```

Optionally, seed clearly-synthetic demo data (a couple of sample
locations, meal types, and ~60 days of synthetic historical consumption
records) for local development/demo purposes:

```bash
python3 -m scripts.seed_demo_data
```

No real SensorSpine data is used anywhere — see `scripts/seed_demo_data.py`'s
docstring and `../data/README.md`.

To create a new migration later (once models change in a further phase):

```bash
alembic revision --autogenerate -m "description of the change"
```

## Authentication & user management (Phase 3: Backend Foundation)

With the schema migrated and roles seeded (Phase 2 steps above), create
your first Administrator account directly via a Python shell (there is
no open "register" endpoint — user creation is Admin-only, and the very
first Admin has no one to create it for them):

```bash
cd backend
python3 << 'PY'
from app.database import session_scope
from app.core.security import hash_password
from app.modules.users.models import Role, User

with session_scope() as db:
    admin_role = db.query(Role).filter_by(name="administrator").one()
    db.add(User(username="admin", password_hash=hash_password("ChangeMe123!"), role_id=admin_role.id))
    db.commit()
    print("Admin user created.")
PY
```

Then, with the server running (`uvicorn app.main:app --reload --port 8000`):

```bash
# Log in
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "ChangeMe123!"}'
# -> { "token": "...", "user": { "id": "...", "username": "admin", "role": "administrator" } }

# Use the token to call a protected, Admin-only endpoint
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <token from above>"
```

See `docs/phase-3-verification.md` for the full endpoint list and what
remains open/deferred.

## Core business features (Phase 4)

With Phase 3's Admin user created and logged in (see above), you can now
exercise the Phase 4 modules. A quick smoke-test sequence:

```bash
# Create a location and meal type (Admin)
curl -X POST http://localhost:8000/api/v1/locations \
  -H "Authorization: Bearer <admin token>" -H "Content-Type: application/json" \
  -d '{"name": "Main Cafeteria"}'

curl -X POST http://localhost:8000/api/v1/meal-types \
  -H "Authorization: Bearer <admin token>" -H "Content-Type: application/json" \
  -d '{"name": "Lunch"}'

# Upload historical data (Admin) — CSV with header:
#   date,location,meal_type,actual_consumed_quantity
curl -X POST http://localhost:8000/api/v1/historical-data/imports \
  -H "Authorization: Bearer <admin token>" \
  -F "file=@/path/to/historical.csv"

# Enter a Planned Quantity (Operations Staff)
curl -X POST http://localhost:8000/api/v1/planned-quantities \
  -H "Authorization: Bearer <ops staff token>" -H "Content-Type: application/json" \
  -d '{"planDate": "2026-09-01", "locationId": "<id>", "mealTypeId": "<id>", "quantity": 200}'

# View the dynamically computed comparison/classification (Manager/Admin)
curl "http://localhost:8000/api/v1/comparisons?locationId=<id>&mealTypeId=<id>&date=2026-09-01" \
  -H "Authorization: Bearer <manager token>"
curl "http://localhost:8000/api/v1/classifications?locationId=<id>&mealTypeId=<id>&date=2026-09-01" \
  -H "Authorization: Bearer <manager token>"

# If classified Surplus, a recommendation now exists automatically:
curl "http://localhost:8000/api/v1/recommendations?locationId=<id>&mealTypeId=<id>" \
  -H "Authorization: Bearer <manager token>"
```

**No forecast-generation endpoint exists yet** (Phase 5). To exercise
comparison/classification/recommendations locally, insert a
`ForecastedDemand` row directly, clearly labeled as test/demo data (see
`tests/test_comparison_classification.py` for the pattern), before
creating the matching Planned Quantity.

See `docs/phase-4-verification.md` for the full endpoint list, the
provisional classification threshold, and everything left open.

## Run tests

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Project structure

```text
backend/
├── app/
│   ├── main.py              # FastAPI app + health-check endpoints only
│   ├── config.py             # Environment-based settings
│   ├── database.py            # SQLAlchemy engine/session, Base, connectivity check
│   ├── models_registry.py      # Imports all ORM models so Base.metadata is complete (for Alembic)
│   ├── core/                    # Shared/cross-cutting utilities (placeholder)
│   └── modules/                  # One package per business capability (TRD v1.0 Section 8)
│       ├── auth/                   # schemas.py, service.py, router.py — login/logout/me (Phase 3)
│       ├── users/                   # models.py + schemas.py, service.py, router.py — Admin-only CRUD (Phase 3)
│       ├── locations/                # + schemas.py, service.py, router.py — LOC-001..005 (Phase 4)
│       ├── meal_types/                # + schemas.py, service.py, router.py — MEAL-001..005 (Phase 4)
│       ├── historical_data/            # + schemas.py, service.py, router.py — HIST-001..003 (Phase 4)
│       ├── forecasting/                 # + preprocessing.py, algorithm.py, evaluation.py, interface.py,
│       │                                 #   schemas.py, service.py, router.py — FC-001..003 (Phase 5)
│       ├── planned_quantities/           # + schemas.py, service.py, router.py — PQ-001..004 (Phase 4)
│       ├── comparison/                    # schemas.py, service.py, router.py — CMP-001 (Phase 4, no models.py by design)
│       ├── classification/                 # schemas.py, service.py, router.py — CLS-001 (Phase 4, no models.py by design)
│       ├── recommendations/                  # + schemas.py, service.py, router.py — REC-001..002 (Phase 4)
│       ├── dashboard/                          # No models — read-oriented aggregation only (not yet implemented)
│       └── reports/                              # No models — read-oriented aggregation only (not yet implemented)
├── migrations/
│   ├── env.py                # Alembic environment (reads DB URL from app.config)
│   ├── script.py.mako          # Migration template
│   └── versions/
│       └── 0001_initial_schema.py   # Creates all 10 tables per Database Specification v1.0
├── scripts/
│   ├── seed_reference_data.py   # Mandatory: seeds the 3 approved roles
│   └── seed_demo_data.py         # Optional: seeds clearly-synthetic demo data
├── tests/
│   ├── test_health.py                       # Phase 1 foundation verification
│   ├── test_auth_users_wiring.py              # Phase 3 (DB-free wiring tests)
│   ├── conftest.py                             # Shared DB-backed fixtures (Phase 4+)
│   ├── test_locations.py                        # Phase 4
│   ├── test_meal_types.py                        # Phase 4
│   ├── test_historical_data.py                    # Phase 4
│   ├── test_planned_quantities.py                  # Phase 4
│   ├── test_comparison_classification.py            # Phase 4
│   ├── test_recommendations.py                        # Phase 4
│   └── test_forecasting.py                             # Phase 5
├── alembic.ini
├── requirements.txt
├── pyproject.toml               # ruff + pytest configuration
└── .env.example
```

Business-logic modules with a `models.py` contain **only ORM schema
definitions** — no service functions, no route handlers, and no CRUD
logic exist yet. Those are introduced module-by-module in later
implementation phases, following Technical Requirements / Technical
Design Document v1.0 (Section 8) and API Specification v1.0.

## Forecasting (Phase 5)

With historical data imported (Phase 4) for a location/meal type, you
can now generate a Forecasted Demand:

```bash
curl -X POST http://localhost:8000/api/v1/forecasts \
  -H "Authorization: Bearer <manager or admin token>" -H "Content-Type: application/json" \
  -d '{"forecastDate": "2026-09-01", "locationId": "<id>", "mealTypeId": "<id>"}'
```

Returns `201` with the generated forecast, `200` if one already exists
for that exact period (single-active-forecast model), or `422`
(`FORECAST_UNAVAILABLE`) if there isn't enough historical data (at
least `MIN_HISTORICAL_RECORDS_FOR_FORECAST`, default 7 records) for
that location/meal type strictly before the requested date.

**Selected model:** a simple recent-period mean (last
`FORECAST_RECENT_WINDOW_SIZE`, default 14, historical records) — chosen
over a day-of-week seasonal candidate based on actual evaluation against
the synthetic demo dataset (the candidate did not outperform it — no
real weekday pattern exists in that synthetic data). See
`app/modules/forecasting/algorithm.py`'s module docstring for the full
evaluation results and reasoning, and `docs/phase-5-verification.md` for
the complete write-up.

## What is intentionally NOT here yet (Phase 5 boundary)

Dashboard, reports, and production deployment configuration. Also not
implemented: routing, donor/recipient matching, logistics, optimization,
external integrations, notifications (none required by the source
documents — explicitly excluded); password reset, MFA, social login,
email verification (Phase 3 scope, still not required); true
server-side token invalidation on logout (stateless JWT trade-off — see
`app/core/security.py`); and — specific to forecasting — any advanced/
deep-learning model, external ML platform, or separate model-serving
infrastructure (explicitly excluded from Phase 5's scope; the selected
model is a simple, explainable statistical baseline). See
`docs/phase-5-verification.md` for the full list, including every
provisional/unresolved decision carried forward.
