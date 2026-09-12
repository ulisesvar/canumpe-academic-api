from app.auth.api_key import generate_api_key

ENDPOINT = "/api/v1/me/courses"

EXPECTED_FIELDS = {"course_id", "short_name", "full_name", "start_date", "end_date", "visible"}


def test_valid_api_key_returns_200_with_expected_schema(client, issue_api_key):
    key = issue_api_key("A0001")

    response = client.get(ENDPOINT, headers={"Authorization": f"Bearer {key}"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert EXPECTED_FIELDS <= set(body[0].keys())


def test_missing_api_key_returns_401(client):
    response = client.get(ENDPOINT)

    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized", "message": "Invalid or missing API key"}


def test_malformed_api_key_returns_401(client):
    response = client.get(ENDPOINT, headers={"Authorization": "Bearer not-a-real-key"})

    assert response.status_code == 401


def test_unknown_api_key_returns_401(client):
    plaintext, _, _ = generate_api_key()

    response = client.get(ENDPOINT, headers={"Authorization": f"Bearer {plaintext}"})

    assert response.status_code == 401


def test_revoked_api_key_returns_401(client, issue_api_key):
    key = issue_api_key("A0001", revoked=True)

    response = client.get(ENDPOINT, headers={"Authorization": f"Bearer {key}"})

    assert response.status_code == 401


def test_student_absent_from_moodle_gets_empty_list(client, issue_api_key):
    key = issue_api_key("NOT-REGISTERED-IN-MOODLE")

    response = client.get(ENDPOINT, headers={"Authorization": f"Bearer {key}"})

    assert response.status_code == 200
    assert response.json() == []


def test_active_enrolment_outside_canumpe_scope_is_not_returned(client, issue_api_key):
    """Bob (A0002) is actively enrolled in a real Moodle course, just not
    the one CANUMPE currently serves -- the API must not leak it."""
    key = issue_api_key("A0002")

    response = client.get(ENDPOINT, headers={"Authorization": f"Bearer {key}"})

    assert response.status_code == 200
    assert response.json() == []


def test_student_a_can_never_see_student_bs_courses(client, issue_api_key):
    key_a = issue_api_key("A0001")
    key_b = issue_api_key("A0002")

    body_a = client.get(ENDPOINT, headers={"Authorization": f"Bearer {key_a}"}).json()
    body_b = client.get(ENDPOINT, headers={"Authorization": f"Bearer {key_b}"}).json()

    assert {c["course_id"] for c in body_a} == {10}
    assert body_b == []


def test_duplicate_moodle_account_number_returns_500_without_leaking_details(issue_api_key):
    """Two non-deleted Moodle users share account number A0009 in the
    fixture -- the API must fail safely rather than arbitrarily returning
    one of them."""
    from fastapi.testclient import TestClient

    from app.main import app

    key = issue_api_key("A0009")

    with TestClient(app, raise_server_exceptions=False) as broken_client:
        response = broken_client.get(ENDPOINT, headers={"Authorization": f"Bearer {key}"})

    assert response.status_code == 500
    body = response.json()
    assert body == {"error": "internal_error", "message": "An unexpected error occurred"}
    assert "A0009" not in response.text


def test_moodle_source_failure_returns_500_without_leaking_details(
    api_db, issue_api_key, monkeypatch
):
    from fastapi.testclient import TestClient

    from app.main import app
    from app.services import course_service

    key = issue_api_key("A0001")

    def boom(*args, **kwargs):
        raise RuntimeError("simulated moodle database outage")

    monkeypatch.setattr(course_service, "get_my_courses", boom)

    with TestClient(app, raise_server_exceptions=False) as broken_client:
        response = broken_client.get(ENDPOINT, headers={"Authorization": f"Bearer {key}"})

    assert response.status_code == 500
    body = response.json()
    assert body == {"error": "internal_error", "message": "An unexpected error occurred"}
    assert "simulated" not in response.text
