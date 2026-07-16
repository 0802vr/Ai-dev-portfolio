from app.core.config import Settings
from app.schemas import ContactCreate
from app.services.ai import AIService


def payload() -> ContactCreate:
    return ContactCreate(name="Анна", phone="+7 900 000-00-00",
        email="anna@example.com", comment="Нужен сайт для нашей компании")

async def test_ai_fallback_without_key() -> None:
    result = await AIService(Settings(gemini_api_key=None)).analyze(payload())
    assert result.used_fallback is True
    assert result.category == "other"
    assert "Анна" in result.suggested_reply

