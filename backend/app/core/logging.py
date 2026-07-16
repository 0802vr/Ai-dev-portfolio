import logging
import logging.handlers
from pathlib import Path

from pythonjsonlogger.json import JsonFormatter


def configure_logging(log_file: str) -> None:
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        path, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
    root.addHandler(logging.StreamHandler())
