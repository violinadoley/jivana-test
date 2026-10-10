from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from app.core.config import Settings

_settings_ctx: ContextVar[Settings | None] = ContextVar("adk_settings", default=None)


def current_settings() -> Settings:
    settings = _settings_ctx.get()
    if settings is None:
        raise RuntimeError("ADK session settings are not bound.")
    return settings


@contextmanager
def bind_settings(settings: Settings) -> Iterator[None]:
    token = _settings_ctx.set(settings)
    try:
        yield
    finally:
        _settings_ctx.reset(token)
