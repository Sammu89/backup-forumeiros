# storage/state_db.py

from __future__ import annotations
import asyncio
from pathlib import Path
from typing import Iterable, Optional, Tuple

import aiosqlite


class StateDB:
    """
    SQLite-backed persistent state for URLs, assets, and redirects.
    """

    def __init__(self, db_path: Path) -> None:
        """
        :param db_path: Path to the SQLite database file.
        """
        self._db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """
        Open the SQLite connection, initialize tables, and set WAL mode.
        """
        self._conn = await aiosqlite.connect(str(self._db_path))
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                url TEXT PRIMARY KEY,
                status TEXT CHECK(status IN ('pending','in_progress','done','error')),
                local_path TEXT,
                depth INTEGER,
                error_text TEXT
            );
        """)
        await self._conn.execute("CREATE INDEX IF NOT EXISTS urls_status_idx ON urls(status);")
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                url TEXT PRIMARY KEY,
                local_path TEXT
            );
        """)
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS redirects (
                src TEXT PRIMARY KEY,
                dst TEXT
            );
        """)
        await self._conn.commit()

    async def reset_in_progress(self) -> None:
        """
        Reset any URLs left in 'in_progress' back to 'pending'.
        Useful after a crash or shutdown.
        """
        assert self._conn
        await self._conn.execute(
            "UPDATE urls SET status='pending' WHERE status='in_progress';"
        )
        await self._conn.commit()

    async def add_seed_urls(self, urls: Iterable[str], depth: int = 0) -> None:
        """
        Add seed URLs at the given depth, without overwriting existing entries.
        """
        assert self._conn
        async with self._lock:
            await self._conn.executemany(
                "INSERT OR IGNORE INTO urls (url, status, depth) VALUES (?, 'pending', ?);",
                [(url, depth) for url in urls],
            )
            await self._conn.commit()

    async def pop_pending(self) -> Optional[Tuple[str, int]]:
        """
        Atomically pop the next pending URL and mark it in_progress.
        Returns a tuple (url, depth), or None if no pending URLs.
        """
        assert self._conn
        async with self._lock:
            cursor = await self._conn.execute(
                "SELECT url, depth FROM urls WHERE status='pending' ORDER BY depth, url LIMIT 1;"
            )
            row = await cursor.fetchone()
            if row is None:
                return None
            url, depth = row
            await self._conn.execute(
                "UPDATE urls SET status='in_progress' WHERE url = ?;", (url,)
            )
            await self._conn.commit()
            return url, depth

    async def mark_done(self, url: str, local_path: str) -> None:
        """
        Mark the URL as done and record its local file path.
        """
        assert self._conn
        await self._conn.execute(
            "UPDATE urls SET status='done', local_path = ? WHERE url = ?;",
            (local_path, url),
        )
        await self._conn.commit()

    async def record_error(self, url: str, error_text: str) -> None:
        """
        Mark the URL as errored and record the error message.
        """
        assert self._conn
        await self._conn.execute(
            "UPDATE urls SET status='error', error_text = ? WHERE url = ?;",
            (error_text, url),
        )
        await self._conn.commit()

    async def add_redirect(self, src: str, dst: str) -> None:
        """
        Record a redirect from src → dst.
        """
        assert self._conn
        await self._conn.execute(
            "INSERT OR IGNORE INTO redirects (src, dst) VALUES (?, ?);", (src, dst)
        )
        await self._conn.commit()

    async def resolve(self, src: str) -> str:
        """
        Resolve a src path through any redirect chain to the final destination.
        """
        assert self._conn
        visited = set()
        current = src
        while True:
            if current in visited:
                break
            visited.add(current)
            cursor = await self._conn.execute(
                "SELECT dst FROM redirects WHERE src = ?;", (current,)
            )
            row = await cursor.fetchone()
            if row is None:
                break
            (current,) = row
        return current

    async def cache_asset(self, url: str, local_path: str) -> bool:
        """
        Record that an asset URL has been saved to local_path.
        Returns False if the URL was already cached, True otherwise.
        """
        assert self._conn
        cursor = await self._conn.execute(
            "SELECT 1 FROM assets WHERE url = ?;", (url,)
        )
        exists = await cursor.fetchone()
        if exists:
            return False
        await self._conn.execute(
            "INSERT INTO assets (url, local_path) VALUES (?, ?);", (url, local_path)
        )
        await self._conn.commit()
        return True

    async def get_asset(self, url: str) -> Optional[str]:
        """
        Get the local_path for a cached asset URL, or None if not cached.
        """
        assert self._conn
        cursor = await self._conn.execute(
            "SELECT local_path FROM assets WHERE url = ?;", (url,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None

    async def pending_count(self) -> int:
        """
        Return the number of URLs still in 'pending' state.
        """
        assert self._conn
        cursor = await self._conn.execute(
            "SELECT COUNT(*) FROM urls WHERE status = 'pending';"
        )
        (count,) = await cursor.fetchone()
        return count
