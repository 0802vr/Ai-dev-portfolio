from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.db import get_session
from app.main import app


async def fake_session() -> AsyncIterator[AsyncMock]:
    yield AsyncMock()


def override_settings() -> Settings:
    return Settings(metrics_api_key="a-strong-test-key", gemini_api_key=None)


app.dependency_overrides[get_session] = fake_session
app.dependency_overrides[get_settings] = override_settings
client = TestClient(app)


def test_liveness_and_request_id() -> None:
    response = client.get("/api/health/live", headers={"X-Request-ID": "test-request"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "test-request"


def test_validation_error_has_safe_shape_and_request_id() -> None:
    response = client.post(
        "/api/contact",
        headers={"X-Request-ID": "validation-request"},
        json={"name": "A", "phone": "bad", "email": "bad", "comment": "short"},
    )
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["request_id"] == "validation-request"
    assert error["details"]


def test_metrics_rejects_wrong_key() -> None:
    response = client.get("/api/metrics", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "metrics_unauthorized"
