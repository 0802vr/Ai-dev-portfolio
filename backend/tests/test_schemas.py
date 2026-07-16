import pytest
from pydantic import ValidationError

from app.schemas import ContactCreate


def test_valid_contact() -> None:
    item = ContactCreate(name="Иван", phone="+7 (999) 123-45-67", email="ivan@example.com",
                         comment="Хочу обсудить разработку сервиса")
    assert item.email == "ivan@example.com"

@pytest.mark.parametrize("phone", ["123", "call-me", "+7<script>"])
def test_invalid_phone(phone: str) -> None:
    with pytest.raises(ValidationError):
        ContactCreate(name="Иван", phone=phone, email="ivan@example.com",
                      comment="Достаточно длинный комментарий")

def test_short_comment_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ContactCreate(name="Иван", phone="+79991234567", email="ivan@example.com", comment="Коротко")
