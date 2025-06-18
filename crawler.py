import os
import re
import traceback
from urllib.parse import urljoin, urlparse, parse_qsl
import asyncio
from bs4 import BeautifulSoup
from redirects import RedirectMap
from redirects import redirects
redirects = RedirectMap()
from state import State
from fetch import Fetcher
from rewriter import process_html, url_to_local_path
from config import load_config

# Base domain and URL
BASE_DOMAIN = "sm-portugal.forumeiros.com"
BASE_URL = f"https://{BASE_DOMAIN}"

# Output directory for downloaded files
OUTPUT_DIR = "backup"

# Allowed and disallowed query parameters
ALLOWED_PARAMS = {"start", "folder", "page_profil"}
BLACKLIST_PARAMS = {"vote", "mode", "friend", "foe", "profil_tabs"}
IGNORED_PREFIXES = ("/admin", "/modcp", "/profile")

def strip_fragment(url: str) -> str:
    return url.split('#', 1)[0]

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
    base_no_frag = strip_fragment(abs_url)
    parsed = urlparse(base_no_frag)
        # ignore certain admin/profile/modcp paths entirely
    if parsed.path.startswith(IGNORED_PREFIXES):
        return False

    if parsed.netloc != BASE_DOMAIN:
        return False
    if not parsed.query:
        return True
    params = dict(parse_qsl(parsed.query))
    for key in params:
        if key in BLACKLIST_PARAMS or key not in ALLOWED_PARAMS:
            return False
    return True


def url_to_local_path(url: str) -> str:
    """Convert URL to local file path for saving."""
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")
    first = path.split("/", 1)[0].lower() if path else ""

    if first.startswith("f"):
        folder = "categorias"
    elif first.startswith("t"):
        folder = "topicos"
    elif first.startswith("u"):
        folder = "users"
    elif first.startswith("g"):
        folder = "grupos"
    elif first.startswith("admin"):
        folder = "admin"
    elif first.startswith("privmsg"):
        folder = "privmsg"
    elif first.startswith("profile"):
        folder = "profile"
    else:
        folder = "misc"
    
    slug = path.replace("/", "_") if path else "index"
    if parsed.query:
        slug += "_" + parsed.query.replace("=", "-").replace("&", "_")
    
    outfile = f"{slug}.html"
    local_dir = os.path.join(OUTPUT_DIR, folder)
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, outfile)


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
                traceback.print_exc()
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
                status, html, final_url = await self.fetcher.fetch_text(url)
            #— HANDLE INTERNAL REDIRECTS —
if status in (301,302) or final_url != url:
    parsed_orig = urlparse(url)
    parsed_fin  = urlparse(final_url)
    if parsed_orig.netloc == parsed_fin.netloc:
        src = parsed_orig.path + (f"?{parsed_orig.query}" if parsed_orig.query else "")
        dst = parsed_fin.path   + (f"?{parsed_fin.query}"  if parsed_fin.query  else "")
        await redirects.add(src, dst)
        # enqueue final URL if new
        await self.state.add_url(dst)
        # mark original done
        await self.state.update_after_fetch(src, True)
        print(f"[DiscoverWorker {self.id}] Redirect: {src} → {dst}")
        continue   # skip normal parsing of html under old URL
    
            # Detect final URL after redirects (aiohttp gives response.url)
            final_url = str(self.fetcher.last_final_url)  # we'll add this attr below
            if final_url != url:
                src_path  = urlparse(url).path + ("?"+urlparse(url).query if urlparse(url).query else "")
                dst_path  = urlparse(final_url).path + ("?"+urlparse(final_url).query if urlparse(final_url).query else "")
                await redirects.add(src_path, dst_path)
                # make sure we use only the destination in state
                await self.state.add_url(dst_path)
                await self.state.update_after_fetch(src_path, True)  # mark original as done/ignored
                url = final_url         # continue processing with the real page
                print(f"[Redirect] {src_path} → {dst_path}")
    
                
                
                
                
                
            except Exception as e:
                traceback.print_exc()
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
                    await asyncio.to_thread(self._save_file, local_path, new_html)
                    print(f"[Worker {self.id}] Saved page: {url} -> {local_path}")
                    await self.state.update_after_fetch(url, True)
                    
                    # Extract new links
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
                    traceback.print_exc()
                    print(f"[Worker {self.id}] Error processing {url}: {e}")
                    await self.state.update_after_fetch(url, False, str(e))
            else:
                print(f"[Worker {self.id}] Failed to fetch {url} (status {status})")
                await self.state.update_after_fetch(url, False, f"HTTP {status}")

    def _save_file(self, path: str, data: str):
        """Helper method to save file synchronously."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)


class DiscoverWorker:
    """Phase-1: crawl only to enumerate links."""
    
    def __init__(self, config, state: State, fetcher: Fetcher, worker_id: int = 0):
        self.config = config
        self.state = state
        self.fetcher = fetcher
        self.id = worker_id
    
    async def run(self):
        empty_checks = 0
        max_empty_checks = 20  # 20 tentativas * 0,5 s ≈ 10 s de margem

        while True:
            path = await self.state.get_next("discover")
            url = urljoin(BASE_URL, path) if path else None
            if url is None:
                empty_checks += 1
                # Se já fez 20 tentativas sem novo URL, sai
                if empty_checks >= max_empty_checks:
                    print(f"[DiscoverWorker {self.id}] Fim da fila. Worker a parar.")
                    break
                await asyncio.sleep(0.5)
                continue  # volta a tentar

            empty_checks = 0  # reset porque encontrou trabalho
            print(f"[DiscoverWorker {self.id}] {url}")
            
            try:
                status, html, final_url = await self.fetcher.fetch_text(url)
                if status in (301,302) or final_url != url:
    po = urlparse(url); pf = urlparse(final_url)
    src = po.path + (f"?{po.query}" if po.query else "")
    dst = pf.path + (f"?{pf.query}" if pf.query else "")
    await redirects.add(src, dst)
    # process & save under final_url
    rewritten = await process_html(final_url, html, self.fetcher, self.state)
    local = url_to_local_path(final_url)
    await asyncio.to_thread(self._save_file, local, rewritten)
    await self.state.mark_downloaded(dst)
    await self.state.update_after_fetch(src, True)
    print(f"[DownloadWorker {self.id}] Redirected download: {src} → {dst}")
    continue

                if status == 200 and html:
                    soup = BeautifulSoup(html, "html.parser")
                    added = 0
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if is_valid_link(href):
                            abs_link = urljoin(BASE_URL, href)
                            base = strip_fragment(abs_link)
                            await self.state.add_url(urlparse(base).path + ("?"+urlparse(base).query if urlparse(base).query else ""))
                            added += 1
                    # Marcar esta página como 'l' (listed)
                    rel_path = urlparse(url).path + ("?"+urlparse(url).query if urlparse(url).query else "")
                    await self.state.mark_discovered(rel_path)

                    print(f"[DiscoverWorker {self.id}] {url}  →  +{added} links")
                else:
                    await self.state.update_after_fetch(url, False, f"HTTP {status}")
            except Exception as e:
                traceback.print_exc()
                print(f"[DiscoverWorker {self.id}] Error processing {url}: {e}")
                await self.state.update_after_fetch(url, False, str(e))


class DownloadWorker:
    """Phase-2: rewrite HTML, download assets."""
    
    def __init__(self, config, state: State, fetcher: Fetcher, progress=None, worker_id: int = 0):
        self.config = config
        self.state = state
        self.fetcher = fetcher
        self.progress = progress
        self.id = worker_id
    
    async def run(self):
        while True:
            try:
                url = await self.state.get_next("download")
            except Exception as e:
                print(f"[DownloadWorker {self.id}] Error getting next URL: {e}")
                url = None
                
            if not url:
                print(f"[DownloadWorker {self.id}] No more URLs to download. Worker stopping.")
                break
                
            try:
                status, html = await self.fetcher.fetch_text(url)
                if status == 200 and html:
                    try:
                        rewritten = await process_html(url, html, self.fetcher, self.state)
                        local_path = url_to_local_path(url)
                        await asyncio.to_thread(self._save_file, local_path, rewritten)
                        rel_path = urlparse(url).path + ("?"+urlparse(url).query if urlparse(url).query else "")
                        await self.state.mark_downloaded(rel_path)

                        if self.progress:
                            self.progress.update(1)
                        print(f"[DownloadWorker {self.id}] Downloaded: {url}")
                    except Exception as e:
                        traceback.print_exc()
                        print(f"[DownloadWorker {self.id}] Error processing {url}: {e}")
                        await self.state.update_after_fetch(url, False, str(e))
                else:
                    await self.state.update_after_fetch(url, False, f"HTTP {status}")
            except Exception as e:
                traceback.print_exc()
                print(f"[DownloadWorker {self.id}] Error fetching {url}: {e}")
                await self.state.update_after_fetch(url, False, str(e))

    def _save_file(self, path: str, data: str):
        """Helper method to save file synchronously."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(data)