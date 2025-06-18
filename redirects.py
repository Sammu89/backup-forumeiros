import os, json, asyncio
from typing import Dict

class RedirectMap:
    """Thread-safe read/write wrapper for redirects.json (src → dst)."""

    def __init__(self, path="redirects.json"):
        self.path = path
        self._lock = asyncio.Lock()
        self.map: Dict[str, str] = {}
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.map = json.load(f)

    async def add(self, src: str, dst: str):
        """Record a redirect; src & dst are relative paths like '/t4898n…'."""
        if src == dst or self.map.get(src) == dst:
            return
        async with self._lock:
            self.map[src] = dst
            await asyncio.to_thread(
                lambda m: open(self.path, "w", encoding="utf-8").write(json.dumps(m, ensure_ascii=False, indent=0)),
                self.map,
            )

    def resolve(self, path: str) -> str:
        """Return final target if path is a known redirect, else same path."""
        while path in self.map:
            path = self.map[path]          # follow chains
        return path
# instância global, para importares em todos os lados
redirects = RedirectMap()
