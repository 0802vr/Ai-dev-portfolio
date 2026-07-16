import re
import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import DeliveryStatus


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    phone: str = Field(min_length=7, max_length=30)
    email: EmailStr
    comment: str = Field(min_length=10, max_length=3000)

    @field_validator("name", "comment")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        digits = re.sub(r"\D", "", value)
        if not 7 <= len(digits) <= 15 or not re.fullmatch(r"[\d\s()+-]+", value):
            raise ValueError("Некорректный номер телефона")
        return value


class AIAnalysis(BaseModel):
    category: Literal["website", "mobile", "consulting", "ai", "support", "other"]
    sentiment: Literal["positive", "neutral", "negative"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(max_length=300)
    suggested_reply: str = Field(max_length=1500)
    used_fallback: bool = False


class ContactResponse(BaseModel):
    id: uuid.UUID
    message: str
    owner_delivery: DeliveryStatus
    user_delivery: DeliveryStatus
    ai_used_fallback: bool
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    database: str
    ai_configured: bool
    smtp_configured: bool


class MetricsResponse(BaseModel):
    total_contacts: int
    contacts_today: int
    ai_fallbacks: int
    failed_notifications: int
