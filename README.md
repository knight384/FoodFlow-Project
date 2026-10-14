# FoodFlow

**Food-Service Demand Forecasting and Surplus Redistribution for Campuses and Hospitality**

Internship project — SensorSpine Private Limited.

## Status

**Phase 1: Repository & Development Environment Setup — complete.**
No business features are implemented yet. See
[`docs/phase-1-verification.md`](docs/phase-1-verification.md) for the full
verification report.

## What this is

A role-based web application that ingests historical meal-demand data,
forecasts future demand, compares it against planned preparation
quantities, flags potential surplus/shortage, and generates simple,
rule-based redistribution recommendations. See
[`docs/planning/`](docs/planning/) for the complete, approved planning
documentation (Foundation, PRD, SRS, TRD, Database Specification, API
Specification, ML & Testing Plan).

## Repository structure

```text
foodflow/
├── backend/     # FastAPI application (modular monolith — TRD v1.0 Section 5)
├── frontend/    # Next.js + TypeScript + Tailwind
├── ml/          # Forecasting/ML module (runs internally within the backend process)
├── docs/        # Planning documents + implementation phase reports
├── data/        # Synthetic/demo datasets only (never real production data)
├── scripts/     # Small local-dev utility scripts
└── docker-compose.yml   # Local PostgreSQL for development only
```

## Getting started

See [`backend/README.md`](backend/README.md) and
[`frontend/README.md`](frontend/README.md) for setup instructions, and
[`scripts/check_prerequisites.sh`](scripts/check_prerequisites.sh) to verify
your local environment has the required tools.

## Documentation

All approved planning documents live in [`docs/planning/`](docs/planning/)
and are the authoritative source of truth for this project:

1. Project Foundation & Scope Definition v1.1
2. Product Requirements Document (PRD) v1.0
3. Software Requirements Specification (SRS) v1.0
4. Technical Requirements / Technical Design Document (TRD) v1.0
5. Database Specification v1.0
6. API Specification v1.0
7. ML & Testing Plan v1.0
