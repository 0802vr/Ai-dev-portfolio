import secrets

from fastapi import APIRouter, Depends, Header, Request, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import MetricsUnauthorized
from app.db import get_session
from app.repositories.contact import ContactRepository
from app.repositories.rate_limit import RateLimitRepository
from app.schemas import ContactCreate, ContactResponse, HealthResponse, MetricsResponse
from app.services.ai import AIService
from app.services.contact import ContactService
from app.services.email import EmailService

router = APIRouter()

@router.post("/contact", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(data: ContactCreate, request: Request,
                         session: AsyncSession = Depends(get_session),
                         settings: Settings = Depends(get_settings)) -> ContactResponse:
    repo = ContactRepository(session)
    service = ContactService(
        repo, RateLimitRepository(session), AIService(settings), EmailService(settings), settings
    )
    direct_ip = request.client.host if request.client else "unknown"
    ip = settings.client_ip(direct_ip, request.headers.get("X-Forwarded-For"))
    item = await service.submit(data, ip)
    return ContactResponse(id=item.id, message="Обращение принято",
        owner_delivery=item.owner_delivery, user_delivery=item.user_delivery,
        ai_used_fallback=item.ai_used_fallback, created_at=item.created_at)

@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health", response_model=HealthResponse)
@router.get("/health/ready", response_model=HealthResponse)
async def readiness(session: AsyncSession = Depends(get_session),
                 settings: Settings = Depends(get_settings)) -> HealthResponse:
    await session.execute(text("SELECT 1"))
    return HealthResponse(status="ok", database="ok", ai_configured=settings.ai_configured,
        smtp_configured=bool(settings.smtp_host and settings.smtp_username))

@router.get("/metrics", response_model=MetricsResponse)
async def metrics(x_api_key: str = Header(default=""),
                  session: AsyncSession = Depends(get_session),
                  settings: Settings = Depends(get_settings)) -> MetricsResponse:
    if not secrets.compare_digest(x_api_key, settings.metrics_api_key):
        raise MetricsUnauthorized("Неверный ключ доступа к метрикам")
    return await ContactRepository(session).metrics()
