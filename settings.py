"""
+Runtime configuration set by main.py —
+used by all other modules to know where to write files and what URL to crawl.
+"""
from urllib.parse import urlparse
# These get filled in main.py **before** the crawler starts.
BASE_URL: str = ""          # full scheme+host, e.g. https://myforum.forumeiros.com
BASE_DOMAIN: str = ""       # just host, e.g. myforum.forumeiros.com
BACKUP_ROOT = None          # Path object pointing to Desktop/<slug>


def get_base_url() -> str:
    """
    Return the full BASE_URL; if unset, derive from BASE_DOMAIN.
    """
    if BASE_URL:
        return BASE_URL
    if BASE_DOMAIN:
        return "https://" + BASE_DOMAIN
    raise RuntimeError("Neither BASE_URL nor BASE_DOMAIN set in settings.py")


def get_base_domain() -> str:
    """
    Return the BASE_DOMAIN; if unset, derive from BASE_URL.
    """
    if BASE_DOMAIN:
        return BASE_DOMAIN
    if BASE_URL:
        return urlparse(BASE_URL).netloc
    raise RuntimeError("Neither BASE_URL nor BASE_DOMAIN set in settings.py")



# Configuration constants
ALLOWED_PARAMS = {"start", "folder", "page_profil"}
BLACKLIST_PARAMS = {"vote", "mode", "friend", "foe", "profil_tabs"}
IGNORED_PREFIXES = ("/admin", "/modcp", "/profile")