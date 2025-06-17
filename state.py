import os
import json
from typing import Dict, List, Optional
import asyncio

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
    def __init__(self, config, state_path: Optional[str] = None, cache_path: Optional[str] = None):
        self.config = config
        self.state_path = state_path or os.path.join(os.getcwd(), "crawl_state.json")
        self.cache_path = cache_path or os.path.join(os.getcwd(), "assets_cache.json")
        self.urls: Dict[str, Dict] = {}
        self.assets_cache: Dict[str, str] = {}
        self.change_count = 0
        # Load state from disk
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
                # If any URL was left in progress (e.g., after an interrupted crawl), reset it to pending
                if status == "in_progress":
                    status = "pending"
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

    async def save(self):
        """Persist crawl state and asset cache to disk asynchronously."""
        # Prepare snapshot of current state
        entries = [
            [url, data["status"], data["retries"], data["last_error"]]
            for url, data in self.urls.items()
        ]
        assets_data = dict(self.assets_cache)
        try:
            # Write files in a separate thread to avoid blocking
            def write_state_and_cache(entries_data, assets_data_local):
                with open(self.state_path, "w", encoding="utf-8") as sf:
                    json.dump(entries_data, sf, ensure_ascii=False)
                with open(self.cache_path, "w", encoding="utf-8") as cf:
                    json.dump(assets_data_local, cf, ensure_ascii=False)
            await asyncio.to_thread(write_state_and_cache, entries, assets_data)
            self.change_count = 0
        except Exception as e:
            print(f"[State] Error saving state to disk: {e}")

    async def _maybe_save(self):
        """Save state to disk if change_count has reached the threshold."""
        if self.change_count >= self.config.save_every:
            await self.save()
            print(f"[Auto-save] Reached {self.config.save_every} changes, state and cache saved.")

    async def add_url(self, url: str):
        """Add a new URL as pending if not already seen."""
        if url not in self.urls:
            self.urls[url] = {"status": "pending", "retries": 0, "last_error": None}
            self.change_count += 1
            print(f"[State] Added URL to queue: {url}")
            await self._maybe_save()

    async def get_next_url(self) -> Optional[str]:
        """Retrieve the next pending URL and mark it in progress (returns None if none pending)."""
        for url, data in list(self.urls.items()):
            if data["status"] == "pending":
                data["status"] = "in_progress"
                self.change_count += 1
                print(f"[State] Dispatching URL: {url} (status -> in_progress)")
                await self._maybe_save()
                return url
        return None

    async def update_after_fetch(self, url: str, success: bool, error: Optional[str] = None):
        """Update status of a URL after attempting fetch (mark done, or schedule retry/error)."""
        entry = self.urls.get(url)
        if not entry:
            return
        if success:
            entry["status"] = "done"
            entry["last_error"] = None
            print(f"[State] Marked done: {url}")
        else:
            entry["retries"] += 1
            entry["last_error"] = error
            if entry["retries"] >= self.config.retry_limit:
                entry["status"] = "error"
                print(f"[State] Marked failed: {url} after {entry['retries']} attempts (error: {error})")
            else:
                entry["status"] = "pending"
                print(f"[State] Will retry {url} (attempt {entry['retries']} of {self.config.retry_limit}), error: {error}")
        self.change_count += 1
        await self._maybe_save()

    def get_asset(self, resource_url: str) -> Optional[str]:
        """If asset URL already downloaded, return local path, else None."""
        return self.assets_cache.get(resource_url)

    async def add_asset(self, resource_url: str, local_path: str):
        """Record a downloaded asset in the cache (if not already recorded)."""
        if resource_url not in self.assets_cache:
            self.assets_cache[resource_url] = local_path
            self.change_count += 1
            print(f"[State] Cached asset: {resource_url} -> {local_path}")
            await self._maybe_save()