# network/__init__.py

"""
The `network` package handles all HTTP-related functionality for the crawler:
  - Throttling and rate limiting (adaptive, fixed, etc.)
  - HTTP session management and wrappers
  - Authentication via cookies
"""

from .http_client import HTTPClient
from .rate_limit import (
    RateLimiter,
    get_limiter,
    AdaptiveLimiter,
    FixedLimiter,
)
from .auth import (
    load_cookies,
    is_logged_in,
    CookieNotFoundError,
    CookieInvalidError,
)
