"""
Phase 5 tests: forecasting data preparation, algorithm selection,
evaluation, and the Forecast API (FC-001..003).

Requires a live database for the API-level tests (see
tests/conftest.py's module docstring for the testing-approach
trade-off). The algorithm/evaluation unit tests (TestAlgorithm,
TestEvaluation classes) are pure-Python and DB-free.
"""

import uuid
from datetime import date, timedelta

import pytest

from app.modules.forecasting.algorithm import day_of_week_seasonal_mean, recent_period_mean
from app.modules.forecasting.evaluation import evaluate_all_series
from app.modules.historical_data.models import HistoricalConsumption
from tests.conftest import unique_name

# ---------------------------------------------------------------------------
# Pure-Python unit tests (no database required)
# ---------------------------------------------------------------------------


def test_recent_period_mean_uses_full_window():
    history = [(date(2026, 1, i), float(i * 10)) for i in range(1, 6)]  # 10..50
    assert recent_period_mean(history, window=14) == 30.0  # mean of all 5


def test_recent_period_mean_uses_only_most_recent_window():
    history = [(date(2026, 1, i), float(i * 10)) for i in range(1, 11)]  # 10..100
    # window=3 -> last 3 values: 80, 90, 100 -> mean 90
    assert recent_period_mean(history, window=3) == 90.0


def test_day_of_week_seasonal_mean_falls_back_with_too_few_same_weekday_points():
    # Only 1 historical point sharing target_date's weekday -> below
    # MIN_SAME_WEEKDAY_SAMPLE (3), so it must fall back to recent_period_mean.
    history = [(date(2026, 1, 5), 100.0), (date(2026, 1, 6), 200.0)]  # Mon, Tue
    target = date(2026, 1, 12)  # also a Monday, but only 1 Monday in history
    result = day_of_week_seasonal_mean(history, target, fallback_window=14)
    assert result == recent_period_mean(history, 14)  # fell back correctly


def test_day_of_week_seasonal_mean_uses_same_weekday_when_enough_samples():
    # 3 Mondays at 100, and 3 Tuesdays at 999 (should be ignored for a Monday target).
    history = [
        (date(2026, 1, 5), 100.0),   # Mon
        (date(2026, 1, 12), 100.0),  # Mon
        (date(2026, 1, 19), 100.0),  # Mon
        (date(2026, 1, 6), 999.0),   # Tue
        (date(2026, 1, 13), 999.0),  # Tue
        (date(2026, 1, 20), 999.0),  # Tue
    ]
    target = date(2026, 1, 26)  # Monday
    assert day_of_week_seasonal_mean(history, target, fallback_window=14) == 100.0


class TestEvaluationRegression:
    """
    Regression protection for the model-selection claim documented in
    algorithm.py's module docstring: the recent-period-mean baseline
    should continue to perform at least as well as the day-of-week
    candidate on the seeded synthetic demo dataset. If this ever fails,
    the documented selection rationale needs to be revisited — this
    test exists specifically to surface that, not to be silently
    adjusted to pass.
    """

    @staticmethod
    def _reproduce_demo_series() -> dict[tuple[str, str], list[tuple[date, float]]]:
        """
        Reproduces backend/scripts/seed_demo_data.py's exact generation
        logic (same RNG seed, same loop order) — used here purely for a
        deterministic, DB-free regression check; does not touch the
        database or that script's actual output.
        """
        import random

        rng = random.Random(42)
        location_names = ["Main Cafeteria (Demo)", "North Campus Dining (Demo)"]
        meal_type_names = ["Breakfast", "Lunch", "Dinner"]
        base_by_meal_type = {"Breakfast": 120, "Lunch": 260, "Dinner": 190}
        history_days = 60

        today = date(2026, 8, 19)  # fixed reference date for full reproducibility
        series: dict[tuple[str, str], list[tuple[date, float]]] = {}
        for day_offset in range(history_days, 0, -1):
            record_date = today - timedelta(days=day_offset)
            for location in location_names:
                for meal_type in meal_type_names:
                    base = base_by_meal_type.get(meal_type, 150)
                    quantity = round(base * rng.uniform(0.85, 1.15))
                    series.setdefault((location, meal_type), []).append((record_date, quantity))
        return series

    def test_baseline_matches_or_beats_candidate_on_synthetic_demo_data(self):
        series = self._reproduce_demo_series()
        result = evaluate_all_series(series, window=14)
        assert result is not None
        assert result.baseline_mae <= result.candidate_mae, (
            f"Baseline MAE ({result.baseline_mae:.2f}) no longer beats candidate MAE "
            f"({result.candidate_mae:.2f}) on the reference synthetic dataset — the "
            f"model-selection rationale in algorithm.py's docstring needs review."
        )


# ---------------------------------------------------------------------------
# Database-backed tests (preprocessing + API)
# ---------------------------------------------------------------------------


def _create_location_and_meal_type(client, admin_headers) -> tuple[str, str]:
    location_id = client.post(
        "/api/v1/locations", json={"name": unique_name("FcLocation")}, headers=admin_headers
    ).json()["id"]
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": unique_name("FcMealType")}, headers=admin_headers
    ).json()["id"]
    return location_id, meal_type_id


def _seed_history(db, location_id: str, meal_type_id: str, num_days: int, base_date: date) -> None:
    for i in range(num_days):
        record_date = base_date - timedelta(days=num_days - i)
        db.add(
            HistoricalConsumption(
                record_date=record_date,
                location_id=uuid.UUID(location_id),
                meal_type_id=uuid.UUID(meal_type_id),
                actual_consumed_quantity=100.0 + i,  # simple increasing series, deterministic
            )
        )
    db.commit()


def test_generate_forecast_with_sufficient_data(client, db, admin_headers, manager_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 7, 1)
    _seed_history(db, location_id, meal_type_id, num_days=20, base_date=forecast_date)

    resp = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date.isoformat(), "locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["forecastedDemand"] > 0
    assert body["locationId"] == location_id
    assert body["mealTypeId"] == meal_type_id
    assert body["forecastDate"] == forecast_date.isoformat()


def test_generate_forecast_is_idempotent_single_active_forecast(
    client, db, admin_headers, manager_headers
):
    """Calling generate again for the same period returns the existing
    forecast (200), per the single-active-forecast model, rather than
    creating a second row."""
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 7, 2)
    _seed_history(db, location_id, meal_type_id, num_days=20, base_date=forecast_date)

    payload = {
        "forecastDate": forecast_date.isoformat(),
        "locationId": location_id,
        "mealTypeId": meal_type_id,
    }
    first = client.post("/api/v1/forecasts", json=payload, headers=manager_headers)
    assert first.status_code == 201
    first_id = first.json()["id"]

    second = client.post("/api/v1/forecasts", json=payload, headers=manager_headers)
    assert second.status_code == 200
    assert second.json()["id"] == first_id  # same row, not a duplicate

    list_resp = client.get(
        "/api/v1/forecasts",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert len(list_resp.json()["data"]) == 1


def test_generate_forecast_insufficient_data_returns_422(client, db, admin_headers, manager_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 7, 3)
    _seed_history(db, location_id, meal_type_id, num_days=2, base_date=forecast_date)  # below default min (7)

    resp = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date.isoformat(), "locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["category"] == "FORECAST_UNAVAILABLE"


def test_generate_forecast_with_zero_history_returns_422(client, admin_headers, manager_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 7, 4)
    # No historical data seeded at all.
    resp = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date.isoformat(), "locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["category"] == "FORECAST_UNAVAILABLE"


def test_forecast_never_uses_data_on_or_after_forecast_date(client, db, admin_headers, manager_headers):
    """
    Data-leakage guard: seed exactly `min_historical_records_for_forecast`
    (7) valid records strictly before the forecast date, plus extra
    records ON the forecast date itself (which must be ignored).
    """
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 7, 10)

    _seed_history(db, location_id, meal_type_id, num_days=7, base_date=forecast_date)
    # Add a record on the forecast date itself with a wildly different
    # value — if leakage occurred, it would skew the result.
    db.add(
        HistoricalConsumption(
            record_date=forecast_date,
            location_id=uuid.UUID(location_id),
            meal_type_id=uuid.UUID(meal_type_id),
            actual_consumed_quantity=99999.0,
        )
    )
    db.commit()

    resp = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date.isoformat(), "locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["forecastedDemand"] < 1000  # nowhere near the leaked 99999 value


def test_get_and_list_forecasts(client, db, admin_headers, manager_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 7, 5)
    _seed_history(db, location_id, meal_type_id, num_days=10, base_date=forecast_date)

    created = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date.isoformat(), "locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    ).json()

    get_resp = client.get(f"/api/v1/forecasts/{created['id']}", headers=manager_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == created["id"]

    missing_resp = client.get(
        f"/api/v1/forecasts/{uuid.uuid4()}", headers=manager_headers
    )
    assert missing_resp.status_code == 404


def test_operations_staff_cannot_access_forecasts(client, ops_staff_headers):
    """
    Operations Staff visibility into forecasts is a "pending permission
    confirmation" cell (API Specification v1.0 Section 15) — not
    implemented, so it must be forbidden.
    """
    resp = client.get("/api/v1/forecasts", headers=ops_staff_headers)
    assert resp.status_code == 403


def test_invalid_location_reference_rejected(client, admin_headers, manager_headers):
    _, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    resp = client.post(
        "/api/v1/forecasts",
        json={
            "forecastDate": "2026-07-06",
            "locationId": "00000000-0000-0000-0000-000000000000",
            "mealTypeId": meal_type_id,
        },
        headers=manager_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["category"] == "VALIDATION_ERROR"
