import aiohttp, asyncio
from urllib.parse import urljoin
from typing import Tuple, Optional

class Fetcher:
    """
    Performs HTTP GET requests with cookies, user-agent, timeouts, and throttling.
    Provides methods to fetch text (HTML) and binary (assets).
    """
    def __init__(self, config, throttle, cookies: dict):
        """
        :param config: Config object with user_agent, etc.
        :param throttle: ThrottleController instance.
        :param cookies: Dict of cookie name -> value.
        """
        self.config = config
        self.throttle = throttle
        self.cookies = cookies
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {"User-Agent": self.config.user_agent}
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers, cookies=self.cookies)

    async def fetch_text(
        self,
        url: str,
        allow_redirects: bool = True
    ) -> Tuple[int, Optional[str], str]:
        """
        Fetch text content from `url`.
        If allow_redirects=False and we get 301/302, we capture the Location header
        and return (status, None, final_url).
        Otherwise we follow redirects and return (status, text, final_url).
        """
        await self._ensure_session()
        await self.throttle.before_request()

        try:
            async with self.session.get(url, allow_redirects=allow_redirects) as resp:
                status = resp.status

                # 1) If 301/302 and we're NOT following, grab Location
                if status in (301, 302) and not allow_redirects:
                    loc = resp.headers.get("Location")
                    # make it absolute
                    final = urljoin(url, loc) if loc else url
                    text  = None

                else:
                    # 2) normal path: follow (or single fetch), read body
                    final = str(resp.url)
                    text  = await resp.text(errors="ignore")

        except Exception:
            status = 500
            text   = None
            final  = url

        self.throttle.after_response(status)
        return status, text, final

    async def fetch_bytes(self, url: str) -> Tuple[int, Optional[bytes]]:
        """
        Fetch binary content (for assets) from the URL.
        Returns (status_code, bytes or None on error).
        """
        await self._ensure_session()
        await self.throttle.before_request()
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                status = response.status
                data = await response.read()
        except Exception:
            status = 500
            data = None
        self.throttle.after_response(status)
        return status, data

    async def close(self):
        """
        Close the underlying HTTP session.
        """
        if self.session:
            await self.session.close()