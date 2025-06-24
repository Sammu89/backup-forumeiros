# network/http_client.py

from __future__ import annotations
import asyncio
from typing import Optional, Tuple
import aiohttp

from forum_backup_crawler.network.rate_limit import RateLimiter


class HTTPClient:
    """
    HTTP client wrapper that integrates with our RateLimiter
    to throttle requests and manage a persistent aiohttp session.
    """

    def __init__(
        self,
        limiter: RateLimiter,
        user_agent: str,
        cookies: Optional[dict] = None,
    ) -> None:
        """
        :param limiter: RateLimiter instance to call before/after requests
        :param user_agent: User-Agent header string
        :param cookies: Optional dict of cookies for the session
        """
        self._limiter = limiter
        self._headers = {"User-Agent": user_agent}
        self._cookies = cookies
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self) -> None:
        """Initialize the aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                headers=self._headers, cookies=self._cookies
            )

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def fetch_text(
        self, url: str, allow_redirects: bool = True
    ) -> Tuple[int, Optional[str], str]:
        """
        Fetch a URL expecting text (HTML, JSON, etc.).

        :param url: URL to GET
        :param allow_redirects: whether to follow 3xx redirects
        :returns: (status_code, text or None on error, final_url)
        """
        await self._limiter.before_request()
        try:
            assert self._session is not None, "Session not started"
            async with self._session.get(url, allow_redirects=allow_redirects, timeout=30) as resp:
                text = await resp.text()
                final = str(resp.url)
                status = resp.status
        except Exception:
            # Network error or timeout
            status, text, final = 0, None, url
        await self._limiter.after_response(status)
        return status, text, final

    async def fetch_bytes(self, url: str) -> Tuple[int, Optional[bytes]]:
        """
        Fetch a URL expecting binary data (images, CSS, JS).

        :param url: URL to GET
        :returns: (status_code, bytes or None on error)
        """
        await self._limiter.before_request()
        try:
            assert self._session is not None, "Session not started"
            async with self._session.get(url, allow_redirects=True, timeout=30) as resp:
                data = await resp.read()
                status = resp.status
        except Exception:
            status, data = 0, None
        await self._limiter.after_response(status)
        return status, data
