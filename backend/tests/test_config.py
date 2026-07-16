import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_metrics_key() -> None:
    with pytest.raises(ValidationError, match="METRICS_API_KEY"):
        Settings(environment="production", metrics_api_key="change-me")


def test_forwarded_ip_is_used_only_when_enabled() -> None:
    forwarded = "203.0.113.10, 10.0.0.1"
    assert Settings(trust_proxy_headers=False).client_ip("127.0.0.1", forwarded) == "127.0.0.1"
    assert Settings(trust_proxy_headers=True).client_ip("127.0.0.1", forwarded) == "203.0.113.10"
