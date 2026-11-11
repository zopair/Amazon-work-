"""Bounded exponential backoff for transient network/model transport failures.

No model client is present in the current deterministic pipeline. Callers should wrap
only idempotent remote operations and provide a narrow retry predicate.
"""
from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry_with_backoff(
    operation: Callable[[], T],
    *,
    attempts: int = 4,
    base_delay: float = 1.0,
    max_delay: float = 8.0,
    retryable: Callable[[Exception], bool] | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if base_delay < 0 or max_delay < 0:
        raise ValueError("backoff delays must be non-negative")
    should_retry = retryable or (lambda exc: isinstance(exc, (TimeoutError, ConnectionError)))
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as exc:
            if attempt == attempts - 1 or not should_retry(exc):
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            sleep(delay)
    raise RuntimeError("unreachable retry state")
