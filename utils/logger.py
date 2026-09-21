"""
logger.py
---------
Application-wide logging setup.

Why this exists:
Instead of every file doing `print()` (which disappears once the app
is packaged into an .exe with PyInstaller and no console window),
every module gets a proper rotating log file at logs/momentum.log.

Usage:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.info("Task completed: %s", task.name)
    log.error("Database write failed", exc_info=True)
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config.settings import settings, PROJECT_ROOT

_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return

    log_cfg = settings.logging
    log_path = PROJECT_ROOT / log_cfg.file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("momentum")
    root.setLevel(getattr(logging, log_cfg.level, logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=log_cfg.max_bytes,
        backupCount=log_cfg.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    _configured = True


def get_logger(module_name: str) -> logging.Logger:
    """Return a named logger (e.g. 'momentum.views.dashboard') sharing app config."""
    _configure_root_logger()
    return logging.getLogger(f"momentum.{module_name}")
