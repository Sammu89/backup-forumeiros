# tests/test_auth.py

import json
import pytest
from pathlib import Path
from aiohttp import ClientSession
from aioresponses import aioresponses

from forum_backup_crawler.network.auth import (
    load_cookies,
    CookieNotFoundError,
    CookieInvalidError,
    is_logged_in,
)


def test_load_cookies_success(tmp_path):
    data = {"sessionid": "abc123", "userid": "42"}
    fp = tmp_path / "cookies.json"
    fp.write_text(json.dumps(data), encoding="utf-8")

    # Pass None to use settings, but override settings.cookies_file for test
    from forum_backup_crawler.config import Settings
    settings = Settings(start_urls=["x"], output_dir=tmp_path / "out")
    settings.cookies_file = fp

    cookies = load_cookies(None, settings)
    assert cookies == data


def test_load_cookies_not_found(tmp_path):
    from forum_backup_crawler.config import Settings
    settings = Settings(start_urls=["x"], output_dir=tmp_path / "out")
    settings.cookies_file = tmp_path / "nope.json"

    with pytest.raises(CookieNotFoundError):
        load_cookies(None, settings)


def test_load_cookies_invalid_json(tmp_path):
    fp = tmp_path / "cookies.json"
    fp.write_text("not json", encoding="utf-8")
    from forum_backup_crawler.config import Settings
    settings = Settings(start_urls=["x"], output_dir=tmp_path / "out")
    settings.cookies_file = fp

    with pytest.raises(CookieInvalidError):
        load_cookies(None, settings)


@pytest.mark.asyncio
async def test_is_logged_in_detects_profile(tmp_path):
    url = "https://example.com"
    html = '<html><body><a href="/profile?mode=edit">Edit Profile</a></body></html>'

    with aioresponses() as m:
        m.get(url, status=200, body=html)

        async with ClientSession() as sess:
            assert await is_logged_in(sess, url)

@pytest.mark.asyncio
async def test_is_logged_in_not_found(tmp_path):
    url = "https://example.com"
    html = '<html><body><p>No profile here</p></body></html>'

    with aioresponses() as m:
        m.get(url, status=200, body=html)

        async with ClientSession() as sess:
            assert not await is_logged_in(sess, url)
