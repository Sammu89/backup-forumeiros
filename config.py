import yaml
import json
import os
from typing import Any, Dict

# Paths for configuration and cookies
CONFIG_PATH = os.path.join(os.getcwd(), "config.yaml")
COOKIES_PATH = os.path.join(os.getcwd(), "cookies.json")

class Config:
    """
    Immutable configuration object loaded from config.yaml.
    Attributes correspond to keys in the YAML config file.
    """
    def __init__(self, data: Dict[str, Any]):
        self.workers: int = data.get("workers", 5)
        self.base_delay: float = data.get("base_delay", 0.5)
        self.min_delay: float = data.get("min_delay", 0.3)
        self.max_delay: float = data.get("max_delay", 8.0)
        self.retry_limit: int = data.get("retry_limit", 3)
        self.save_every: int = data.get("save_every", 100)
        self.user_agent: str = data.get("user_agent", "ForumSMPTBackup/1.0")

def load_config() -> Config:
    """
    Load configuration from CONFIG_PATH. If the file does not exist,
    create it with default values and then load.
    """
    default = {
        "workers": 5,
        "base_delay": 0.5,
        "min_delay": 0.3,
        "max_delay": 8.0,
        "retry_limit": 3,
        "save_every": 100,
        "user_agent": "ForumSMPTBackup/1.0"
    }
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            yaml.dump(default, f)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or default
    return Config(data)

def get_cookies() -> Dict[str, str]:
    """
    Read cookie values from COOKIES_PATH.
    Returns an empty dict if file does not exist.
    """
    if not os.path.exists(COOKIES_PATH):
        return {}
    with open(COOKIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def set_cookies(cookies: Dict[str, str]) -> None:
    """
    Write cookie values to COOKIES_PATH.
    Overwrites any existing file.
    """
    with open(COOKIES_PATH, "w", encoding="utf-8") as f:
        json.dump(cookies, f, indent=2)

# Example usage:
# config = load_config()
# cookies = get_cookies()
# set_cookies({"_fa-screen": "...", "fa_sm-portugal_forumeiros_com_sid": "...", ...})