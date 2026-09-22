"""Logging basico a consola + archivo."""
import logging
from logging.handlers import RotatingFileHandler

from config import LOG_DIR

_configured = False


def get_logger(name: str) -> logging.Logger:
    global _configured
    if not _configured:
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        console = logging.StreamHandler()
        console.setFormatter(fmt)

        fileh = RotatingFileHandler(
            LOG_DIR / "app.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
        )
        fileh.setFormatter(fmt)

        root = logging.getLogger()
        root.setLevel(logging.INFO)
        root.addHandler(console)
        root.addHandler(fileh)
        _configured = True
    return logging.getLogger(name)
