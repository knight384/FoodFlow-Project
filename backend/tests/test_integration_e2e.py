"""
Phase 6 integration test suite: end-to-end Journeys A-G, exercising the
full Historical Data -> Forecast -> Planned Quantity -> Comparison ->
Classification -> Recommendation pipeline through the REAL API
endpoints -- not by seeding ForecastedDemand directly via ORM (the
pattern used in Phases 4/5's unit-level tests), but by actually calling
POST /forecasts and letting the real forecasting service (Phase 5)
generate it. This is the specific integration gap Phase 6 closes: no
prior test proved the real forecast-generation code path flows
correctly into comparison/classification/recommendation.

This file does NOT replace or modify the existing 52 tests (Phases
1-5) -- it is purely additive. Uses the same DB-backed fixtures as
every other Phase 4+ test file (see tests/conftest.py).
"""

import io
import uuid
from datetime import date, timedelta

from app.modules.historical_data.models import HistoricalConsumption
from tests.conftest import unique_name


def _create_location_and_meal_type(client, admin_headers) -> tuple[str, str]:
    location_id = client.post(
        "/api/v1/locations", json={"name": unique_name("E2ELocation")}, headers=admin_headers
    ).json()["id"]
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": unique_name("E2EMealType")}, headers=admin_headers
    ).json()["id"]
    return location_id, meal_type_id


def _seed_constant_history(
    db, location_id: str, meal_type_id: str, num_days: int, value: float, base_date: date
) -> None:
    """Seeds `num_days` records, all with the SAME value, strictly
    before `base_date` -- makes the resulting forecast deterministic
    (recent_period_mean of a constant series equals that constant),
    which is what lets Journeys B-E assert exact classification
    outcomes while still exercising the real forecasting code path."""
    for i in range(num_days):
        record_date = base_date - timedelta(days=num_days - i)
        db.add(
            HistoricalConsumption(
                record_date=record_date,
                location_id=uuid.UUID(location_id),
                meal_type_id=uuid.UUID(meal_type_id),
                actual_consumed_quantity=value,
            )
        )
    db.commit()


def _generate_forecast(client, headers, location_id, meal_type_id, forecast_date):
    resp = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date, "locationId": location_id, "mealTypeId": meal_type_id},
        headers=headers,
    )
    assert resp.status_code in (200, 201), resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Journey A -- Historical Data -> Forecast (via the REAL CSV upload endpoint)
# ---------------------------------------------------------------------------


def test_journey_a_historical_data_to_forecast(client, admin_headers, manager_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    location_name = client.get(f"/api/v1/locations/{location_id}", headers=admin_headers).json()["name"]
    meal_type_name = client.get(f"/api/v1/meal-types/{meal_type_id}", headers=admin_headers).json()["name"]

    forecast_date = date(2026, 8, 1)
    csv_rows = "date,location,meal_type,actual_consumed_quantity\n"
    for i in range(10):  # 10 days, above the default min-records threshold (7)
        record_date = forecast_date - timedelta(days=10 - i)
        csv_rows += f"{record_date.isoformat()},{location_name},{meal_type_name},{100 + i}\n"

    files = {"file": ("journey_a.csv", io.BytesIO(csv_rows.encode("utf-8")), "text/csv")}
    import_resp = client.post("/api/v1/historical-data/imports", files=files, headers=admin_headers)
    assert import_resp.status_code == 201
    import_id = import_resp.json()["importId"]

    detail = client.get(f"/api/v1/historical-data/imports/{import_id}", headers=admin_headers).json()
    assert detail["validRecords"] == 10
    assert detail["invalidRecords"] == 0

    forecast = _generate_forecast(client, manager_headers, location_id, meal_type_id, forecast_date.isoformat())
    assert forecast["forecastedDemand"] > 0

    retrieved = client.get(f"/api/v1/forecasts/{forecast['id']}", headers=manager_headers)
    assert retrieved.status_code == 200
    assert retrieved.json()["id"] == forecast["id"]


# ---------------------------------------------------------------------------
# Journey B -- Forecast + Planned Quantity -> Comparison
# ---------------------------------------------------------------------------


def test_journey_b_forecast_and_planned_quantity_to_comparison(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 8, 2)
    _seed_constant_history(db, location_id, meal_type_id, num_days=10, value=100.0, base_date=forecast_date)

    forecast = _generate_forecast(client, manager_headers, location_id, meal_type_id, forecast_date.isoformat())
    assert forecast["forecastedDemand"] == 100.0  # deterministic: constant history

    client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": forecast_date.isoformat(),
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 150,
        },
        headers=ops_staff_headers,
    )

    cmp_resp = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": forecast_date.isoformat()},
        headers=manager_headers,
    )
    row = cmp_resp.json()["data"][0]
    assert row["forecastedDemand"] == 100.0
    assert row["plannedQuantity"] == 150.0
    assert row["potentialSurplus"] == 50.0
    assert row["potentialShortage"] == 0.0
    assert row["variancePercentage"] == 50.0


# ---------------------------------------------------------------------------
# Journey C -- Comparison -> Classification (surplus / shortage / balanced)
# ---------------------------------------------------------------------------


def _run_classification_case(client, db, admin_headers, manager_headers, ops_staff_headers, planned_quantity, day_num):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 8, 10 + day_num)
    _seed_constant_history(db, location_id, meal_type_id, num_days=10, value=100.0, base_date=forecast_date)
    _generate_forecast(client, manager_headers, location_id, meal_type_id, forecast_date.isoformat())

    client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": forecast_date.isoformat(),
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": planned_quantity,
        },
        headers=ops_staff_headers,
    )

    cls_resp = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": forecast_date.isoformat()},
        headers=manager_headers,
    )
    return cls_resp.json()["data"][0], location_id, meal_type_id, forecast_date


def test_journey_c_classification_surplus(client, db, admin_headers, manager_headers, ops_staff_headers):
    row, *_ = _run_classification_case(client, db, admin_headers, manager_headers, ops_staff_headers, 150, 0)
    assert row["status"] == "surplus"


def test_journey_c_classification_shortage(client, db, admin_headers, manager_headers, ops_staff_headers):
    row, *_ = _run_classification_case(client, db, admin_headers, manager_headers, ops_staff_headers, 50, 1)
    assert row["status"] == "shortage"


def test_journey_c_classification_balanced(client, db, admin_headers, manager_headers, ops_staff_headers):
    row, *_ = _run_classification_case(client, db, admin_headers, manager_headers, ops_staff_headers, 103, 2)
    assert row["status"] == "balanced"


# ---------------------------------------------------------------------------
# Journey D -- Surplus -> Recommendation generated & retrieved
# ---------------------------------------------------------------------------


def test_journey_d_surplus_generates_and_retrieves_recommendation(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    row, location_id, meal_type_id, forecast_date = _run_classification_case(
        client, db, admin_headers, manager_headers, ops_staff_headers, 150, 3
    )
    assert row["status"] == "surplus"

    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    data = list_resp.json()["data"]
    assert len(data) == 1
    assert data[0]["estimatedSurplusQuantity"] == 50.0  # 150 - 100
    assert data[0]["isAdvisory"] is True

    detail_resp = client.get(f"/api/v1/recommendations/{data[0]['id']}", headers=manager_headers)
    assert detail_resp.status_code == 200


# ---------------------------------------------------------------------------
# Journey E -- Shortage/Balanced -> No recommendation
# ---------------------------------------------------------------------------


def test_journey_e_shortage_produces_no_recommendation(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    row, location_id, meal_type_id, _ = _run_classification_case(
        client, db, admin_headers, manager_headers, ops_staff_headers, 50, 4
    )
    assert row["status"] == "shortage"
    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert list_resp.json()["data"] == []


def test_journey_e_balanced_produces_no_recommendation(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    row, location_id, meal_type_id, _ = _run_classification_case(
        client, db, admin_headers, manager_headers, ops_staff_headers, 103, 5
    )
    assert row["status"] == "balanced"
    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert list_resp.json()["data"] == []


# ---------------------------------------------------------------------------
# Journey F -- Insufficient historical data
# ---------------------------------------------------------------------------


def test_journey_f_insufficient_data_forecast_unavailable_no_fabrication(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    forecast_date = date(2026, 8, 20)
    # Below the default min-records threshold (7).
    _seed_constant_history(db, location_id, meal_type_id, num_days=2, value=100.0, base_date=forecast_date)

    forecast_resp = client.post(
        "/api/v1/forecasts",
        json={"forecastDate": forecast_date.isoformat(), "locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert forecast_resp.status_code == 422
    assert forecast_resp.json()["error"]["category"] == "FORECAST_UNAVAILABLE"

    # Staff can still record a Planned Quantity even without a forecast.
    client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": forecast_date.isoformat(),
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 120,
        },
        headers=ops_staff_headers,
    )

    cmp_row = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": forecast_date.isoformat()},
        headers=manager_headers,
    ).json()["data"][0]
    assert cmp_row["forecastedDemand"] is None  # never fabricated
    assert cmp_row["plannedQuantity"] == 120.0
    assert cmp_row["potentialSurplus"] is None

    cls_row = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": forecast_date.isoformat()},
        headers=manager_headers,
    ).json()["data"][0]
    assert cls_row["status"] == "unavailable"


# ---------------------------------------------------------------------------
# Journey G -- Authorization across confirmed permissions
# ---------------------------------------------------------------------------


def test_journey_g_read_access_confirmed_roles(client, admin_headers, manager_headers):
    """Admin and Manager: confirmed read access to the forecast-adjacent pipeline."""
    for headers in (admin_headers, manager_headers):
        assert client.get("/api/v1/forecasts", headers=headers).status_code == 200
        assert client.get("/api/v1/comparisons", headers=headers).status_code == 200
        assert client.get("/api/v1/classifications", headers=headers).status_code == 200
        assert client.get("/api/v1/recommendations", headers=headers).status_code == 200
        assert client.get("/api/v1/dashboard", headers=headers).status_code == 200
        assert (
            client.get(
                "/api/v1/reports",
                params={"dateFrom": "2026-01-01", "dateTo": "2026-01-31"},
                headers=headers,
            ).status_code
            == 200
        )


def test_journey_g_operations_staff_forbidden_from_pending_cells(client, ops_staff_headers):
    """
    Operations Staff: confirmed FORBIDDEN from the forecast-adjacent
    pipeline (pending permission confirmation cells -- not silently
    granted).
    """
    checks = [
        ("/api/v1/forecasts", None),
        ("/api/v1/comparisons", None),
        ("/api/v1/classifications", None),
        ("/api/v1/recommendations", None),
        ("/api/v1/dashboard", None),
        ("/api/v1/reports", {"dateFrom": "2026-01-01", "dateTo": "2026-01-31"}),
    ]
    for path, params in checks:
        resp = client.get(path, params=params, headers=ops_staff_headers)
        assert resp.status_code == 403, f"{path} should be forbidden for Operations Staff"


def test_journey_g_planned_quantity_permission_matrix(
    client, admin_headers, manager_headers, ops_staff_headers
):
    """
    Operations Staff: confirmed ALLOWED to create Planned Quantity.
    Admin/Manager: confirmed NOT allowed (pending-confirmation cell,
    not implemented -- this test protects against that cell ever being
    silently granted without an explicit decision).
    """
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    payload = {
        "planDate": "2026-08-25",
        "locationId": location_id,
        "mealTypeId": meal_type_id,
        "quantity": 100,
    }

    assert client.post("/api/v1/planned-quantities", json=payload, headers=admin_headers).status_code == 403
    assert client.post("/api/v1/planned-quantities", json=payload, headers=manager_headers).status_code == 403
    assert client.post("/api/v1/planned-quantities", json=payload, headers=ops_staff_headers).status_code == 201
