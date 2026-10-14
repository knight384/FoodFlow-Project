# Data Directory

This directory is a placeholder for **synthetic/demo historical datasets**
used for local development and mentor demonstrations (Database Specification
v1.0 Section 26).

## Phase 1 status

Empty — no sample data has been generated or added yet. Historical data
import, validation, and storage are not implemented in Phase 1.

## Rules for this directory (apply once data is added)

- Only synthetic/fabricated data may be committed here — **never real
  SensorSpine operational data** (Foundation v1.1; Database Specification
  v1.0 Section 26 explicitly requires this).
- Actual data files (`.csv`, `.xlsx`, etc.) are excluded from version
  control via `.gitignore` at the repository root — only this README is
  tracked. This avoids accidentally committing large or sensitive files;
  sample datasets should be generated locally via a script (to be added in
  a later phase) rather than checked in directly.
