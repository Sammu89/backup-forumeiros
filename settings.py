"""
Runtime configuration shared by all modules.
Set dynamically by main.py before crawling starts.
"""

from urllib.parse import urlparse
from pathlib import Path
from typing import Any, Dict
import os
import json
import yaml

# ────────────────────────────────────────────────
# 🔧 Runtime values (set dynamically in main.py)
# ────────────────────────────────────────────────

BASE_URL: str = ""          # Full scheme+host, e.g. https://myforum.forumeiros.com
BASE_DOMAIN: str = ""       # Just domain, e.g. myforum.forumeiros.com
BACKUP_ROOT: Path = None    # Set to Desktop/<slug> by main.py before use

# ────────────────────────────────────────────────
# 🌐 Helpers for derived values
# ────────────────────────────────────────────────

def get_base_url() -> str:
    """Return BASE_URL or derive it from BASE_DOMAIN."""
    if BASE_URL:
        return BASE_URL
    if BASE_DOMAIN:
        return "https://" + BASE_DOMAIN
    raise RuntimeError("Neither BASE_URL nor BASE_DOMAIN set.")

def get_base_domain() -> str:
    """Return BASE_DOMAIN or derive it from BASE_URL."""
    if BASE_DOMAIN:
        return BASE_DOMAIN
    if BASE_URL:
        return urlparse(BASE_URL).netloc
    raise RuntimeError("Neither BASE_URL nor BASE_DOMAIN set.")

# ────────────────────────────────────────────────
# ⚙️ General crawler config constants
# ────────────────────────────────────────────────

ALLOWED_PARAMS = {"start", "folder", "page_profil"}
BLACKLIST_PARAMS = {"vote", "mode", "friend", "foe", "profil_tabs"}
IGNORED_PREFIXES = ("/admin", "/modcp", "/profile")

# ────────────────────────────────────────────────
# 🗂️ Config and cookies
# ────────────────────────────────────────────────

def get_config_path() -> str:
    if BACKUP_ROOT is None:
        raise RuntimeError("BACKUP_ROOT must be set before accessing config path.")
    return str(BACKUP_ROOT / "config.yaml")

def get_cookies_path() -> str:
    if BACKUP_ROOT is None:
        raise RuntimeError("BACKUP_ROOT must be set before accessing cookies path.")
    return str(BACKUP_ROOT / "cookies.json")


class Config:
    """Immutable configuration object loaded from config.yaml."""
    def __init__(self, data: Dict[str, Any]):
        self.workers: int = data.get("workers", 5)
        self.base_delay: float = data.get("base_delay", 0.5)
        self.min_delay: float = data.get("min_delay", 0.3)
        self.max_delay: float = data.get("max_delay", 8.0)
        self.retry_limit: int = data.get("retry_limit", 3)
        self.save_every: int = data.get("save_every", 100)
        self.user_agent: str = data.get("user_agent", "ForumSMPTBackup/1.0")

def load_config() -> Config:
    """Load config from YAML or create with defaults."""
    default = {
        "workers": 5,
        "base_delay": 0.5,
        "min_delay": 0.3,
        "max_delay": 8.0,
        "retry_limit": 3,
        "save_every": 100,
        "user_agent": "ForumSMPTBackup/1.0"
    }
    path = get_config_path()
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(default, f)
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or default
    return Config(data)

def get_cookies() -> Dict[str, str]:
    """Read cookies from file or return empty dict."""
    path = get_cookies_path()
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def set_cookies(cookies: Dict[str, str]) -> None:
    """Write cookies to file, overwriting existing."""
    path = get_cookies_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)
