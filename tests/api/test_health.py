def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_reports_both_databases_ok_when_reachable(client):
    response = client.get("/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["api_db"] == "ok"
    assert body["attendance_db"] == "ok"
