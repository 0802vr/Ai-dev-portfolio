from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contact, DeliveryStatus
from app.schemas import AIAnalysis, ContactCreate, MetricsResponse


class ContactRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_recent_by_ip(self, ip_hash: str, seconds: int) -> int:
        since = datetime.now(UTC) - timedelta(seconds=seconds)
        value = await self.session.scalar(select(func.count(Contact.id)).where(
            Contact.ip_hash == ip_hash, Contact.created_at >= since))
        return int(value or 0)

    async def create(self, data: ContactCreate, ip_hash: str, ai: AIAnalysis) -> Contact:
        item = Contact(**data.model_dump(), ip_hash=ip_hash, ai_category=ai.category,
            ai_sentiment=ai.sentiment, ai_priority=ai.priority, ai_summary=ai.summary,
            ai_reply=ai.suggested_reply, ai_used_fallback=ai.used_fallback)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def set_delivery(self, item: Contact, owner: DeliveryStatus,
                           user: DeliveryStatus, error: str | None) -> None:
        item.owner_delivery, item.user_delivery = owner, user
        item.delivery_error = error[:1000] if error else None
        await self.session.commit()

    async def metrics(self) -> MetricsResponse:
        today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        row = (await self.session.execute(select(func.count(Contact.id),
            func.sum(case((Contact.created_at >= today, 1), else_=0)),
            func.sum(case((Contact.ai_used_fallback.is_(True), 1), else_=0)),
            func.sum(case((or_(Contact.owner_delivery == DeliveryStatus.failed,
                Contact.user_delivery == DeliveryStatus.failed), 1), else_=0))))).one()
        return MetricsResponse(total_contacts=int(row[0] or 0), contacts_today=int(row[1] or 0),
            ai_fallbacks=int(row[2] or 0), failed_notifications=int(row[3] or 0))

