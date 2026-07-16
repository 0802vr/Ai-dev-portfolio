class ApplicationError(Exception):
    status_code = 500
    code = "application_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class RateLimitExceeded(ApplicationError):
    status_code = 429
    code = "rate_limit_exceeded"


class MetricsUnauthorized(ApplicationError):
    status_code = 401
    code = "metrics_unauthorized"

