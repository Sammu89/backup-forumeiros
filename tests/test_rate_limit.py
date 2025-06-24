import asyncio
import pytest
from forum_backup_crawler.network.rate_limit import AdaptiveLimiter, FixedLimiter

@pytest.mark.asyncio
async def test_fixed_limiter_keeps_delay_and_workers():
    lim = FixedLimiter(delay=0.2, workers=3)
    assert lim.current_delay == 0.2
    assert lim.current_workers == 3
    await lim.before_request()
    # after_response does nothing
    await lim.after_response(200)
    assert lim.current_delay == 0.2
    assert lim.current_workers == 3

@pytest.mark.asyncio
async def test_adaptive_backoff_and_recovery():
    lim = AdaptiveLimiter(base_delay=0.1, min_delay=0.05, max_delay=1.0, max_workers=5)
    # simulate a 429
    await lim.before_request()
    await lim.after_response(429)
    assert lim.current_delay == 0.2  # doubled
    assert lim.current_workers == 4  # one fewer

    # simulate 30 successes to speed up
    for _ in range(30):
        await lim.before_request()
        await lim.after_response(200)
    assert lim.current_delay == 0.1  # back toward base (but not below min)
    assert lim.current_workers == 5  # back to max_workers
