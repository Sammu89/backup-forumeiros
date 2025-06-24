# config.py

import tomllib
import tomli_w
from pathlib import Path
from typing import List, Literal, Optional
from contextlib import asynccontextmanager

import aiohttp
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Application settings for Forum Backup Crawler.

    Values can come from:
      1. A TOML file passed to from_file()
      2. Environment variables with the FBC_ prefix
      3. Defaults defined here
    """

    start_urls: List[str] = Field(
        ..., description="List of forum URLs to begin crawling from"
    )
    output_dir: Path = Field(
        ..., description="Base folder to save mirrored site files"
    )
    temp_dir: Optional[Path] = Field(
        None,
        description="Workspace for DB, logs, cookies; defaults to output_dir/'temp'",
    )
    concurrency: int = Field(8, description="Number of async workers")
    depth_limit: int = Field(4, description="Max link-following depth")
    rate_limiter: Literal["adaptive", "fixed", "token_bucket"] = Field(
        "adaptive", description="Throttle strategy"
    )
    cookies_file: Optional[Path] = Field(
        None, description="Path to JSON file with browser cookies"
    )
    user_agent: str = Field(
        "ForumBackupCrawler/1.0", description="User-Agent header for HTTP requests"
    )

    # Pydantic‐v2 config for env vars
    model_config = {
        "env_prefix": "FBC_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @classmethod
    def from_file(cls, path: Optional[Path] = None) -> "Settings":
        """
        Load settings from a TOML file (if path given), then override
        with any environment variables. Finally, ensure temp_dir is set.
        """
        data: dict = {}
        if path:
            toml_text = Path(path).read_text(encoding="utf-8")
            data = tomllib.loads(toml_text)

        settings = cls(**data)

        # Default temp_dir if unset
        if settings.temp_dir is None:
            settings.temp_dir = settings.output_dir / "temp"

        return settings

    def save(self) -> None:
        """
        Write the currently active settings to temp_dir/config.toml
        so future runs see the same configuration.
        """
        # Ensure temp_dir exists
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Dump all fields to TOML
        toml_str = tomli_w.dumps(self.model_dump())

        config_path = self.temp_dir / "config.toml"
        config_path.write_text(toml_str, encoding="utf-8")

    @asynccontextmanager
    async def http_session(self, **kwargs):
        """
        Async context manager yielding an aiohttp.ClientSession
        with proper headers and cookies.

        Usage:
            async with settings.http_session(cookies=my_cookies) as session:
                ...
        """
        headers = {"User-Agent": self.user_agent}
        cookies = kwargs.get("cookies", None)

        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            yield session
