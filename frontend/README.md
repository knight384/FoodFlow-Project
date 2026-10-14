# FoodFlow Frontend (Next.js + TypeScript + Tailwind)

Phase 1 status: repository & development environment setup only. The single
page in this app exists only to verify the frontend can reach the backend
and that the backend can reach PostgreSQL — it is not business UI.

## Prerequisites

- Node.js 18.18+ (Next.js 14 requirement)

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local   # then edit if your backend runs elsewhere
```

## Run the development server

```bash
npm run dev
```

Visit `http://localhost:3000` — you should see three status indicators
(Frontend / Backend API / Database connectivity). With the backend
running (see `../backend/README.md`) and a reachable PostgreSQL instance
(see `../docker-compose.yml`), all three should be green.

## Type-check and lint

```bash
npm run typecheck
npm run lint
```

## Project structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx     # Root layout
│   │   ├── page.tsx        # Phase 1 foundation-check page (not business UI)
│   │   └── globals.css      # Tailwind directives
│   └── lib/
│       └── config.ts         # API base URL only (no business API client yet)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── postcss.config.mjs
├── next.config.mjs
└── .env.example
```

## What is intentionally NOT here yet (Phase 1 boundary)

Login/authentication UI, role-aware navigation, dashboard, forecasts,
Planned Quantity forms, location/meal-type management, historical data
upload, reports, and any other business screen. See the Phase 1
verification report for the full list.
