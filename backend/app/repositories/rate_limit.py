from datetime import UTC, datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RateLimitBucket


class RateLimitRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def consume(self, ip_hash: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        now = datetime.now(UTC)
        epoch = int(now.timestamp())
        window_epoch = epoch - (epoch % window_seconds)
        window_start = datetime.fromtimestamp(window_epoch, UTC)
        statement = (
            insert(RateLimitBucket)
            .values(ip_hash=ip_hash, window_start=window_start, request_count=1)
            .on_conflict_do_update(
                constraint="uq_rate_limit_bucket",
                set_={"request_count": RateLimitBucket.request_count + 1},
            )
            .returning(RateLimitBucket.request_count)
        )
        count = int((await self.session.scalar(statement)) or 1)
        await self.session.commit()
        retry_after = window_seconds - (epoch - window_epoch)
        return count <= limit, retry_after
