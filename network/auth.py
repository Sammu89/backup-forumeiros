# network/auth.py

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from forum_backup_crawler.config import Settings


class CookieNotFoundError(Exception):
    """Raised when the cookies JSON file cannot be found."""


class CookieInvalidError(Exception):
    """Raised when the cookies file exists but contains invalid JSON."""


def load_cookies(
    path: Optional[Path], settings: Settings
) -> dict[str, str]:
    """
    Load cookies from a JSON file.

    If `path` is None, uses `settings.cookies_file`. The file must exist and
    contain valid JSON mapping cookie names to values.

    :param path: Optional Path to a JSON file.
    :param settings: Settings object (for default cookies_file).
    :returns: Dict of cookie name → value
    :raises CookieNotFoundError: if the file does not exist.
    :raises CookieInvalidError: if the file exists but isn't valid JSON.
    """
    cookie_path = Path(path) if path else settings.cookies_file
    if not cookie_path or not cookie_path.exists():
        raise CookieNotFoundError(f"Cookies file not found: {cookie_path}")
    try:
        text = cookie_path.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, dict):
            raise CookieInvalidError(f"Expected JSON object, got {type(data)}")
    except json.JSONDecodeError as e:
        raise CookieInvalidError(f"Invalid JSON in cookies file: {e}") from e

    # Return only string→string mappings
    return {str(k): str(v) for k, v in data.items()}


async def is_logged_in(
    session: aiohttp.ClientSession, url: str
) -> bool:
    """
    Check if the session is authenticated by fetching `url` and scanning for
    a '/profile' link (common in phpBB/Forumeiros when logged in).

    :param session: aiohttp.ClientSession already configured with cookies.
    :param url: The forum URL to fetch and inspect.
    :returns: True if a profile link is found; False otherwise.
    """
    try:
        async with session.get(url, timeout=30) as resp:
            html = await resp.text()
    except Exception:
        # On network errors, presume not logged in
        return False

    soup = BeautifulSoup(html, "html.parser")
    # Look for any <a href="/profile...">
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/profile"):
            return True
    return False
