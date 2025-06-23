import aiohttp



import asyncio



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



        self.last_final_url: str = ""







    async def _ensure_session(self):



        if self.session is None:



            timeout = aiohttp.ClientTimeout(total=30)



            headers = {"User-Agent": self.config.user_agent}



            self.session = aiohttp.ClientSession(



                timeout=timeout, headers=headers, cookies=self.cookies



            )







    async def fetch_text(



        self, url: str, allow_redirects: bool = True



    ) -> Tuple[int, Optional[str], str]:



        """



        Fetch text content (HTML) from the URL.



        Returns (status_code, text or None on error, final_url).



        """



        await self._ensure_session()



        await self.throttle.before_request()



        try:



            async with self.session.get(url, allow_redirects=allow_redirects) as response:



                status = response.status



                # Capture the final URL after any redirects



                self.last_final_url = str(response.url)



                text = await response.text(errors="ignore")



        except Exception:



            status = 500



            text = None



            # On error, retain the original URL



            self.last_final_url = url



        finally:



            # Notify throttle controller



            self.throttle.after_response(status)



        return status, text, self.last_final_url







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



        finally:



            self.throttle.after_response(status)



        return status, data







    async def close(self):



        """



        Close the underlying HTTP session.



        """



        if self.session:



            if not self.session.closed:

                await self.session.close()