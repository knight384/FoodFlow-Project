"""
Phase 4 tests: Historical Data import/validation (HIST-001..003).
"""

import io

from tests.conftest import unique_name


def _create_location_and_meal_type(client, admin_headers) -> tuple[str, str]:
    location_name = unique_name("HistLocation")
    meal_type_name = unique_name("HistMealType")
    location_id = client.post(
        "/api/v1/locations", json={"name": location_name}, headers=admin_headers
    ).json()["id"]
    meal_type_id = client.post(
        "/api/v1/meal-types", json={"name": meal_type_name}, headers=admin_headers
    ).json()["id"]
    return location_name, meal_type_name


def _upload(client, admin_headers, csv_text: str):
    files = {"file": ("historical.csv", io.BytesIO(csv_text.encode("utf-8")), "text/csv")}
    return client.post("/api/v1/historical-data/imports", files=files, headers=admin_headers)


def test_valid_import_all_rows_valid(client, admin_headers):
    location_name, meal_type_name = _create_location_and_meal_type(client, admin_headers)
    csv_text = (
        "date,location,meal_type,actual_consumed_quantity\n"
        f"2026-01-01,{location_name},{meal_type_name},100\n"
        f"2026-01-02,{location_name},{meal_type_name},110\n"
    )
    resp = _upload(client, admin_headers, csv_text)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "completed"
    import_id = body["importId"]

    detail_resp = client.get(f"/api/v1/historical-data/imports/{import_id}", headers=admin_headers)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["totalRecords"] == 2
    assert detail["validRecords"] == 2
    assert detail["invalidRecords"] == 0
    assert detail["errors"] == []


def test_import_with_mixed_valid_and_invalid_rows_preserves_valid_rows(client, admin_headers):
    """Transaction integrity: valid rows must not be lost because other rows are invalid."""
    location_name, meal_type_name = _create_location_and_meal_type(client, admin_headers)
    csv_text = (
        "date,location,meal_type,actual_consumed_quantity\n"
        f"2026-02-01,{location_name},{meal_type_name},100\n"  # valid
        f"not-a-date,{location_name},{meal_type_name},100\n"  # invalid date
        f"2026-02-03,{location_name},{meal_type_name},-5\n"  # negative quantity
        f"2026-02-04,Nonexistent Location XYZ,{meal_type_name},100\n"  # invalid location
        f"2026-02-05,{location_name},Nonexistent Meal XYZ,100\n"  # invalid meal type
        f"2026-02-06,{location_name},{meal_type_name},not-a-number\n"  # non-numeric quantity
        f",{location_name},{meal_type_name},100\n"  # missing date
        f"2026-02-08,{location_name},{meal_type_name},120\n"  # valid
    )
    resp = _upload(client, admin_headers, csv_text)
    assert resp.status_code == 201
    import_id = resp.json()["importId"]

    detail = client.get(f"/api/v1/historical-data/imports/{import_id}", headers=admin_headers).json()
    assert detail["totalRecords"] == 8
    assert detail["validRecords"] == 2
    assert detail["invalidRecords"] == 6
    assert len(detail["errors"]) == 6

    reasons = " ".join(e["failureReason"] for e in detail["errors"]).lower()
    assert "invalid date" in reasons
    assert ">= 0" in reasons or "negative" in reasons or "must be" in reasons
    assert "unrecognized location" in reasons
    assert "unrecognized meal type" in reasons
    assert "not numeric" in reasons
    assert "missing required field" in reasons


def test_import_missing_required_column_fails_cleanly(client, admin_headers):
    csv_text = "date,location,actual_consumed_quantity\n2026-01-01,SomeLocation,100\n"
    resp = _upload(client, admin_headers, csv_text)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "failed"

    detail = client.get(
        f"/api/v1/historical-data/imports/{body['importId']}", headers=admin_headers
    ).json()
    assert detail["totalRecords"] == 0
    assert len(detail["errors"]) == 1
    assert "missing required column" in detail["errors"][0]["failureReason"].lower()


def test_list_import_jobs(client, admin_headers):
    location_name, meal_type_name = _create_location_and_meal_type(client, admin_headers)
    csv_text = (
        "date,location,meal_type,actual_consumed_quantity\n"
        f"2026-03-01,{location_name},{meal_type_name},50\n"
    )
    _upload(client, admin_headers, csv_text)

    list_resp = client.get("/api/v1/historical-data/imports", headers=admin_headers)
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert "data" in body and "pagination" in body
    assert len(body["data"]) >= 1


def test_non_admin_cannot_upload_historical_data(client, ops_staff_headers):
    files = {"file": ("x.csv", io.BytesIO(b"date,location,meal_type,actual_consumed_quantity\n"), "text/csv")}
    resp = client.post("/api/v1/historical-data/imports", files=files, headers=ops_staff_headers)
    assert resp.status_code == 403
