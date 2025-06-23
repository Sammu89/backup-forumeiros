import os
import traceback
import asyncio
from urllib.parse import urljoin, urlparse, parse_qsl
from bs4 import BeautifulSoup
from pathlib import Path

from redirects import redirects
import settings as st
from settings import get_base_domain, ALLOWED_PARAMS, BLACKLIST_PARAMS, IGNORED_PREFIXES
from state import State
from fetch import Fetcher
from rewriter import process_html
from settings import load_config


def strip_fragment(url: str) -> str:
    """Remove the #fragment from a URL."""
    return url.split('#', 1)[0]


def is_valid_link(href: str) -> bool:
    """
    Determine if an href should be included in the crawl:
    - Must be within st.BASE_URL domain.
    - Must not be an action (e.g. mode=reply).
    - Ignore admin/modcp/profile.
    - Only allow query params in ALLOWED_PARAMS.
    """
    # Skip anchors, mailto and javascript links
    if href.startswith(("#", "mailto:", "javascript:")):
        return False

    # Try to normalize URL; if it fails, ignore
    try:
        abs_url = urljoin(st.BASE_URL, href)
        no_frag = strip_fragment(abs_url)
        parsed = urlparse(no_frag)
    except Exception:
        return False

    # Ignore admin, modcp, profile paths
    if parsed.path.startswith(IGNORED_PREFIXES):
        return False

    # Domain must match exactly
    if parsed.netloc != get_base_domain():
        return False

    # Allow paths without query
    if not parsed.query:
        return True

    # Otherwise, validate parameters
    params = dict(parse_qsl(parsed.query))
    for key in params:
        if key in BLACKLIST_PARAMS or key not in ALLOWED_PARAMS:
            return False

    return True


def url_to_local_path(url: str) -> str:
    """
    Map a full URL to a folder/filename under ./backup/.
    Categories (f*), topics (t*), users (u*), groups (g*), etc.
    """
    parsed = urlparse(url)
    # ─── Special-case the site root ────────────────────────────────────────
    if parsed.path in ("", "/"):
        backup_root = st.BACKUP_ROOT or Path("backup")
        return str(backup_root / "index.html")
    
    # Map URL patterns to folder names
    folder_mapping = {
        "f": "categorias",
        "t": "topicos", 
        "u": "users",
        "g": "grupos",
        "admin": "admin",
        "privmsg": "privmsg",
        "profile": "profile"
    }
    
    folder = "misc"  # default
    for prefix, folder_name in folder_mapping.items():
        if first.startswith(prefix):
            folder = folder_name
            break

    # Create filename slug
    slug = path.replace("/", "_") if path else "index"
    if parsed.query:
    # Sanitize query parameters (avoid “/” nesting)
        query_slug = (
            parsed.query
            .replace("=", "-")
            .replace("&", "_")
            .replace("/", "_")
        )
        slug += f"_{query_slug}"


    outfile = f"{slug}.html"
    
    # Use pathlib for better path handling
    backup_root = st.BACKUP_ROOT or Path("backup")
    local_dir = backup_root / folder
    local_dir.mkdir(parents=True, exist_ok=True)
    
    return str(local_dir / outfile)


async def safe_file_write(filepath: str, content: str) -> bool:
    """Safely write content to file asynchronously."""
    try:
        def write_file():
            # make sure the full path exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

        
        await asyncio.to_thread(write_file)
        return True
    except Exception as e:
        print(f"[FileWrite] Error writing {filepath}: {e}")
        return False


async def safe_file_read(filepath: str) -> str:
    """Safely read content from file asynchronously."""
    try:
        def read_file():
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        
        return await asyncio.to_thread(read_file)
    except Exception as e:
        print(f"[FileRead] Error reading {filepath}: {e}")
        return ""


def extract_path_from_url(url: str) -> str:
    """Extract path and query from URL for state management."""
    parsed = urlparse(url)
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


async def handle_redirect(worker_id: int, original_url: str, final_url: str, state: State) -> bool:
    """Handle URL redirects and update state."""
    if final_url == original_url:
        return False
        
    if urlparse(final_url).netloc != st.BASE_DOMAIN:
        return False
    
    src_path = extract_path_from_url(original_url)
    dst_path = extract_path_from_url(final_url)
    
    print(f"[Worker {worker_id}] Redirect: {src_path} → {dst_path}")
    await redirects.add(src_path, dst_path)
    await state.add_url(dst_path)
    await state.update_after_fetch(src_path, True)
    return True


class DiscoverWorker:
    """Phase-1: Only fetch HTML, extract links, map redirects—no assets."""

    def __init__(self, config, state: State, fetcher: Fetcher, worker_id: int = 0):
        self.config = config
        self.state = state
        self.fetcher = fetcher
        self.id = worker_id

    async def run(self):
        empty_count = 0
        max_empty = 20

        while True:
            path = await self.state.get_next("discover")
            if not path:
                empty_count += 1
                if empty_count >= max_empty:
                    print(f"[DiscoverWorker {self.id}] No more pending URLs, stopping.")
                    break
                await asyncio.sleep(0.5)
                continue

            empty_count = 0
            await self._process_url(path)

    async def _process_url(self, path: str):
        """Process a single URL for discovery."""
        url = urljoin(st.BASE_URL, path)
        print(f"[DiscoverWorker {self.id}] Fetching: {url}")

        try:
            # First try without redirects to catch 301/302
            status, _, redirect_url = await self.fetcher.fetch_text(url, allow_redirects=False)

            # Handle immediate redirects
            if status in (301, 302):
                if await handle_redirect(self.id, url, redirect_url, self.state):
                    return

            # Fetch the actual HTML content
            status, html, final_url = await self.fetcher.fetch_text(url, allow_redirects=True)

            # Handle any final redirects
            if await handle_redirect(self.id, url, final_url, self.state):
                return

            # Check for successful response
            if status != 200 or not html:
                print(f"[DiscoverWorker {self.id}] HTTP {status}, skipping {path}")
                await self.state.update_after_fetch(path, False, f"HTTP {status}")
                return

            # Save raw HTML locally
            local_path = url_to_local_path(final_url)
            if await safe_file_write(local_path, html):
                print(f"[DiscoverWorker {self.id}] Saved HTML: {local_path}")
            else:
                await self.state.update_after_fetch(path, False, "File write error")
                return

            # Extract and process links
            link_count = await self._extract_links(html)
            await self.state.mark_discovered(path)
            print(f"[DiscoverWorker {self.id}] {path} → +{link_count} links")

        except Exception as e:
            traceback.print_exc()
            await self.state.update_after_fetch(path, False, str(e))

    async def _extract_links(self, html: str) -> int:
        """Extract valid links from HTML content."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            added_count = 0

            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if is_valid_link(href):
                    # Normalize the link
                    abs_url = urljoin(st.BASE_URL, href)
                    clean_url = strip_fragment(abs_url)
                    path = extract_path_from_url(clean_url)
                    
                    await self.state.add_url(path)
                    added_count += 1

            return added_count
        except Exception as e:
            print(f"[DiscoverWorker {self.id}] Link extraction error: {e}")
            return 0


class DownloadWorker:
    """Phase-2: Fetch HTML, rewrite & download assets, then save."""

    def __init__(self, config, state: State, fetcher: Fetcher, progress=None, worker_id: int = 0):
        self.config = config
        self.state = state
        self.fetcher = fetcher
        self.progress = progress
        self.id = worker_id

    async def run(self):
        while True:
            path = await self.state.get_next("download")
            if not path:
                print(f"[DownloadWorker {self.id}] No more downloads, stopping.")
                break

            await self._process_download(path)

    async def _process_download(self, path: str):
        """Process a single URL for download and asset processing."""
        url = urljoin(st.BASE_URL, path)
        print(f"[DownloadWorker {self.id}] Processing: {path}")

        try:
            # Fetch fresh HTML for processing
            status, html, final_url = await self.fetcher.fetch_text(url, allow_redirects=True)

            # Handle redirects during download
            if await handle_redirect(self.id, url, final_url, self.state):
                return

            # Check for successful response
            if status != 200 or not html:
                print(f"[DownloadWorker {self.id}] HTTP {status}, skipping {path}")
                await self.state.update_after_fetch(path, False, f"HTTP {status}")
                return

            # Process HTML and download assets
            processed_html = await process_html(final_url, html, self.fetcher, self.state)
            
            # Save processed HTML
            save_path = url_to_local_path(final_url)
            if await safe_file_write(save_path, processed_html):
                final_path = extract_path_from_url(final_url)
                await self.state.mark_downloaded(final_path)
                
                if self.progress:
                    self.progress.update(1)
                    
                print(f"[DownloadWorker {self.id}] Completed: {final_path}")
            else:
                await self.state.update_after_fetch(path, False, "File write error")

        except Exception as e:
            traceback.print_exc()
            await self.state.update_after_fetch(path, False, str(e))