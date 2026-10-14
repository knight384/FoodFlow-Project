# Phase 4 Dependency Fix Report
## Missing `python-multipart` runtime dependency
### Food-Service Demand Forecasting and Surplus Redistribution System (FoodFlow)

**Scope:** Targeted dependency fix only, per your instructions. No
business logic, API paths, schemas, database design, or RBAC changed.

---

## 1. Root Cause — Confirmed

Inspected `backend/app/modules/historical_data/router.py` directly. The
upload endpoint (HIST-001) is declared as:

```python
@router.post("/imports", response_model=ImportAcceptedResponse, status_code=status.HTTP_201_CREATED)
async def upload_historical_data(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("administrator")),
) -> ImportAcceptedResponse:
```

The `file: UploadFile` parameter is what triggers `multipart/form-data`
parsing — this is the correct, spec-mandated shape (API Specification
v1.0 Section 14 explicitly requires `multipart/form-data` for this
endpoint, and this exact code was already verified endpoint-conformant
in both the Phase 4 implementation report and the Phase 4 verification
pass).

However, FastAPI/Starlette do **not** bundle a multipart parser
themselves — they delegate to the separate `python-multipart` package
*at request-handling time*, not at import time. That's why:
- `python3 -m py_compile` never caught this (no import-time reference to `python-multipart` exists anywhere in the code — it's loaded lazily by Starlette internals).
- The static endpoint/schema conformance checks in prior verification passes never caught this (they check paths, methods, and field shapes — not the runtime request-parsing dependency chain).
- It only surfaces the moment an actual HTTP request hits an `UploadFile`-typed endpoint, which requires a live server — something this authoring environment has never been able to run (confirmed again this session: no network, no `pip install` possible here).

**This is a pure dependency-list omission, not a code defect.** The
router code was correct from the moment it was written; `requirements.txt`
simply never listed the package that code depends on at runtime.

---

## 2. Fix Applied

**File changed: `backend/requirements.txt` only.** One dependency line
added, with an inline comment explaining exactly why it's needed and
what error occurs without it (so this doesn't happen again silently):

```diff
 # --- Web framework ---
 fastapi==0.115.0
 uvicorn[standard]==0.30.6
 
+# --- Multipart form parsing ---
+# Required at RUNTIME by app/modules/historical_data/router.py's
+# `file: UploadFile` parameter (HIST-001, POST /historical-data/imports).
+# API Specification v1.0 Section 14 specifies multipart/form-data for
+# this endpoint. FastAPI/Starlette defer multipart parsing to this
+# package — it is never imported directly in application code, but is
+# loaded internally the moment any request hits an UploadFile-typed
+# endpoint. Without it, FastAPI raises at request time:
+#   RuntimeError: Form data requires "python-multipart" to be installed.
+# This was missing from Phase 4's original requirements.txt; added here
+# as a targeted dependency fix (no code/behavior change).
+python-multipart==0.0.9
+
 # --- Configuration ---
 python-dotenv==1.0.1
```

**Version choice:** `0.0.9` — a stable, widely-used release of
`python-multipart`, compatible with FastAPI `0.115.0`/Starlette (the
versions already pinned in this project). This is the standard package
FastAPI's own documentation names for this exact purpose.

**Nothing else was touched.** Confirmed via file-modification-time diff
against the last verification report: `backend/requirements.txt` is the
only file changed. `historical_data/router.py` and every other Phase
1–4 file are byte-identical to before this fix.

---

## 3. Confirmation: No Business Logic, API, Schema, Database, or RBAC Changes

- **API paths/methods:** unchanged — `router.py` not modified.
- **Request/response schemas:** unchanged — `schemas.py` not modified.
- **Business logic:** unchanged — `service.py` not modified.
- **Database/migrations:** unchanged — no migration file added or modified.
- **RBAC:** unchanged — `require_roles("administrator")` calls not modified.
- **Other Phase 4 modules** (locations, meal_types, planned_quantities, comparison, classification, recommendations): untouched.

---

## 4. Dependency Documentation

- `backend/requirements.txt` now self-documents the reason for this
  dependency (see the diff above) — this is the primary fix, since the
  omission itself was the defect.
- `backend/README.md`'s existing `pip install -r requirements.txt`
  instruction required **no wording change** — it already installs
  everything listed in the file, and now that includes
  `python-multipart`. No other documentation (module docstrings, prior
  verification reports) made an incorrect claim about this dependency
  that needs correcting — the omission was silent, not a false
  statement anywhere.
- This report itself is new documentation of the fix, added as a
  separate file (`docs/phase-4-dependency-fix.md`) rather than editing
  the two prior Phase 4 verification reports — those remain an accurate
  historical record of what was checked and missed at the time, per
  this project's established pattern of never rewriting past reports.

---

## 5. Test Suite Re-Run

**Not possible in this authoring environment** — same constraint as
every phase and pass before this one: no network egress (`pip install`
cannot reach PyPI here), no PostgreSQL, no Docker. This was re-confirmed
at the start of this fix.

What I verified instead, within this environment's limits:
- `backend/app/modules/historical_data/router.py` still compiles cleanly (`python3 -m py_compile`) — unchanged and syntactically valid.
- `backend/requirements.txt` is well-formed (one dependency per line, correctly pinned, no syntax issues that would break `pip install -r`).
- Confirmed via filesystem timestamp diff that no other file changed.

**Please re-run on your Windows environment:**
```bash
cd backend
pip install -r requirements.txt
pytest -v
```
Expected: the collection error (`RuntimeError: Form data requires
"python-multipart" to be installed.`) should no longer occur, and test
collection should proceed normally. Per the corrected count from the
verification pass, expect **39 tests** to run (not 38 — see
`docs/phase-4-verification-pass-2.md` Section 2.2 for that correction).

---

## 6. Status

**Dependency gap fixed at the source level** (root cause identified,
correct package added with a compatible pin, fully documented inline).
**Not yet confirmed resolved end-to-end** — that requires your
Windows-side `pip install` + `pytest` run, since this environment
cannot install packages or execute the suite. Please report back the
actual `pytest` output so this can be marked fully resolved rather than
just "fixed in theory."

Not proceeding to Phase 5.
