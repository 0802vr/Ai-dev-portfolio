import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DeliveryStatus(enum.StrEnum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    skipped = "skipped"


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80))
    phone: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(254), index=True)
    comment: Mapped[str] = mapped_column(Text)
    ip_hash: Mapped[str] = mapped_column(String(64), index=True)
    ai_category: Mapped[str] = mapped_column(String(40), default="other")
    ai_sentiment: Mapped[str] = mapped_column(String(20), default="neutral")
    ai_priority: Mapped[str] = mapped_column(String(20), default="medium")
    ai_summary: Mapped[str] = mapped_column(String(300), default="")
    ai_reply: Mapped[str] = mapped_column(Text, default="")
    ai_used_fallback: Mapped[bool] = mapped_column(default=True)
    owner_delivery: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), default=DeliveryStatus.pending
    )
    user_delivery: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus), default=DeliveryStatus.pending
    )
    delivery_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )


class RateLimitBucket(Base):
    __tablename__ = "rate_limit_buckets"
    __table_args__ = (
        UniqueConstraint("ip_hash", "window_start", name="uq_rate_limit_bucket"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip_hash: Mapped[str] = mapped_column(String(64), index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    request_count: Mapped[int] = mapped_column(Integer, default=1)
