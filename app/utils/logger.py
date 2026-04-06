"""
Logging setup for FastAPI.
Called once from the app lifespan handler.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

try:
    import colorlog
    _HAS_COLORLOG = True
except ImportError:
    _HAS_COLORLOG = False


def setup_logger(log_level: str = "INFO", log_file: str = "logs/app.log") -> None:
    """Configure the root logger with console + rotating file handlers."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    if root.handlers:
        return  # already configured (e.g., called twice in tests)

    # ── Console handler ───────────────────────────────────────────
    if _HAS_COLORLOG:
        console_fmt = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(name)s%(reset)s — %(message)s",
            log_colors={
                "DEBUG": "cyan", "INFO": "green",
                "WARNING": "yellow", "ERROR": "red", "CRITICAL": "bold_red",
            },
        )
    else:
        console_fmt = logging.Formatter("%(levelname)-8s %(name)s — %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_fmt)
    console_handler.setLevel(level)
    root.addHandler(console_handler)

    # ── Rotating file handler (max 5 MB, keep 3 backups) ─────────
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
    file_fmt = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(file_fmt)
    file_handler.setLevel(level)
    root.addHandler(file_handler)
