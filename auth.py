import json
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# ─────────────────────────────────────────────────────────────────────────────
# Custom exceptions for cookie handling
# ─────────────────────────────────────────────────────────────────────────────
class CookieNotFoundError(RuntimeError):
    """Raised when the cookies file does not exist."""
    pass

class CookieInvalidError(RuntimeError):
    """Raised when the cookies file contains invalid JSON."""
    pass

# ─────────────────────────────────────────────────────────────────────────────
# Cookie loading
# ─────────────────────────────────────────────────────────────────────────────
def load_cookies(path: str = None) -> dict:
    """
    Load cookies from JSON at `path`.
    If `path` is None, uses settings.get_cookies_path().
    Raises:
      - CookieNotFoundError if the file does not exist.
      - CookieInvalidError   if the file isn't valid JSON.
    """
    if path is None:
        from settings import get_cookies_path
        path = get_cookies_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise CookieNotFoundError(f"Cookie file not found at {path}")
    except json.JSONDecodeError as e:
        raise CookieInvalidError(f"Invalid JSON in cookie file: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Authentication check
# ─────────────────────────────────────────────────────────────────────────────
async def is_logged_in(session: aiohttp.ClientSession, url: str) -> bool:
    """
    Return True if fetching `url` with this session shows a /profile link,
    indicating the user is authenticated.
    """
    # Debug: show which cookies we're sending
    sent = session.cookie_jar.filter_cookies(url)
    print(f"   ↳ Cookies sent: {{ {', '.join(f'{c.key}={c.value}' for c in sent.values())} }}")

    # Fetch the page
    print(f"🔍 [Auth] Fetching full page: {url}")
    resp = await session.get(url)
    resp.raise_for_status()
    print(f"   ↳ Status code: {resp.status}")

    # Parse HTML
    html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")

    # Look for any <a href=".../profile?...">
    anchors = soup.find_all("a", href=True)
    print(f"🔗 [Auth] Scanning {len(anchors)} links for '/profile'…")
    for a in anchors:
        href = a["href"]
        full = urljoin(url, href)
        path = urlparse(full).path.lower()
        if path.startswith("/profile"):
            print(f"   ↳ Found profile link: {full}")
            print("✅ [Auth] Final decision: LOGGED IN\n")
            return True

    print("❌ [Auth] No '/profile' link found. ANONYMOUS\n")
    return False
