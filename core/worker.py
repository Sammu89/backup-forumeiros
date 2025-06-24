# core/worker.py

from __future__ import annotations
import asyncio
import logging
from typing import Optional

from forum_backup_crawler.processing.html_rewriter import rewrite
from forum_backup_crawler.storage.path_mapper import PathMapper
from forum_backup_crawler.core.scheduler import Context

logger = logging.getLogger(__name__)


async def worker(ctx: Context, worker_id: int) -> None:
    """
    Single crawler worker loop:
      1. Pop a pending URL from the DB.
      2. Fetch its content.
      3. Depending on the result, process HTML, assets, or record errors.
      4. Repeat until no URLs are pending.
    """
    db = ctx.db
    client = ctx.client
    limiter = ctx.limiter
    mapper = ctx.mapper
    settings = ctx.settings

    while True:
        # 1. Get next pending URL
        pop = await db.pop_pending()
        if pop is None:
            logger.debug(f"Worker {worker_id}: no more URLs, exiting.")
            return

        url, depth = pop
        logger.debug(f"Worker {worker_id}: processing {url} (depth {depth})")

        # 2. Fetch content (text or bytes)
        status, text, final_url = await client.fetch_text(url)
        if status == 0:
            # network error
            await db.record_error(url, "network error")
            continue

        content_type = None
        if status < 300 and text is not None:
            content_type = "html"

        # 3a. HTML page
        if content_type == "html":
            try:
                new_html, new_links = rewrite(text, final_url, ctx)
                # compute local path and save
                local_path = mapper.url_to_path(final_url)
                (settings.output_dir / local_path).write_text(new_html, encoding="utf-8")

                # mark done and record new links
                await db.mark_done(url, str(local_path))
                if depth + 1 <= settings.depth_limit:
                    await db.add_seed_urls(new_links, depth + 1)
            except Exception as e:
                logger.exception(f"Worker {worker_id}: error processing HTML for {url}")
                await db.record_error(url, str(e))
            continue

        # 3b. Binary asset (we treat via cache_asset)
        if text is None:
            # fetch_bytes could be used, but cache_asset handles writing
            try:
                cached = await db.cache_asset(url, None)  # placeholder: logic inside will fetch
                if not cached:
                    logger.debug(f"Worker {worker_id}: asset already cached {url}")
            except Exception as e:
                logger.exception(f"Worker {worker_id}: error saving asset {url}")
                await db.record_error(url, str(e))
            continue

        # 3c. Redirect (3xx)
        if 300 <= status < 400:
            # record redirect chain
            await db.add_redirect(url, final_url)
            await db.mark_done(url, final_url)  # treat as done
            continue

        # 3d. Other HTTP errors
        await db.record_error(url, f"HTTP {status}")
