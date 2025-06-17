import os
import json
import asyncio
from typing import Dict, List

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
    def __init__(self, config, state_path=None, cache_path=None):
        self.config = config
        self.state_path = state_path or os.path.join(os.getcwd(), "crawl_state.json")
        self.cache_path = cache_path or os.path.join(os.getcwd(), "assets_cache.json")
        self.urls: Dict[str, Dict] = {}
        self.assets_cache: Dict[str, str] = {}
        self.change_count = 0
        self.lock = asyncio.Lock()
        # load existing state
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._load())

    async def _load(self):
        # Load crawl_state
        if os.path.exists(self.state_path):
            with open(self.state_path, "r", encoding="utf-8") as f:
                entries: List[List] = json.load(f)
            for url, status, retries, last_error in entries:
                self.urls[url] = {
                    "status": status,
                    "retries": retries,
                    "last_error": last_error,
                }
        # Load asset cache
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                self.assets_cache = json.load(f)

    async def save(self):
        """Persist both crawl state and assets cache to disk."""
        async with self.lock:
            # Save crawl_state.json
            entries = [
                [url, data["status"], data["retries"], data["last_error"]]
                for url, data in self.urls.items()
            ]
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False)
            # Save assets_cache.json
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.assets_cache, f, ensure_ascii=False)
            self.change_count = 0

    async def _maybe_save(self):
        if self.change_count >= self.config.save_every:
            await self.save()

    async def add_url(self, url: str):
        """Add new URL to crawl state as pending."""
        async with self.lock:
            if url not in self.urls:
                self.urls[url] = {"status": "pending", "retries": 0, "last_error": None}
                self.change_count += 1
        await self._maybe_save()

    async def get_next_url(self) -> str:
        """Get next pending URL and mark it in_progress."""
        async with self.lock:
            for url, data in self.urls.items():
                if data["status"] == "pending":
                    data["status"] = "in_progress"
                    self.change_count += 1
                    next_url = url
                    break
            else:
                return None
        await self._maybe_save()
        return next_url

    async def update_after_fetch(self, url: str, success: bool, error: str = None):
        """Update URL status after fetch attempt."""
        async with self.lock:
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
        await self._maybe_save()

    def get_asset(self, resource_url: str) -> str:
        """Return local path if asset already downloaded, else None."""
        return self.assets_cache.get(resource_url)

    async def add_asset(self, resource_url: str, local_path: str):
        """Add downloaded resource to cache."""
        async with self.lock:
            if resource_url not in self.assets_cache:
                self.assets_cache[resource_url] = local_path
                self.change_count += 1
        await self._maybe_save()
