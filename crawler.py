import re
from urllib.parse import urljoin, urlparse, parse_qsl
import asyncio
from bs4 import BeautifulSoup

from state import State
from fetch import Fetcher
from rewriter import process_html, url_to_local_path
from config import load_config

# Base URL and domain
BASE_DOMAIN = "sm-portugal.forumeiros.com"
BASE_URL = f"https://{BASE_DOMAIN}"

# Allowed query parameters that represent actual pages
ALLOWED_PARAMS = {"start", "folder", "page_profil"}

# Blacklisted query parameters that represent actions
BLACKLIST_PARAMS = {
    "vote", "mode", "friend", "foe", "profil_tabs"
}

def is_valid_link(href: str) -> bool:
    """
    Determine if href should be included in the crawl.
    - Must be within BASE_URL.
    - Must not be only actions (mode=reply etc).
    - Only allow query params in ALLOWED_PARAMS.
    """
    # Skip anchors, mailto, javascript
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
        return False

    abs_url = urljoin(BASE_URL, href)
    parsed = urlparse(abs_url)
    # Must be same domain
    if parsed.netloc != BASE_DOMAIN:
        return False
    # If no query, include
    if not parsed.query:
        return True
    # Parse query params
    params = dict(parse_qsl(parsed.query))
    for key in params:
        if key in BLACKLIST_PARAMS:
            return False
        if key not in ALLOWED_PARAMS:
            return False
    return True

class CrawlWorker:
    """
    Worker that fetches pages, processes HTML, extracts links, and updates state.
    """
    def __init__(self, config, state: State, fetcher: Fetcher):
        self.config = config
        self.state = state
        self.fetcher = fetcher

    async def run(self):
        while True:
            url = await self.state.get_next_url()
            if url is None:
                break
            # Fetch page text
            status, html = await self.fetcher.fetch_text(url)
            if status == 200 and html:
                try:
                    # Rewrite HTML and save local copy
                    new_html = await process_html(url, html, self.fetcher, self.state)
                    local_path = url_to_local_path(url)
                    async with asyncio.to_thread(open, local_path, "w", encoding="utf-8") as f:
                        f.write(new_html)
                    await self.state.update_after_fetch(url, True)

                    # Extract and enqueue new links from original HTML
                    soup = BeautifulSoup(html, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if is_valid_link(href):
                            abs_link = urljoin(BASE_URL, href)
                            await self.state.add_url(abs_link)

                except Exception as e:
                    await self.state.update_after_fetch(url, False, str(e))
            else:
                await self.state.update_after_fetch(url, False, f"HTTP {status}")