"""
Phase 4 tests: Planned Quantity management (PQ-001..004).
"""

from tests.conftest import unique_name


def _create_location_and_meal_type(client, admin_headers) -> tuple[str, str]:
    location_id = client.post(
        "/api/v1/locations", json={"name": unique_name("PQLocation")}, headers=admin_headers
    ).json()["id"]
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": unique_name("PQMealType")}, headers=admin_headers
    ).json()["id"]
    return location_id, meal_type_id


def test_ops_staff_can_create_retrieve_list_update_planned_quantity(
    client, admin_headers, ops_staff_headers
):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)

    create_resp = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": "2026-04-01",
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 200,
        },
        headers=ops_staff_headers,
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["quantity"] == 200
    assert created["locationId"] == location_id
    pq_id = created["id"]

    get_resp = client.get(f"/api/v1/planned-quantities/{pq_id}", headers=ops_staff_headers)
    assert get_resp.status_code == 200

    list_resp = client.get(
        "/api/v1/planned-quantities", params={"locationId": location_id}, headers=ops_staff_headers
    )
    assert list_resp.status_code == 200
    assert any(pq["id"] == pq_id for pq in list_resp.json()["data"])

    patch_resp = client.patch(
        f"/api/v1/planned-quantities/{pq_id}", json={"quantity": 250}, headers=ops_staff_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["quantity"] == 250


def test_negative_quantity_rejected(client, admin_headers, ops_staff_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    resp = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": "2026-04-02",
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": -10,
        },
        headers=ops_staff_headers,
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["category"] == "VALIDATION_ERROR"


def test_invalid_location_reference_rejected(client, admin_headers, ops_staff_headers):
    _, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    resp = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": "2026-04-03",
            "locationId": "00000000-0000-0000-0000-000000000000",
            "mealTypeId": meal_type_id,
            "quantity": 100,
        },
        headers=ops_staff_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["category"] == "VALIDATION_ERROR"


def test_duplicate_planned_quantity_returns_409(client, admin_headers, ops_staff_headers):
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    payload = {
        "planDate": "2026-04-04",
        "locationId": location_id,
        "mealTypeId": meal_type_id,
        "quantity": 100,
    }
    first = client.post("/api/v1/planned-quantities", json=payload, headers=ops_staff_headers)
    assert first.status_code == 201
    second = client.post("/api/v1/planned-quantities", json=payload, headers=ops_staff_headers)
    assert second.status_code == 409
    assert second.json()["error"]["category"] == "DUPLICATE_RESOURCE"


def test_admin_cannot_create_planned_quantity(client, admin_headers):
    """
    Admin ability to enter Planned Quantity is an unresolved permission
    cell (SRS/PRD/API Spec) and is therefore NOT implemented — only
    Operations Staff (the confirmed role) may create/edit.
    """
    location_id, meal_type_id = _create_location_and_meal_type(client, admin_headers)
    resp = client.post(
        "/api/v1/planned-quantities",
        json={
            "planDate": "2026-04-05",
            "locationId": location_id,
            "mealTypeId": meal_type_id,
            "quantity": 100,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 403
