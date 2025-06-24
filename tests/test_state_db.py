# tests/test_state_db.py

import pytest
import asyncio
from pathlib import Path

from forum_backup_crawler.storage.state_db import StateDB


@pytest.mark.asyncio
async def test_add_and_pop_and_done(tmp_path):
    db_path = tmp_path / "state.db"
    db = StateDB(db_path)
    await db.connect()
    await db.reset_in_progress()

    # Add seed URLs
    urls = ["a", "b", "c"]
    await db.add_seed_urls(urls, depth=0)
    assert await db.pending_count() == 3

    # Pop one, should be "a"
    first = await db.pop_pending()
    assert first == ("a", 0)
    assert await db.pending_count() == 2

    # Mark done
    await db.mark_done("a", "a.html")

    # Pop remaining: "b", then "c"
    second = await db.pop_pending()
    third = await db.pop_pending()
    assert second[0] == "b"
    assert third[0] == "c"
    assert await db.pending_count() == 0


@pytest.mark.asyncio
async def test_record_error(tmp_path):
    db = StateDB(tmp_path / "state.db")
    await db.connect()
    await db.reset_in_progress()

    await db.add_seed_urls(["x"], depth=0)
    popped = await db.pop_pending()
    assert popped == ("x", 0)

    await db.record_error("x", "oops")
    # No pending left
    assert await db.pending_count() == 0


@pytest.mark.asyncio
async def test_redirect_and_resolve(tmp_path):
    db = StateDB(tmp_path / "state.db")
    await db.connect()
    await db.reset_in_progress()

    # Chain A->B->C
    await db.add_redirect("A", "B")
    await db.add_redirect("B", "C")
    # Resolve should follow to C
    result = await db.resolve("A")
    assert result == "C"
    # Non-existing src returns itself
    assert await db.resolve("X") == "X"


@pytest.mark.asyncio
async def test_asset_cache(tmp_path):
    db = StateDB(tmp_path / "state.db")
    await db.connect()
    await db.reset_in_progress()

    # First cache returns True
    ok1 = await db.cache_asset("u1", "path1")
    assert ok1 is True
    # Second cache same URL returns False
    ok2 = await db.cache_asset("u1", "path1")
    assert ok2 is False
    # get_asset returns the stored path
    path = await db.get_asset("u1")
    assert path == "path1"
