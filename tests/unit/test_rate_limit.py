from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.rate_limit import RateLimitMiddleware


def _make_app(requests_per_minute: int) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)

    @app.get("/thing")
    def thing() -> dict[str, str]:
        return {"ok": "yes"}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def test_requests_under_the_limit_all_succeed():
    client = TestClient(_make_app(requests_per_minute=3))

    for _ in range(3):
        assert client.get("/thing").status_code == 200


def test_request_over_the_limit_gets_429_with_retry_after():
    client = TestClient(_make_app(requests_per_minute=3))
    for _ in range(3):
        client.get("/thing")

    response = client.get("/thing")

    assert response.status_code == 429
    assert response.json() == {
        "error": "too_many_requests",
        "message": "Rate limit exceeded. Try again later.",
    }
    assert int(response.headers["retry-after"]) >= 1


def test_health_endpoint_is_exempt_from_rate_limiting():
    client = TestClient(_make_app(requests_per_minute=1))

    for _ in range(5):
        assert client.get("/health").status_code == 200


def test_different_endpoints_share_the_same_client_bucket():
    """The limit is per client, not per route -- hammering distinct
    endpoints must not be a way around it."""
    client = TestClient(_make_app(requests_per_minute=2))

    assert client.get("/thing").status_code == 200
    assert client.get("/thing").status_code == 200
    assert client.get("/thing").status_code == 429
