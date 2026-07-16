import hashlib

from app.core.config import Settings
from app.core.exceptions import RateLimitExceeded
from app.models import Contact
from app.repositories.contact import ContactRepository
from app.schemas import ContactCreate
from app.services.ai import AIService
from app.services.email import EmailService


class ContactService:
    def __init__(self, repo: ContactRepository, ai: AIService,
                 email: EmailService, settings: Settings) -> None:
        self.repo, self.ai, self.email, self.settings = repo, ai, email, settings

    async def submit(self, data: ContactCreate, ip: str) -> Contact:
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()
        count = await self.repo.count_recent_by_ip(ip_hash, self.settings.rate_limit_window_seconds)
        if count >= self.settings.rate_limit_requests:
            raise RateLimitExceeded("Слишком много обращений. Попробуйте позже.")
        analysis = await self.ai.analyze(data)
        item = await self.repo.create(data, ip_hash, analysis)
        owner, user, error = await self.email.notify(item)
        await self.repo.set_delivery(item, owner, user, error)
        return item

