import os
import json
from typing import Dict, List, Optional

class State:
    """
    Manages crawl state (URLs) and asset cache.
    crawl_state.json format: [
        ["url", "status", retries, "last_error"],
        ...
    ]
    assets_cache.json format: {
        "resource_url": "local_path",
        ...
    }
    """
    def __init__(self, config, state_path: Optional[str]=None, cache_path: Optional[str]=None):
        self.config = config
        self.state_path = state_path or os.path.join(os.getcwd(), "crawl_state.json")
        self.cache_path = cache_path or os.path.join(os.getcwd(), "assets_cache.json")
        self.urls: Dict[str, Dict] = {}
        self.assets_cache: Dict[str, str] = {}
        self.change_count = 0
        # Carrega estado de disco
        self._load()

    def _load(self):
        # Load crawl_state.json
        if os.path.exists(self.state_path):
            with open(self.state_path, "r", encoding="utf-8") as f:
                try:
                    entries: List[List] = json.load(f)
                except json.JSONDecodeError:
                    entries = []
            for url, status, retries, last_error in entries:
                self.urls[url] = {
                    "status": status,
                    "retries": retries,
                    "last_error": last_error,
                }
        # Load assets_cache.json
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                try:
                    self.assets_cache = json.load(f)
                except json.JSONDecodeError:
                    self.assets_cache = {}

    def save(self):
        """Persiste crawl_state.json e assets_cache.json."""
        # crawl_state.json
        entries = [
            [url, data["status"], data["retries"], data["last_error"]]
            for url, data in self.urls.items()
        ]
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False)
        # assets_cache.json
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.assets_cache, f, ensure_ascii=False)
        self.change_count = 0

    def _maybe_save(self):
        if self.change_count >= self.config.save_every:
            self.save()

    def add_url(self, url: str):
        """Adiciona URL nova como pending."""
        if url not in self.urls:
            self.urls[url] = {"status": "pending", "retries": 0, "last_error": None}
            self.change_count += 1
            self._maybe_save()

    def get_next_url(self) -> Optional[str]:
        """Retorna próxima URL pending e marca como in_progress."""
        for url, data in self.urls.items():
            if data["status"] == "pending":
                data["status"] = "in_progress"
                self.change_count += 1
                self._maybe_save()
                return url
        return None

    def update_after_fetch(self, url: str, success: bool, error: Optional[str] = None):
        """Atualiza status após tentativa de fetch."""
        entry = self.urls.get(url)
        if not entry:
            return
        if success:
            entry["status"] = "done"
            entry["last_error"] = None
        else:
            entry["retries"] += 1
            entry["last_error"] = error
            if entry["retries"] >= self.config.retry_limit:
                entry["status"] = "error"
            else:
                entry["status"] = "pending"
        self.change_count += 1
        self._maybe_save()

    def get_asset(self, resource_url: str) -> Optional[str]:
        """Retorna caminho local se já estiver no cache, senão None."""
        return self.assets_cache.get(resource_url)

    def add_asset(self, resource_url: str, local_path: str):
        """Adiciona recurso ao cache."""
        if resource_url not in self.assets_cache:
            self.assets_cache[resource_url] = local_path
            self.change_count += 1
            self._maybe_save()