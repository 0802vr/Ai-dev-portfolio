class ApplicationError(Exception):
    status_code = 500
    code = "application_error"

    def __init__(self, message: str, headers: dict[str, str] | None = None) -> None:
        self.message = message
        self.headers = headers or {}
        super().__init__(message)


class RateLimitExceeded(ApplicationError):
    status_code = 429
    code = "rate_limit_exceeded"

    def __init__(self, message: str, retry_after: int) -> None:
        super().__init__(message, {"Retry-After": str(retry_after)})


class MetricsUnauthorized(ApplicationError):
    status_code = 401
    code = "metrics_unauthorized"
