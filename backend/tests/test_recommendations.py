"""
Phase 4 tests: Rule-Based Redistribution Recommendation (REC-001..002).

Verifies the trigger point documented in
app/modules/recommendations/service.py: recommendations are generated
as a side effect of Planned Quantity create/update, only when the
resulting classification is Surplus.
"""

import uuid
from datetime import date as date_type

from app.modules.forecasting.models import ForecastedDemand
from tests.conftest import unique_name


def _create_location_and_meal_type(client, admin_headers) -> tuple[str, str]:
    location_id = client.post(
        "/api/v1/locations", json={"name": unique_name("RecLocation")}, headers=admin_headers
    ).json()["id"]
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": unique_name("RecMealType")}, headers=admin_headers
    ).json()["id"]
    return location_id, meal_type_id


def _seed_forecast(db, location_id: str, meal_type_id: str, forecast_date: str, quantity: float) -> None:
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


def test_surplus_generates_recommendation(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-06-01"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)

    create_resp = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": plan_date,
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 250,
        },
        headers=ops_staff_headers,
    )
    assert create_resp.status_code == 201

    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert list_resp.status_code == 200
    data = list_resp.json()["data"]
    assert len(data) == 1
    rec = data[0]
    assert rec["estimatedSurplusQuantity"] == 150  # 250 - 100
    assert rec["isAdvisory"] is True
    assert rec["periodDate"] == plan_date
    assert "surplus" in rec["recommendationText"].lower()

    detail_resp = client.get(f"/api/v1/recommendations/{rec['id']}", headers=manager_headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == rec["id"]


def test_shortage_does_not_generate_recommendation(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-06-02"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 200)

    client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": plan_date,
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 100,
        },
        headers=ops_staff_headers,
    )

    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert list_resp.json()["data"] == []


def test_balanced_does_not_generate_recommendation(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-06-03"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)

    client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": plan_date,
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 103,
        },
        headers=ops_staff_headers,
    )

    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    assert list_resp.json()["data"] == []


def test_recommendation_updates_idempotently_on_repeated_surplus(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    """Editing a still-Surplus Planned Quantity updates the existing
    recommendation rather than creating a duplicate."""
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-06-04"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 100)

    created = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": plan_date,
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 200,
        },
        headers=ops_staff_headers,
    ).json()

    client.patch(
        f"/api/v1/planned-quantities/{created['id']}",
        json={"quantity": 300},
        headers=ops_staff_headers,
    )

    list_resp = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    )
    data = list_resp.json()["data"]
    assert len(data) == 1  # updated in place, not duplicated
    assert data[0]["estimatedSurplusQuantity"] == 200  # 300 - 100


def test_recommendation_is_never_executed_or_routed(
    client, db, admin_headers, manager_headers, ops_staff_headers
):
    """
    Confirms the response contains no routing/logistics/execution
    fields — only advisory text and metadata (SRS-FR-027).
    """
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    plan_date = "2026-06-05"
    _seed_forecast(db, location_id, meal_type_id, plan_date, 50)
    client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": plan_date,
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 200,
        },
        headers=ops_staff_headers,
    )

    rec = client.get(
        "/api/v1/recommendations",
        params={"locationId": location_id, "mealTypeId": meal_type_id},
        headers=manager_headers,
    ).json()["data"][0]

    expected_fields = {
        "id",
        "periodDate",
        "locationId",
        "mealTypeId",
        "estimatedSurplusQuantity",
        "recommendationText",
        "secondaryLocationId",
        "isAdvisory",
        "generatedAt",
    }
    assert set(rec.keys()) == expected_fields
    assert rec["isAdvisory"] is True


def test_operations_staff_cannot_view_recommendations(client, ops_staff_headers):
    """Recommendation visibility for Operations Staff is a "pending
    permission confirmation" cell — not implemented, so it must be
    forbidden."""
    resp = client.get("/api/v1/recommendations", headers=ops_staff_headers)
    assert resp.status_code == 403
