"""
Phase 4 tests: Location management (LOC-001..005).

Requires a live database — see tests/conftest.py's module docstring for
the testing-approach trade-off.
"""

from tests.conftest import collection_contains_id, unique_name


def test_admin_can_create_list_retrieve_update_location(client, admin_headers):
    name = unique_name("Location")

    create_resp = client.post("/api/v1/locations", json={"name": name}, headers=admin_headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == name
    assert created["isActive"] is True
    location_id = created["id"]

    get_resp = client.get(f"/api/v1/locations/{location_id}", headers=admin_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == location_id

    list_resp = client.get("/api/v1/locations", headers=admin_headers)
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert "pagination" in body
    # See tests/conftest.py's collection_contains_id docstring: the
    # default page may not contain this item once accumulated rows in
    # the shared dev DB exceed one page — search the whole collection,
    # not just the arbitrary first page, per documented pagination
    # semantics (API Specification v1.0 Section 22).
    assert collection_contains_id(client, "/api/v1/locations", admin_headers, location_id)

    new_name = unique_name("LocationRenamed")
    patch_resp = client.patch(
        f"/api/v1/locations/{location_id}", json={"name": new_name}, headers=admin_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == new_name


def test_create_location_duplicate_name_returns_409(client, admin_headers):
    name = unique_name("Duplicate")
    first = client.post("/api/v1/locations", json={"name": name}, headers=admin_headers)
    assert first.status_code == 201

    second = client.post("/api/v1/locations", json={"name": name}, headers=admin_headers)
    assert second.status_code == 409
    assert second.json()["error"]["category"] == "DUPLICATE_RESOURCE"


def test_create_location_empty_name_returns_validation_error(client, admin_headers):
    resp = client.post("/api/v1/locations", json={"name": ""}, headers=admin_headers)
    assert resp.status_code == 422
    assert resp.json()["error"]["category"] == "VALIDATION_ERROR"


def test_non_admin_cannot_create_location(client, manager_headers):
    resp = client.post(
        "/api/v1/locations", json={"name": unique_name("Forbidden")}, headers=manager_headers
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["category"] == "FORBIDDEN"


def test_delete_location_archives_it_safely(client, admin_headers):
    """
    Verifies the PROVISIONAL soft-archive delete behavior (see
    app/modules/locations/service.py's module docstring): DELETE sets
    isActive=false rather than physically removing the row, so
    referential/historical integrity is preserved.
    """
    name = unique_name("ToArchive")
    create_resp = client.post("/api/v1/locations", json={"name": name}, headers=admin_headers)
    location_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/locations/{location_id}", headers=admin_headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["isActive"] is False

    # The archived location is excluded from the default (active-only) list...
    # (searches the whole collection — see conftest.collection_contains_id's
    # docstring for why an unfiltered single-page check is not reliable
    # against a shared, accumulating dev database)
    assert not collection_contains_id(client, "/api/v1/locations", admin_headers, location_id)

    # ...but still directly retrievable (its history is preserved, not deleted).
    get_resp = client.get(f"/api/v1/locations/{location_id}", headers=admin_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["isActive"] is False

    # ...and visible again with includeInactive=true.
    assert collection_contains_id(
        client, "/api/v1/locations", admin_headers, location_id, params={"includeInactive": "true"}
    )
