import os
import json
from typing import Dict, List, Optional
from urllib.parse import urlparse
import asyncio

# ─── Compact persistence ──────────────────────────────────────────────────────
# p=pending • i=in_progress • l=listed(discovered) • d=downloaded • e=error
CODE2TEXT = {"p": "pending", "i": "in_progress", "l": "listed",
             "d": "downloaded", "e": "error"}
TEXT2CODE = {v: k for k, v in CODE2TEXT.items()}

def base_path(full_url: str) -> str:
    """Return only '/f1…' part – drop scheme, host and fragment."""
    parsed = urlparse(full_url)
    return parsed.path + ("?" + parsed.query if parsed.query else "")


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
        self._save_lock = asyncio.Lock()   # <── NOVO
        self._load()

    def _load(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, "r", encoding="utf-8") as f:
                for line in f:
                    path, code, retries, last_err = json.loads(line)
                    # reset in_progress to pending on startup
                    code = "p" if code == "i" else code
                    self.urls[path] = {
                        "status": CODE2TEXT[code],
                        "retries": retries,
                        "last_error": last_err,
                    }

        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                self.assets_cache = json.load(f)

    async def save(self, sort_after: bool = False):
        """
        Persist crawl_state.json (one JSON entry per line) and assets_cache.json,
        optionally sorting the state file after every 1000 entries.
        A single asyncio.Lock serialises writes to avoid OSError 22 on Windows.
        """
        # 1) Build the lines to write
        lines = []
        for path, data in self.urls.items():
            code    = TEXT2CODE[data["status"]]
            retries = data["retries"]
            err     = data["last_error"]
            lines.append(json.dumps([path, code, retries, err], ensure_ascii=False))

        # 2) Sort if requested
        if sort_after:
            lines.sort()

        # 3) Write both files under the lock (single writer)
        async with self._save_lock:          # ← only two new lines
            def _write_files():
                os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
                with open(self.state_path, "w", encoding="utf-8") as sf:
                    sf.write("\n".join(lines))
                with open(self.cache_path, "w", encoding="utf-8") as cf:
                    json.dump(self.assets_cache, cf, ensure_ascii=False)

            await asyncio.to_thread(_write_files)  # ← now indented inside the lock

        self.change_count = 0


    async def _maybe_save(self):
        """
        Auto‐save when change_count threshold hit; 
        trigger sort every time pending_count() % 1000 == 0
        """
        if self.change_count >= self.config.save_every:
            sort_flag = self.pending_count() % 1000 == 0
            await self.save(sort_after=sort_flag)
            if sort_flag:
                print("[State] crawl_state.json sorted alphabetically.")

    async def add_url(self, url: str):
        if url not in self.urls:
            self.urls[url] = {"status": "pending", "retries": 0, "last_error": None}
            self.change_count += 1
            await self._maybe_save()

    # called when HTML fetched & links extracted
    async def mark_discovered(self, path: str):
        entry = self.urls.get(path)
        if entry and entry["status"] != "downloaded":
            entry["status"] = "listed"   # ou código "l" consoante optaste
            self.change_count += 1
            await self._maybe_save()

    # called after rewrite + asset download
    async def mark_downloaded(self, path: str):
        entry = self.urls.get(path)
        if entry:
            entry["status"] = "downloaded"   # ou "d"
            entry["last_error"] = None
            self.change_count += 1
            await self._maybe_save()

    async def get_next(self, phase: str):
        wanted = "pending" if phase == "discover" else "listed"
        for url, data in self.urls.items():
            if data["status"] == wanted:
                data["status"] = "in_progress"
                self.change_count += 1
                await self._maybe_save()
                return url
        return None

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
            entry["status"] = "downloaded"
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

    def pending_count(self) -> int:
        """Return the number of URLs still in 'pending' status."""
        return sum(1 for v in self.urls.values() if v["status"] == "pending")

    async def add_asset(self, resource_url: str, local_path: str):
        """Record a downloaded asset in the cache (if not already recorded)."""
        if resource_url not in self.assets_cache:
            self.assets_cache[resource_url] = local_path
            self.change_count += 1
            print(f"[State] Cached asset: {resource_url} -> {local_path}")
            await self._maybe_save()