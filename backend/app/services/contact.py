import hashlib

from app.core.config import Settings
from app.core.exceptions import RateLimitExceeded
from app.models import Contact
from app.repositories.contact import ContactRepository
from app.repositories.rate_limit import RateLimitRepository
from app.schemas import ContactCreate
from app.services.ai import AIService
from app.services.email import EmailService


class ContactService:
    def __init__(self, repo: ContactRepository, rate_limit: RateLimitRepository, ai: AIService,
                 email: EmailService, settings: Settings) -> None:
        self.repo, self.rate_limit = repo, rate_limit
        self.ai, self.email, self.settings = ai, email, settings

    async def submit(self, data: ContactCreate, ip: str) -> Contact:
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        allowed, retry_after = await self.rate_limit.consume(
            ip_hash, self.settings.rate_limit_requests, self.settings.rate_limit_window_seconds
        )
        if not allowed:
            raise RateLimitExceeded("Слишком много обращений. Попробуйте позже.", retry_after)
        analysis = await self.ai.analyze(data)
        item = await self.repo.create(data, ip_hash, analysis)
        owner, user, error = await self.email.notify(item)
        await self.repo.set_delivery(item, owner, user, error)
        return item
