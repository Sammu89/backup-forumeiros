import os
import traceback
import asyncio
from urllib.parse import urljoin, urlparse, parse_qsl
from bs4 import BeautifulSoup

from redirects import redirects
from state import State
from fetch import Fetcher
from rewriter import process_html, url_to_local_path
from config import load_config

# Base domain and URL
BASE_DOMAIN = "sm-portugal.forumeiros.com"
BASE_URL = f"https://{BASE_DOMAIN}"

# Allowed/disallowed params & prefixes
ALLOWED_PARAMS = {"start", "folder", "page_profil"}
BLACKLIST_PARAMS = {"vote", "mode", "friend", "foe", "profil_tabs"}
IGNORED_PREFIXES = ("/admin", "/modcp", "/profile")


def strip_fragment(url: str) -> str:
    """Remove the #fragment from a URL."""
    return url.split('#', 1)[0]


def is_valid_link(href: str) -> bool:
    """
    Determine if an href should be included in the crawl:
    - Must be within BASE_URL domain.
    - Must not be an action (e.g. mode=reply).
    - Ignore admin/modcp/profile.
    - Only allow query params in ALLOWED_PARAMS.
    """
    # descartar âncoras, mailto e javascript
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
        return False

    # tenta normalizar URL; se falhar, ignora
    try:
        abs_url = urljoin(BASE_URL, href)
        base_no_frag = strip_fragment(abs_url)
        parsed = urlparse(base_no_frag)
    except Exception:
        return False

    # ignora paths de admin, modcp, profile
    if parsed.path.startswith(IGNORED_PREFIXES):
        return False

    # domínio deve casar exatamente
    if parsed.netloc != BASE_DOMAIN:
        return False

    # permite caminhos sem query
    if not parsed.query:
        return True

    # senão, valida os parâmetros
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
    local_dir = os.path.join("backup", folder)
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, outfile)


class DiscoverWorker:
    """Phase-1: Only fetch HTML, extract links, map redirects—no assets."""

    def __init__(self, config, state: State, fetcher: Fetcher, worker_id: int = 0):
        self.config = config
        self.state = state
        self.fetcher = fetcher
        self.id = worker_id

    async def run(self):
        empty, max_empty = 0, 20
        while True:
            path = await self.state.get_next("discover")
            if not path:
                empty += 1
                if empty >= max_empty:
                    print(f"[DiscoverWorker {self.id}] no more pending, stopping.")
                    break
                await asyncio.sleep(0.5)
                continue

            empty = 0
            url = urljoin(BASE_URL, path)
            print(f"[DiscoverWorker {self.id}] Fetching: {url}")
            try:
                # 1) Try WITHOUT following redirects to catch 301/302
                status, _, final_url = await self.fetcher.fetch_text(url, allow_redirects=False)

                # 2) If it was an internal redirect, handle immediately
                if status in (301, 302) and urlparse(final_url).netloc == BASE_DOMAIN:
                    po = urlparse(url)
                    pf = urlparse(final_url)
                    src = po.path + (f"?{po.query}" if po.query else "")
                    dst = pf.path + (f"?{pf.query}" if pf.query else "")
                    print(f"[DiscoverWorker {self.id}] Redirect: {src} → {dst}")
                    await redirects.add(src, dst)
                    await self.state.add_url(dst)
                    await self.state.update_after_fetch(src, True)
                    continue  # skip link extraction on the old URL

                # 3) Otherwise fetch the real HTML (following any further redirects)
                status, html, final_url = await self.fetcher.fetch_text(url, allow_redirects=True)
            except Exception as e:
                traceback.print_exc()
                await self.state.update_after_fetch(path, False, str(e))
                continue

            # — Redirect handling —
            if final_url != url and urlparse(final_url).netloc == BASE_DOMAIN:
                po = urlparse(url)
                pf = urlparse(final_url)
                src = po.path + (f"?{po.query}" if po.query else "")
                dst = pf.path + (f"?{pf.query}" if pf.query else "")
                print(f"[DiscoverWorker {self.id}] Redirect: {src} → {dst}")
                await redirects.add(src, dst)
                await self.state.add_url(dst)
                await self.state.update_after_fetch(src, True)
                continue

            # — Non-200? —
            if status != 200 or not html:
                print(f"[DiscoverWorker {self.id}] HTTP {status}, skipping")
                await self.state.update_after_fetch(path, False, f"HTTP {status}")
                continue

            # — Extract links —
            soup = BeautifulSoup(html, "html.parser")
            added = 0
            for a in soup.find_all("a", href=True):
                h = a["href"]
                if is_valid_link(h):
                    link = urljoin(BASE_URL, h)
                    nf = strip_fragment(link)
                    p = urlparse(nf)
                    qp = p.path + (f"?{p.query}" if p.query else "")
                    await self.state.add_url(qp)
                    added += 1

            await self.state.mark_discovered(path)
            print(f"[DiscoverWorker {self.id}] {path} → +{added} links")


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
                print(f"[DownloadWorker {self.id}] no more downloads, stopping.")
                break

            url = urljoin(BASE_URL, path)
            print(f"[DownloadWorker {self.id}] Fetch for download: {url}")
            try:
                # catch Location header first
                status, _, final_url = await self.fetcher.fetch_text(url, allow_redirects=False)
                if status in (301, 302) and urlparse(final_url).netloc == BASE_DOMAIN:
                    # identical redirect handling as above
                    po, pf = urlparse(url), urlparse(final_url)
                    src = po.path + (f"?{po.query}" if po.query else "")
                    dst = pf.path + (f"?{pf.query}" if pf.query else "")
                    print(f"[DownloadWorker {self.id}] Redirect: {src} → {dst}")
                    await redirects.add(src, dst)
                    await self.state.add_url(dst)
                    await self.state.update_after_fetch(src, True)
                    continue

                # fetch real content
                status, html, final_url = await self.fetcher.fetch_text(url, allow_redirects=True)
            except Exception as e:
                traceback.print_exc()
                await self.state.update_after_fetch(path, False, str(e))
                continue

            # — Redirect handling in download —
            if final_url != url and urlparse(final_url).netloc == BASE_DOMAIN:
                po = urlparse(url)
                pf = urlparse(final_url)
                src = po.path + (f"?{po.query}" if po.query else "")
                dst = pf.path + (f"?{pf.query}" if pf.query else "")
                print(f"[DownloadWorker {self.id}] Redirected download: {src} → {dst}")
                await redirects.add(src, dst)
                await self.state.add_url(dst)
                await self.state.update_after_fetch(src, True)
                continue

            # — Non-200? —
            if status != 200 or not html:
                print(f"[DownloadWorker {self.id}] HTTP {status}, skipping")
                await self.state.update_after_fetch(path, False, f"HTTP {status}")
                continue

            # — Rewrite HTML & assets —
            try:
                new_html = await process_html(url, html, self.fetcher, self.state)
                save_to = url_to_local_path(final_url if final_url != url else url)
                
                # Write file asynchronously
                def write_file(path, data):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(data)
                
                await asyncio.to_thread(write_file, save_to, new_html)
                
                fp = urlparse(final_url).path + (f"?{urlparse(final_url).query}" if urlparse(final_url).query else "")
                await self.state.mark_downloaded(fp)
                if self.progress:
                    self.progress.update(1)
                print(f"[DownloadWorker {self.id}] Saved: {fp}")
            except Exception as e:
                traceback.print_exc()
                await self.state.update_after_fetch(path, False, str(e))