"""
historical_data module.

Historical Actual Consumed Quantity upload, validation, storage, import status. See TRD v1.0 Section 8, SRS-FR-007-010.

Phase 2: HistoricalConsumption, ImportJob, ImportRecordError ORM models (see models.py).

Phase 4 (Core Backend Business Features) status: implemented.
- schemas.py — ImportAcceptedResponse, ImportJobSummary/DetailResponse, ImportJobListResponse
- service.py — CSV parsing/validation/import (day-of-week remains derived, never persisted;
  duplicate-record policy remains unimplemented, per Database Specification v1.0 Section 29)
- router.py — HIST-001..003 (API Specification v1.0 Section 14)
"""
