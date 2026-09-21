"""
settings.py
------------
Centralized configuration loader for Momentum.

Why this exists:
Every other module in the app (views, controllers, database) needs
values like colors, window size, reminder times, etc. Instead of
hardcoding those values everywhere, they all import `settings` from
this file, which loads config.json ONCE and exposes it as a typed,
dot-accessible object.

If a user wants to change the accent color, morning reminder time,
or add a new habit, they edit config.json -- no code changes needed.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


# Root of the whole project (momentum/), computed relative to this file
# so the app works regardless of the current working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "config.json"


class _DotDict(dict):
    """
    A dict that also supports attribute access: settings.theme.accent
    instead of settings["theme"]["accent"]. Purely a convenience layer;
    behaves exactly like a dict otherwise.
    """

    def __getattr__(self, key: str) -> Any:
        try:
            value = self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc
        if isinstance(value, dict):
            # Wrap nested dicts lazily so settings.a.b.c works at any depth
            value = _DotDict(value)
        return value


class Settings:
    """
    Singleton-style configuration manager.

    Usage:
        from config.settings import settings
        settings.theme.accent          -> "#4F8EF7"
        settings.get("app.window_width") -> 1280
        settings.reload()              -> re-reads config.json from disk
    """

    _instance: "Settings | None" = None

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self._data: dict[str, Any] = json.load(f)

    def reload(self) -> None:
        """Re-read config.json from disk (e.g. after a settings screen edit)."""
        self._load()

    def __getattr__(self, key: str) -> Any:
        try:
            value = self._data[key]
        except KeyError as exc:
            raise AttributeError(f"No config section named '{key}'") from exc
        if isinstance(value, dict):
            return _DotDict(value)
        return value

    def get(self, dotted_path: str, default: Any = None) -> Any:
        """Access a nested value with a dotted path, e.g. 'theme.accent'."""
        node: Any = self._data
        for part in dotted_path.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    def resolve_path(self, relative_path: str) -> Path:
        """Turn a config-relative path (e.g. database.path) into an absolute Path."""
        return PROJECT_ROOT / relative_path


# Single shared instance imported everywhere else in the app.
settings = Settings()


def ensure_runtime_dirs() -> None:
    """Create data/, logs/, backups/ directories if they don't exist yet."""
    for rel_dir in ("data", "logs", "backups"):
        os.makedirs(PROJECT_ROOT / rel_dir, exist_ok=True)
