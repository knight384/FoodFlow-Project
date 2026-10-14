"""
Phase 4 tests: Dynamic Comparison (CMP-001) and Dynamic Classification
(CLS-001).

=== Controlled test/demo Forecasted Demand data ===
No forecasting endpoint exists yet (Phase 5). Per this phase's explicit
instruction ("For local testing only, controlled Forecasted Demand
records may be used as explicitly labeled demo/test data. Do NOT
generate fake ML predictions."), these tests insert ForecastedDemand
rows directly via the ORM with fixed, hand-picked values — never through
any prediction logic — solely to exercise the comparison/classification
computation against known inputs.

=== Provisional threshold ===
The default provisional classification threshold is 10% (see
app/config.py and app/modules/classification/service.py's module
docstring) unless CLASSIFICATION_THRESHOLD_PERCENTAGE is overridden in
the test environment. These tests assert against that 10% default.
"""

import uuid

from app.modules.forecasting.models import ForecastedDemand
from tests.conftest import unique_name


def _create_location_and_meal_type(client, admin_headers) -> tuple[str, str]:
    location_id = client.post(
        "/api/v1/locations", json={"name": unique_name("CmpLocation")}, headers=admin_headers
    ).json()["id"]
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": unique_name("CmpMealType")}, headers=admin_headers
    ).json()["id"]
    return location_id, meal_type_id


def _seed_forecast(db, location_id: str, meal_type_id: str, forecast_date: str, quantity: float) -> None:
    from datetime import date as date_type

    db.add(
        ForecastedDemand(
            forecast_date=date_type.fromisoformat(forecast_date),
            location_id=uuid.UUID(location_id),
            meal_type_id=uuid.UUID(meal_type_id),
            predicted_quantity=quantity,
            model_version="test-fixture-not-ml",
        )
    )
    db.commit()


def _create_planned_quantity(client, headers, plan_date, location_id, meal_type_id, quantity):
    resp = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": plan_date,
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": quantity,
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_comparison_and_classification_surplus(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-01"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)
    _create_planned_quantity(client, ops_staff_headers, plan_date, location_id, meal_type_id, 200)

    cmp_resp = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    )
    assert cmp_resp.status_code == 200
    row = cmp_resp.json()["data"][0]
    assert row["forecastedDemand"] == 100
    assert row["plannedQuantity"] == 200
    assert row["potentialSurplus"] == 100
    assert row["potentialShortage"] == 0
    assert row["variancePercentage"] == 100.0

    cls_resp = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    )
    assert cls_resp.status_code == 200
    cls_row = cls_resp.json()["data"][0]
    assert cls_row["status"] == "surplus"
    assert cls_row["thresholdApplied"] == 10.0


def test_comparison_and_classification_shortage(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-02"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 200)
    _create_planned_quantity(client, ops_staff_headers, plan_date, location_id, meal_type_id, 100)

    cmp_row = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert cmp_row["potentialShortage"] == 100
    assert cmp_row["potentialSurplus"] == 0

    cls_row = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert cls_row["status"] == "shortage"


def test_classification_balanced(client, db, admin_headers, manager_headers, ops_staff_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-03"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)
    _create_planned_quantity(client, ops_staff_headers, plan_date, location_id, meal_type_id, 105)

    cls_row = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert cls_row["status"] == "balanced"


def test_classification_threshold_boundary(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    """At exactly the threshold (10%), the period is Balanced, not Surplus —
    the comparison uses a strict `>` (not `>=`) per
    app/modules/classification/service.py."""
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)

    plan_date_at = "2026-05-04"
    _seed_forecast(db, location_id, meal_type_id, plan_date_at, 100)
    _create_planned_quantity(client, ops_staff_headers, plan_date_at, location_id, meal_type_id, 110)
    at_boundary = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date_at},
        headers=manager_headers,
    ).json()["data"][0]
    assert at_boundary["status"] == "balanced"

    plan_date_over = "2026-05-05"
    _seed_forecast(db, location_id, meal_type_id, plan_date_over, 100)
    _create_planned_quantity(client, ops_staff_headers, plan_date_over, location_id, meal_type_id, 111)
    over_boundary = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date_over},
        headers=manager_headers,
    ).json()["data"][0]
    assert over_boundary["status"] == "surplus"


def test_comparison_missing_forecast(client, db, admin_headers, manager_headers, ops_staff_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-06"
    _create_planned_quantity(client, ops_staff_headers, plan_date, location_id, meal_type_id, 150)

    row = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert row["forecastedDemand"] is None
    assert row["plannedQuantity"] == 150
    assert row["potentialSurplus"] is None
    assert row["potentialShortage"] is None
    assert row["variancePercentage"] is None

    cls_row = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert cls_row["status"] == "unavailable"


def test_comparison_missing_planned_quantity(client, db, admin_headers, manager_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-07"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)

    row = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert row["forecastedDemand"] == 100
    assert row["plannedQuantity"] is None
    assert row["potentialSurplus"] is None


def test_zero_forecast_edge_case_does_not_produce_infinity_or_error(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-08"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 0)
    _create_planned_quantity(client, ops_staff_headers, plan_date, location_id, meal_type_id, 50)

    row = client.get(
        "/api/v1/comparisons",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert row["forecastedDemand"] == 0
    assert row["variancePercentage"] is None  # never infinity, never a crash

    cls_row = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert cls_row["status"] == "unavailable"


def test_dynamic_recalculation_reflects_updated_planned_quantity(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    """Confirms comparison is computed fresh on every request — no
    stale/cached value survives an update to Planned Quantity."""
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-05-09"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)
    created = _create_planned_quantity(
        client, ops_staff_headers, plan_date, location_id, meal_type_id, 200
    )

    first = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert first["status"] == "surplus"

    client.patch(
        f"/api/v1/planned-quantities/{created['id']}",
        json={"quantity": 102},
        headers=ops_staff_headers,
    )

    second = client.get(
        "/api/v1/classifications",
        params={"locationId": location_id, "mealTypeId": meal_type_id, "date": plan_date},
        headers=manager_headers,
    ).json()["data"][0]
    assert second["status"] == "balanced"


def test_operations_staff_cannot_view_comparisons_or_classifications(
    client, ops_staff_headers
):
    """
    Operations Staff visibility into comparisons/classifications is not
    one of the explicitly confirmed permissions (API Specification v1.0
    authorizes only Manager/Admin for CMP-001/CLS-001) — so it must be
    forbidden, not silently allowed.
    """
    cmp_resp = client.get("/api/v1/comparisons", headers=ops_staff_headers)
    assert cmp_resp.status_code == 403

    cls_resp = client.get("/api/v1/classifications", headers=ops_staff_headers)
    assert cls_resp.status_code == 403
