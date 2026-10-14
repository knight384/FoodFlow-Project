"""
Phase 4 tests: Meal-type management (MEAL-001..005). Mirrors
test_locations.py's pattern (same underlying service design) at lighter
coverage, since the two modules are structurally identical.
"""

from tests.conftest import collection_contains_id, unique_name


def test_admin_can_create_list_retrieve_update_meal_type(client, admin_headers):
    name = unique_name("MealType")

    create_resp = client.post("/api/v1/meal-types", json={"name": name}, headers=admin_headers)
    assert create_resp.status_code == 201
    meal_type_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/v1/meal-types/{meal_type_id}", headers=admin_headers)
    assert get_resp.status_code == 200

    new_name = unique_name("MealTypeRenamed")
    patch_resp = client.patch(
        f"/api/v1/meal-types/{meal_type_id}", json={"name": new_name}, headers=admin_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == new_name

    list_resp = client.get("/api/v1/meal-types", headers=admin_headers)
    assert list_resp.status_code == 200
    # See tests/conftest.py's collection_contains_id docstring: search
    # the whole collection, not just the arbitrary default first page.
    assert collection_contains_id(client, "/api/v1/meal-types", admin_headers, meal_type_id)


def test_create_meal_type_duplicate_name_returns_409(client, admin_headers):
    name = unique_name("DuplicateMeal")
    assert client.post("/api/v1/meal-types", json={"name": name}, headers=admin_headers).status_code == 201
    second = client.post("/api/v1/meal-types", json={"name": name}, headers=admin_headers)
    assert second.status_code == 409


def test_create_meal_type_empty_name_returns_validation_error(client, admin_headers):
    resp = client.post("/api/v1/meal-types", json={"name": ""}, headers=admin_headers)
    assert resp.status_code == 422


def test_delete_meal_type_archives_it_safely(client, admin_headers):
    name = unique_name("MealToArchive")
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": name}, headers=admin_headers
    ).json()["id"]

    delete_resp = client.delete(f"/api/v1/meal-types/{meal_type_id}", headers=admin_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["isActive"] is False
