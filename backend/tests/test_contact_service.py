from unittest.mock import AsyncMock

import pytest

from app.core.config import Settings
from app.core.exceptions import RateLimitExceeded
from app.schemas import ContactCreate
from app.services.contact import ContactService


def payload() -> ContactCreate:
    return ContactCreate(name="Анна", phone="+79990000000", email="anna@example.com",
                         comment="Нужен новый корпоративный сайт")

async def test_rate_limit_stops_before_ai() -> None:
    repo, rate_limit, ai, email = AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()
    rate_limit.consume.return_value = (False, 120)
    service = ContactService(repo, rate_limit, ai, email, Settings(rate_limit_requests=5))
    with pytest.raises(RateLimitExceeded):
        await service.submit(payload(), "127.0.0.1")
    ai.analyze.assert_not_awaited()
