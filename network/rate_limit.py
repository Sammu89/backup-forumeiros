from __future__ import annotations
import asyncio
from typing import Protocol, Literal


class RateLimiter(Protocol):
    """Protocol for any rate limiter strategy."""

    async def before_request(self) -> None:
        """Pause before making an HTTP request."""

    async def after_response(self, status: int) -> None:
        """Adjust internal state based on the HTTP response status."""

    @property
    def current_delay(self) -> float:
        """Current delay before requests."""

    @property
    def current_workers(self) -> int:
        """Current permitted level of concurrency."""


def get_limiter(
    strategy: Literal["adaptive", "fixed", "token_bucket"],
    *,
    base_delay: float,
    min_delay: float,
    max_delay: float,
    max_workers: int,
) -> RateLimiter:
    """
    Factory that returns an instance of a RateLimiter based on the chosen strategy.
    """
    if strategy == "adaptive":
        return AdaptiveLimiter(base_delay, min_delay, max_delay, max_workers)
    # For now, ignore token_bucket and default to FixedLimiter
    return FixedLimiter(base_delay, max_workers)


class AdaptiveLimiter:
    """
    Adaptive rate limiter with exponential back-off on errors and gradual speed-up on successes.
    """

    def __init__(
        self,
        base_delay: float = 0.5,
        min_delay: float = 0.1,
        max_delay: float = 5.0,
        max_workers: int = 8,
    ) -> None:
        self._delay = base_delay
        self._min_delay = min_delay
        self._max_delay = max_delay
        self._max_workers = max_workers
        self._success_streak = 0
        self._workers = max_workers

    @property
    def current_delay(self) -> float:
        return self._delay

    @property
    def current_workers(self) -> int:
        return self._workers

    async def before_request(self) -> None:
        await asyncio.sleep(self._delay)

    async def after_response(self, status: int) -> None:
        if status == 429 or 500 <= status < 600:
            # Exponential back-off
            self._delay = min(self._delay * 2, self._max_delay)
            self._workers = max(self._workers - 1, 1)
            self._success_streak = 0
        elif 200 <= status < 300:
            # Success: gradually speed up
            self._success_streak += 1
            if self._success_streak >= 30:
                self._delay = max(self._delay - 0.1, self._min_delay)
                self._workers = min(self._workers + 1, self._max_workers)
                self._success_streak = 0
        # Other status codes => no change


class FixedLimiter:
    """
    Simple rate limiter that always waits a fixed delay and uses fixed workers.
    """

    def __init__(self, delay: float = 0.5, workers: int = 8) -> None:
        self._delay = delay
        self._workers = workers

    @property
    def current_delay(self) -> float:
        return self._delay

    @property
    def current_workers(self) -> int:
        return self._workers

    async def before_request(self) -> None:
        await asyncio.sleep(self._delay)

    async def after_response(self, status: int) -> None:
        # No dynamic adjustment
        return
