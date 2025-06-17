import re
from urllib.parse import urljoin, urlparse, parse_qsl
import asyncio
from bs4 import BeautifulSoup

from state import State
from fetch import Fetcher
from rewriter import process_html, url_to_local_path
from config import load_config

# Base domain and URL
BASE_DOMAIN = "sm-portugal.forumeiros.com"
BASE_URL = f"https://{BASE_DOMAIN}"

# Allowed and disallowed query parameters
ALLOWED_PARAMS = {"start", "folder", "page_profil"}
BLACKLIST_PARAMS = {"vote", "mode", "friend", "foe", "profil_tabs"}

def is_valid_link(href: str) -> bool:
    """
    Determine if an href should be included in the crawl:
    - Must be within BASE_URL domain.
    - Must not be an action (e.g. mode=reply).
    - Only allow query params in ALLOWED_PARAMS.
    """
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
        return False
    abs_url = urljoin(BASE_URL, href)
    parsed = urlparse(abs_url)
    if parsed.netloc != BASE_DOMAIN:
        return False
    if not parsed.query:
        return True
    params = dict(parse_qsl(parsed.query))
    for key in params:
        if key in BLACKLIST_PARAMS or key not in ALLOWED_PARAMS:
            return False
    return True

class CrawlWorker:
    """
    Worker that fetches pages, processes HTML, extracts links, and updates state.
    """
    def __init__(self, config, state: State, fetcher: Fetcher, worker_id: int = 0):
        self.config = config
        self.state = state
        self.fetcher = fetcher
        self.id = worker_id

    async def run(self):
        while True:
            try:
                url = await self.state.get_next_url()
            except Exception as e:
                print(f"[Worker {self.id}] Error retrieving next URL: {e}")
                url = None
            if url is None:
                if any(data["status"] == "in_progress" for data in list(self.state.urls.values())):
                    print(f"[Worker {self.id}] No URL to crawl right now, waiting for new tasks...")
                    await asyncio.sleep(0.5)
                    continue
                else:
                    print(f"[Worker {self.id}] No more URLs to crawl. Worker stopping.")
                    break
            print(f"[Worker {self.id}] Fetching: {url}")
            try:
                status, html = await self.fetcher.fetch_text(url)
            except Exception as e:
                print(f"[Worker {self.id}] Exception during fetch of {url}: {e}")
                await self.state.update_after_fetch(url, False, str(e))
                continue
            if status == 200 and html:
                print(f"[Worker {self.id}] Fetched {url} (status {status}, {len(html)} bytes)")
                try:
                    print(f"[Worker {self.id}] Processing HTML for {url}")
                    new_html = await process_html(url, html, self.fetcher, self.state)
                    local_path = url_to_local_path(url)
                    print(f"[Worker {self.id}] Saving page content to {local_path}")
                    await asyncio.to_thread(lambda path, data: open(path, "w", encoding="utf-8").write(data), local_path, new_html)
                    print(f"[Worker {self.id}] Saved page: {url} -> {local_path}")
                    await self.state.update_after_fetch(url, True)
                    soup = BeautifulSoup(html, "html.parser")
                    new_links_count = 0
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if is_valid_link(href):
                            abs_link = urljoin(BASE_URL, href)
                            await self.state.add_url(abs_link)
                            new_links_count += 1
                    print(f"[Worker {self.id}] Extracted {new_links_count} new links from {url}")
                except Exception as e:
                    print(f"[Worker {self.id}] Error processing {url}: {e}")
                    await self.state.update_after_fetch(url, False, str(e))
            else:
                print(f"[Worker {self.id}] Failed to fetch {url} (status {status})")
                await self.state.update_after_fetch(url, False, f"HTTP {status}")