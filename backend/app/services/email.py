import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import Settings
from app.models import Contact, DeliveryStatus

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def configured(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_username)

    def _send(self, recipient: str, subject: str, text: str) -> None:
        message = EmailMessage()
        message["From"], message["To"], message["Subject"] = self.settings.smtp_from_email, recipient, subject
        message.set_content(text)
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=10) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.send_message(message)

    async def notify(self, item: Contact) -> tuple[DeliveryStatus, DeliveryStatus, str | None]:
        if not self.configured:
            return DeliveryStatus.skipped, DeliveryStatus.skipped, "SMTP is not configured"
        owner = user = DeliveryStatus.sent
        errors: list[str] = []
        owner_text = (f"Новая заявка от {item.name}\nEmail: {item.email}\nТелефон: {item.phone}\n\n"
            f"{item.comment}\n\nAI: {item.ai_category} / {item.ai_sentiment} / {item.ai_priority}\n"
            f"Кратко: {item.ai_summary}")
        try:
            await asyncio.to_thread(self._send, self.settings.owner_email,
                                    f"Новая заявка: {item.ai_category}", owner_text)
        except Exception as exc:
            logger.exception("Owner email failed")
            owner, errors = DeliveryStatus.failed, [f"owner:{type(exc).__name__}"]
        try:
            await asyncio.to_thread(self._send, item.email, "Обращение получено", item.ai_reply)
        except Exception as exc:
            logger.exception("User email failed")
            user, errors = DeliveryStatus.failed, errors + [f"user:{type(exc).__name__}"]
        return owner, user, ",".join(errors) or None

