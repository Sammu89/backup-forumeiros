# core/scheduler.py

from __future__ import annotations
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from forum_backup_crawler.config import Settings
from forum_backup_crawler.network.rate_limit import get_limiter, RateLimiter
from forum_backup_crawler.network.http_client import HTTPClient
from forum_backup_crawler.network.auth import load_cookies, CookieNotFoundError
from forum_backup_crawler.storage.state_db import StateDB
from forum_backup_crawler.storage.path_mapper import PathMapper
from forum_backup_crawler.core.worker import worker


@dataclass
class Context:
    """
    Carries shared components for each worker:
      - settings: global config
      - db:        the SQLite-backed state store
      - client:    the HTTP client with throttling
      - limiter:   the RateLimiter strategy
      - mapper:    URL ↔ filesystem-path logic
    """
    settings: Settings
    db: StateDB
    client: HTTPClient
    limiter: RateLimiter
    mapper: PathMapper


async def run(settings: Settings) -> None:
    """
    Orchestrate the entire crawl:
      1. Prepare directories
      2. Load cookies & build HTTP client
      3. Initialize state database
      4. Seed starting URLs
      5. Spawn worker tasks
      6. Wait for completion and clean up
    """

    # 1. Ensure output & temp folders exist
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)

    # 2. Load cookies for auth (if provided)
    try:
        cookies = load_cookies(settings.cookies_file, settings)
    except CookieNotFoundError:
        cookies = {}

    # 3. Build rate limiter strategy
    limiter = get_limiter(
        settings.rate_limiter,
        base_delay=0.5,
        min_delay=0.1,
        max_delay=5.0,
        max_workers=settings.concurrency,
    )

    # 4. Start HTTP client with headers & cookies
    client = HTTPClient(limiter, settings.user_agent, cookies)
    await client.start()

    # 5. Initialize the SQLite-backed state DB
    db_path = settings.temp_dir / "state.db"
    db = StateDB(db_path)
    await db.connect()
    await db.reset_in_progress()           # clear any crashed runs
    await db.add_seed_urls(settings.start_urls)  # enqueue the first URLs

    # 6. Prepare path-mapping logic
    mapper = PathMapper(settings.output_dir)

    # 7. Bundle everything into our Context
    ctx = Context(settings, db, client, limiter, mapper)

    # 8. Launch async workers
    tasks = [
        asyncio.create_task(worker(ctx, idx + 1), name=f"worker-{idx+1}")
        for idx in range(settings.concurrency)
    ]

    # 9. Wait for all workers to finish
    await asyncio.gather(*tasks)

    # 10. Clean up the HTTP session
    await client.close()
