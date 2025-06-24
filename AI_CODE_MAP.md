# 🧠 AI-Friendly Code Structure Analysis

*Generated for AI model comprehension and code modification assistance*

## 🌲 Project Structure & Complexity Map

```text
📊 Legend:
🟢 Low Complexity (≤10)  🟡 Medium (11-20)  🔴 High (>20)
📃 Small (<100 lines)   📄 Medium (100-500)  📚 Large (>500)
🏛️ Class  ⚙️ Function  ⚡ Async  🔶 Abstract  📁 Directory

PROJECT_ROOT/
├── 📃 __main__.py 🟢 (0 lines, complexity: 0)
├── 📃 cli.py 🟢 (0 lines, complexity: 0)
├── 📃 config.py 🟢 (99 lines, complexity: 0)
│   ├── 🏛️ Settings (line 13, 2 methods)
├── 📁 core
│   ├── 📃 scheduler.py 🟢 (92 lines, complexity: 0)
│   │   ├── 🏛️ Context (line 19, 0 methods)
│   │   └── ⚡ run 🟢 (line 35, complexity: 2)
│   └── 📃 worker.py 🟢 (87 lines, complexity: 0)
│       └── ⚡ worker 🔴 (line 15, complexity: 13)
├── 📃 logging_config.py 🟢 (0 lines, complexity: 0)
├── 📁 network
│   ├── 📃 auth.py 🟢 (76 lines, complexity: 0)
│   │   ├── 🏛️ CookieNotFoundError (line 14, 0 methods)
│   │   ├── 🏛️ CookieInvalidError (line 18, 0 methods)
│   │   └── ⚙️ load_cookies 🟢 (line 22, complexity: 5)
│   │   └── ⚡ is_logged_in 🟢 (line 52, complexity: 4)
│   ├── 📃 http_client.py 🟢 (85 lines, complexity: 0)
│   │   ├── 🏛️ HTTPClient (line 11, 1 methods)
│   └── 📄 rate_limit.py 🟢 (109 lines, complexity: 0)
│       ├── 🏛️ RateLimiter (line 6, 2 methods)
│       ├── 🏛️ AdaptiveLimiter (line 41, 3 methods)
│       ├── 🏛️ FixedLimiter (line 87, 3 methods)
│       └── ⚙️ get_limiter 🟢 (line 24, complexity: 2)
├── 📁 processing
│   ├── 📃 crawler.py 🟢 (0 lines, complexity: 0)
│   └── 📃 html_rewriter.py 🟢 (0 lines, complexity: 0)
├── 📁 storage
│   ├── 📃 assets.py 🟢 (0 lines, complexity: 0)
│   ├── 📃 path_mapper.py 🟢 (0 lines, complexity: 0)
│   └── 📄 state_db.py 🟢 (187 lines, complexity: 0)
│       ├── 🏛️ StateDB (line 11, 1 methods)
├── 📁 tests
│   ├── 📃 test_auth.py 🟢 (71 lines, complexity: 0)
│   │   └── ⚙️ test_load_cookies_success 🟢 (line 17, complexity: 1)
│   │   └── ⚙️ test_load_cookies_not_found 🟢 (line 31, complexity: 1)
│   │   └── ⚙️ test_load_cookies_invalid_json 🟢 (line 40, complexity: 1)
│   │   └── ⚡ test_is_logged_in_detects_profile 🟢 (line 52, complexity: 1)
│   │   └── ⚡ test_is_logged_in_not_found 🟢 (line 63, complexity: 1)
│   ├── 📃 test_config.py 🟢 (0 lines, complexity: 0)
│   ├── 📃 test_path_mapper.py 🟢 (0 lines, complexity: 0)
│   ├── 📃 test_rate_limit.py 🟢 (30 lines, complexity: 0)
│   │   └── ⚡ test_fixed_limiter_keeps_delay_and_workers 🟢 (line 6, complexity: 1)
│   │   └── ⚡ test_adaptive_backoff_and_recovery 🟢 (line 17, complexity: 2)
│   └── 📃 test_state_db.py 🟢 (83 lines, complexity: 0)
│       └── ⚡ test_add_and_pop_and_done 🟢 (line 11, complexity: 1)
│       └── ⚡ test_record_error 🟢 (line 39, complexity: 1)
│       └── ⚡ test_redirect_and_resolve 🟢 (line 54, complexity: 1)
│       └── ⚡ test_asset_cache 🟢 (line 70, complexity: 1)
└── 📁 utils
    ├── 📃 timeit.py 🟢 (0 lines, complexity: 0)
    └── 📃 typing.py 🟢 (0 lines, complexity: 0)
```

## 📊 Comprehensive Project Metrics

- **Python Files Analyzed:** 21
- **Total Lines of Code:** 919
- **Classes Defined:** 9
- **Top-Level Functions:** 16
- **Class Methods:** 12
- **Average File Complexity:** 0.0
- **External Dependencies:** 17
- **Most Complex Files:** __main__.py, cli.py, config.py

## 🔗 Dependency Overview

- **__future__** → Used in 6 files
- **aiohttp** → Used in 4 files
- **aioresponses** → Used in 1 files
- **aiosqlite** → Used in 1 files
- **asyncio** → Used in 7 files
- **bs4** → Used in 1 files
- **contextlib** → Used in 1 files
- **dataclasses** → Used in 1 files
- **forum_backup_crawler** → Used in 7 files
- **json** → Used in 2 files
- **logging** → Used in 1 files
- **pathlib** → Used in 6 files
- **pydantic** → Used in 1 files
- **pytest** → Used in 3 files
- **tomli_w** → Used in 1 files
- **tomllib** → Used in 1 files
- **typing** → Used in 7 files

---

## 📄 File Analysis: `__main__.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `cli.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `config.py`

**Overview:** 99 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiohttp`
- `tomli_w`
- `tomllib`

**From Imports:**
- `from contextlib import asynccontextmanager`
- `from pathlib import Path`
- `from pydantic import BaseSettings, Field`
- `from typing import List, Literal, Optional`

### 🏛️ Class Definitions

#### `Settings` extends BaseSettings - lines 13-99
**Purpose:** Application settings for Forum Backup Crawler.

Values can come from:
  1. A TOML file passed to from_file()
  2. Environment variables with the FBC_ ...

**Class Variables:**
- `model_config` = {'env_prefix': 'FBC_', 'env_file': '.env', 'env_file_encoding': 'utf-8'}

**Methods:**
- `from_file(cls, path: Optional[Path]) -> 'Settings'` 🟢 (lines 53-69, complexity: 3) @classmethod
  - 📝 Load settings from a TOML file (if path given), then override
with any environment variables. Finall...
  - 🔗 Calls: `Path, Path(path).read_text, cls, tomllib.loads`
- `save(self) -> None` 🟢 (lines 71-83, complexity: 1)
  - 📝 Write the currently active settings to temp_dir/config.toml
so future runs see the same configuratio...
  - 🔗 Calls: `config_path.write_text, self.model_dump, self.temp_dir.mkdir, tomli_w.dumps`

### 🌐 External API Usage

- **Path(path)**: `Path(path).read_text`
- **aiohttp**: `aiohttp.ClientSession`
- **config_path**: `config_path.write_text`
- **kwargs**: `kwargs.get`
- **tomli_w**: `tomli_w.dumps`
- **tomllib**: `tomllib.loads`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `Field, Path, cls, self.model_dump, self.temp_dir.mkdir`

**External API calls:** `Path(path).read_text, aiohttp.ClientSession, config_path.write_text, kwargs.get, tomli_w.dumps, tomllib.loads`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `core/scheduler.py`

**Overview:** 92 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`

**From Imports:**
- `from __future__ import annotations`
- `from dataclasses import dataclass`
- `from forum_backup_crawler.config import Settings`
- `from forum_backup_crawler.core.worker import worker`
- `from forum_backup_crawler.network.auth import load_cookies, CookieNotFoundError`
- `from forum_backup_crawler.network.http_client import HTTPClient`
- `from forum_backup_crawler.network.rate_limit import get_limiter, RateLimiter`
- `from forum_backup_crawler.storage.path_mapper import PathMapper`
- `from forum_backup_crawler.storage.state_db import StateDB`
- `from pathlib import Path`
- `from typing import Optional`

### 🌐 Global Scope Variables

**Global Variables:**
- `cookies` = load_cookies(settings.cookies_file, settings) (line 52)
- `cookies` = {} (line 54)
- `limiter` = get_limiter(settings.rate_limiter, base_delay=0.5, min_delay=0.1, max_delay=5.0, max_workers=settings.concurrency) (line 57)
- `client` = HTTPClient(limiter, settings.user_agent, cookies) (line 66)
- `db_path` = settings.temp_dir / 'state.db' (line 70)
- `db` = StateDB(db_path) (line 71)
- `mapper` = PathMapper(settings.output_dir) (line 77)
- `ctx` = Context(settings, db, client, limiter, mapper) (line 80)
- `tasks` = [asyncio.create_task(worker(ctx, idx + 1), name=f'worker-{idx + 1}') for idx in range(settings.concurrency)] (line 83)

### 🏛️ Class Definitions

#### `Context` - lines 19-32 @dataclass
**Purpose:** Carries shared components for each worker:
  - settings: global config
  - db:        the SQLite-backed state store
  - client:    the HTTP client wit...

### ⚙️ Top-Level Functions

#### `async run(settings: Settings) -> None` 🟢 (lines 35-92, complexity: 2)
**Purpose:** Orchestrate the entire crawl:
  1. Prepare directories
  2. Load cookies & build HTTP client
  3. Initialize state database
  4. Seed starting URLs
  ...
- 🔗 Function calls: `Context, HTTPClient, PathMapper, StateDB, asyncio.create_task, asyncio.gather, client.close, client.start` (+9 more)
- 📊 Local variables: `cookies, cookies, limiter, client, db_path` (+4 more)

### 🌐 External API Usage

- **asyncio**: `asyncio.create_task, asyncio.gather`
- **client**: `client.close, client.start`
- **db**: `db.add_seed_urls, db.connect, db.reset_in_progress`
- **settings**: `settings.output_dir.mkdir, settings.temp_dir.mkdir`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `Context, HTTPClient, PathMapper, StateDB, get_limiter, load_cookies, worker`

**External API calls:** `asyncio.create_task, asyncio.gather, client.close, client.start, db.add_seed_urls, db.connect, db.reset_in_progress, settings.output_dir.mkdir, settings.temp_dir.mkdir`

**Built-in functions:** `range`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `core/worker.py`

**Overview:** 87 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`
- `logging`

**From Imports:**
- `from __future__ import annotations`
- `from forum_backup_crawler.core.scheduler import Context`
- `from forum_backup_crawler.processing.html_rewriter import rewrite`
- `from forum_backup_crawler.storage.path_mapper import PathMapper`
- `from typing import Optional`

### 🌐 Global Scope Variables

**Global Variables:**
- `logger` = logging.getLogger(__name__) (line 12)
- `db` = ctx.db (line 23)
- `client` = ctx.client (line 24)
- `limiter` = ctx.limiter (line 25)
- `mapper` = ctx.mapper (line 26)
- `settings` = ctx.settings (line 27)
- `pop` = await db.pop_pending() (line 31)
- `content_type` = None (line 46)
- `content_type` = 'html' (line 48)
- `local_path` = mapper.url_to_path(final_url) (line 55)
- `cached` = await db.cache_asset(url, None) (line 71)

### ⚙️ Top-Level Functions

#### `async worker(ctx: Context, worker_id: int) -> None` 🔴 (lines 15-87, complexity: 13)
**Purpose:** Single crawler worker loop:
  1. Pop a pending URL from the DB.
  2. Fetch its content.
  3. Depending on the result, process HTML, assets, or record ...
- 🔗 Function calls: `(settings.output_dir / local_path).write_text, client.fetch_text, db.add_redirect, db.add_seed_urls, db.cache_asset, db.mark_done, db.pop_pending, db.record_error` (+5 more)
- 📊 Local variables: `db, client, limiter, mapper, settings` (+5 more)

### 🌐 External API Usage

- **(settings**: `(settings.output_dir / local_path).write_text`
- **client**: `client.fetch_text`
- **db**: `db.add_redirect, db.add_seed_urls, db.cache_asset, db.mark_done, db.pop_pending, db.record_error`
- **logger**: `logger.debug, logger.exception`
- **logging**: `logging.getLogger`
- **mapper**: `mapper.url_to_path`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `rewrite`

**External API calls:** `(settings.output_dir / local_path).write_text, client.fetch_text, db.add_redirect, db.add_seed_urls, db.cache_asset, db.mark_done, db.pop_pending, db.record_error, logger.debug, logger.exception, logging.getLogger, mapper.url_to_path`

**Built-in functions:** `str`

### 🤖 AI Modification Hints

- **Refactoring candidates:** Functions `worker` have high complexity and could benefit from decomposition

---

## 📄 File Analysis: `logging_config.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `network/auth.py`

**Overview:** 76 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiohttp`
- `json`

**From Imports:**
- `from __future__ import annotations`
- `from bs4 import BeautifulSoup`
- `from forum_backup_crawler.config import Settings`
- `from pathlib import Path`
- `from typing import Optional`

### 🌐 Global Scope Variables

**Global Variables:**
- `cookie_path` = Path(path) if path else settings.cookies_file (line 37)
- `text` = cookie_path.read_text(encoding='utf-8') (line 41)
- `data` = json.loads(text) (line 42)
- `html` = await resp.text() (line 65)
- `soup` = BeautifulSoup(html, 'html.parser') (line 70)
- `href` = a['href'] (line 73)

### 🏛️ Class Definitions

#### `CookieNotFoundError` extends Exception - lines 14-15
**Purpose:** Raised when the cookies JSON file cannot be found.

#### `CookieInvalidError` extends Exception - lines 18-19
**Purpose:** Raised when the cookies file exists but contains invalid JSON.

### ⚙️ Top-Level Functions

#### `load_cookies(path: Optional[Path], settings: Settings) -> dict[str, str]` 🟢 (lines 22-49, complexity: 5)
**Purpose:** Load cookies from a JSON file.

If `path` is None, uses `settings.cookies_file`. The file must exist and
contain valid JSON mapping cookie names to va...
- 🔗 Function calls: `Path, cookie_path.exists, cookie_path.read_text, data.items, isinstance, json.loads, str`
- 📊 Local variables: `cookie_path, text, data`

#### `async is_logged_in(session: aiohttp.ClientSession, url: str) -> bool` 🟢 (lines 52-76, complexity: 4)
**Purpose:** Check if the session is authenticated by fetching `url` and scanning for
a '/profile' link (common in phpBB/Forumeiros when logged in).

:param sessio...
- 🔗 Function calls: `BeautifulSoup, href.startswith, resp.text, session.get, soup.find_all`
- 📊 Local variables: `html, soup, href`

### 🌐 External API Usage

- **cookie_path**: `cookie_path.exists, cookie_path.read_text`
- **data**: `data.items`
- **href**: `href.startswith`
- **json**: `json.loads`
- **resp**: `resp.text`
- **session**: `session.get`
- **soup**: `soup.find_all`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `BeautifulSoup, Path`

**External API calls:** `cookie_path.exists, cookie_path.read_text, data.items, href.startswith, json.loads, resp.text, session.get, soup.find_all`

**Built-in functions:** `isinstance, str`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `network/http_client.py`

**Overview:** 85 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiohttp`
- `asyncio`

**From Imports:**
- `from __future__ import annotations`
- `from forum_backup_crawler.network.rate_limit import RateLimiter`
- `from typing import Optional, Tuple`

### 🏛️ Class Definitions

#### `HTTPClient` - lines 11-85
**Purpose:** HTTP client wrapper that integrates with our RateLimiter
to throttle requests and manage a persistent aiohttp session.

**Methods:**
- `__init__(self, limiter: RateLimiter, user_agent: str, cookies: Optional[dict]) -> None` 🟢 (lines 17-31, complexity: 1)
  - 📝 :param limiter: RateLimiter instance to call before/after requests
:param user_agent: User-Agent hea...

### 🌐 External API Usage

- **aiohttp**: `aiohttp.ClientSession`
- **resp**: `resp.read, resp.text`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `self._limiter.after_response, self._limiter.before_request, self._session.close, self._session.get`

**External API calls:** `aiohttp.ClientSession, resp.read, resp.text`

**Built-in functions:** `str`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `network/rate_limit.py`

**Overview:** 109 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`

**From Imports:**
- `from __future__ import annotations`
- `from typing import Protocol, Literal`

### 🏛️ Class Definitions

#### `RateLimiter` extends Protocol - lines 6-21
**Purpose:** Protocol for any rate limiter strategy.

**Methods:**
- `current_delay(self) -> float` 🟢 (lines 16-17, complexity: 1) @property
  - 📝 Current delay before requests.
- `current_workers(self) -> int` 🟢 (lines 20-21, complexity: 1) @property
  - 📝 Current permitted level of concurrency.

#### `AdaptiveLimiter` - lines 41-83
**Purpose:** Adaptive rate limiter with exponential back-off on errors and gradual speed-up on successes.

**Methods:**
- `__init__(self, base_delay: float, min_delay: float, max_delay: float, max_workers: int) -> None` 🟢 (lines 46-58, complexity: 1)
- `current_delay(self) -> float` 🟢 (lines 61-62, complexity: 1) @property
- `current_workers(self) -> int` 🟢 (lines 65-66, complexity: 1) @property

#### `FixedLimiter` - lines 87-109
**Purpose:** Simple rate limiter that always waits a fixed delay and uses fixed workers.

**Methods:**
- `__init__(self, delay: float, workers: int) -> None` 🟢 (lines 92-94, complexity: 1)
- `current_delay(self) -> float` 🟢 (lines 97-98, complexity: 1) @property
- `current_workers(self) -> int` 🟢 (lines 101-102, complexity: 1) @property

### ⚙️ Top-Level Functions

#### `get_limiter(strategy: Literal['adaptive', 'fixed', 'token_bucket']) -> RateLimiter` 🟢 (lines 24-38, complexity: 2)
**Purpose:** Factory that returns an instance of a RateLimiter based on the chosen strategy.
- 🔗 Function calls: `AdaptiveLimiter, FixedLimiter`

### 🌐 External API Usage

- **asyncio**: `asyncio.sleep`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `AdaptiveLimiter, FixedLimiter`

**External API calls:** `asyncio.sleep`

**Built-in functions:** `max, min`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `processing/crawler.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `processing/html_rewriter.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `storage/assets.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `storage/path_mapper.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `storage/state_db.py`

**Overview:** 187 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiosqlite`
- `asyncio`

**From Imports:**
- `from __future__ import annotations`
- `from pathlib import Path`
- `from typing import Iterable, Optional, Tuple`

### 🏛️ Class Definitions

#### `StateDB` - lines 11-187
**Purpose:** SQLite-backed persistent state for URLs, assets, and redirects.

**Methods:**
- `__init__(self, db_path: Path) -> None` 🟢 (lines 16-22, complexity: 1)
  - 📝 :param db_path: Path to the SQLite database file.
  - 🔗 Calls: `asyncio.Lock`

### 🌐 External API Usage

- **aiosqlite**: `aiosqlite.connect`
- **asyncio**: `asyncio.Lock`
- **cursor**: `cursor.fetchone`
- **visited**: `visited.add`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `self._conn.commit, self._conn.execute, self._conn.executemany`

**External API calls:** `aiosqlite.connect, asyncio.Lock, cursor.fetchone, visited.add`

**Built-in functions:** `set, str`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `tests/test_auth.py`

**Overview:** 71 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `json`
- `pytest`

**From Imports:**
- `from aiohttp import ClientSession`
- `from aioresponses import aioresponses`
- `from forum_backup_crawler.config import Settings, Settings, Settings, Settings, Settings, Settings`
- `from forum_backup_crawler.network.auth import load_cookies, CookieNotFoundError, CookieInvalidError, is_logged_in`
- `from pathlib import Path`

### 🌐 Global Scope Variables

**Global Variables:**
- `data` = {'sessionid': 'abc123', 'userid': '42'} (line 18)
- `fp` = tmp_path / 'cookies.json' (line 19)
- `settings` = Settings(start_urls=['x'], output_dir=tmp_path / 'out') (line 24)
- `cookies` = load_cookies(None, settings) (line 27)
- `settings` = Settings(start_urls=['x'], output_dir=tmp_path / 'out') (line 33)
- `fp` = tmp_path / 'cookies.json' (line 41)
- `settings` = Settings(start_urls=['x'], output_dir=tmp_path / 'out') (line 44)
- `url` = 'https://example.com' (line 53)
- `html` = '<html><body><a href="/profile?mode=edit">Edit Profile</a></body></html>' (line 54)
- `url` = 'https://example.com' (line 64)
- `html` = '<html><body><p>No profile here</p></body></html>' (line 65)

### ⚙️ Top-Level Functions

#### `test_load_cookies_success(tmp_path)` 🟢 (lines 17-28, complexity: 1)
- 🔗 Function calls: `Settings, fp.write_text, json.dumps, load_cookies`
- 📊 Local variables: `data, fp, settings, cookies`

#### `test_load_cookies_not_found(tmp_path)` 🟢 (lines 31-37, complexity: 1)
- 🔗 Function calls: `Settings, load_cookies, pytest.raises`
- 📊 Local variables: `settings`

#### `test_load_cookies_invalid_json(tmp_path)` 🟢 (lines 40-48, complexity: 1)
- 🔗 Function calls: `Settings, fp.write_text, load_cookies, pytest.raises`
- 📊 Local variables: `fp, settings`

#### `async test_is_logged_in_detects_profile(tmp_path)` 🟢 (lines 52-60, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `ClientSession, aioresponses, is_logged_in, m.get`
- 📊 Local variables: `url, html`

#### `async test_is_logged_in_not_found(tmp_path)` 🟢 (lines 63-71, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `ClientSession, aioresponses, is_logged_in, m.get`
- 📊 Local variables: `url, html`

### 🌐 External API Usage

- **fp**: `fp.write_text`
- **json**: `json.dumps`
- **m**: `m.get`
- **pytest**: `pytest.raises`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `ClientSession, Settings, aioresponses, is_logged_in, load_cookies`

**External API calls:** `fp.write_text, json.dumps, m.get, pytest.raises`

### 🤖 AI Modification Hints

- **Documentation needed:** Functions `test_load_cookies_success, test_load_cookies_not_found, test_load_cookies_invalid_json, test_is_logged_in_detects_profile, test_is_logged_in_not_found` lack docstrings

---

## 📄 File Analysis: `tests/test_config.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `tests/test_path_mapper.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `tests/test_rate_limit.py`

**Overview:** 30 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`
- `pytest`

**From Imports:**
- `from forum_backup_crawler.network.rate_limit import AdaptiveLimiter, FixedLimiter`

### 🌐 Global Scope Variables

**Global Variables:**
- `lim` = FixedLimiter(delay=0.2, workers=3) (line 7)
- `lim` = AdaptiveLimiter(base_delay=0.1, min_delay=0.05, max_delay=1.0, max_workers=5) (line 18)

### ⚙️ Top-Level Functions

#### `async test_fixed_limiter_keeps_delay_and_workers()` 🟢 (lines 6-14, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `FixedLimiter, lim.after_response, lim.before_request`
- 📊 Local variables: `lim`

#### `async test_adaptive_backoff_and_recovery()` 🟢 (lines 17-30, complexity: 2) @pytest.mark.asyncio
- 🔗 Function calls: `AdaptiveLimiter, lim.after_response, lim.before_request, range`
- 📊 Local variables: `lim`

### 🌐 External API Usage

- **lim**: `lim.after_response, lim.before_request`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `AdaptiveLimiter, FixedLimiter`

**External API calls:** `lim.after_response, lim.before_request`

**Built-in functions:** `range`

### 🤖 AI Modification Hints

- **Documentation needed:** Functions `test_fixed_limiter_keeps_delay_and_workers, test_adaptive_backoff_and_recovery` lack docstrings

---

## 📄 File Analysis: `tests/test_state_db.py`

**Overview:** 83 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`
- `pytest`

**From Imports:**
- `from forum_backup_crawler.storage.state_db import StateDB`
- `from pathlib import Path`

### 🌐 Global Scope Variables

**Global Variables:**
- `db_path` = tmp_path / 'state.db' (line 12)
- `db` = StateDB(db_path) (line 13)
- `urls` = ['a', 'b', 'c'] (line 18)
- `first` = await db.pop_pending() (line 23)
- `second` = await db.pop_pending() (line 31)
- `third` = await db.pop_pending() (line 32)
- `db` = StateDB(tmp_path / 'state.db') (line 40)
- `popped` = await db.pop_pending() (line 45)
- `db` = StateDB(tmp_path / 'state.db') (line 55)
- `result` = await db.resolve('A') (line 63)
- `db` = StateDB(tmp_path / 'state.db') (line 71)
- `ok1` = await db.cache_asset('u1', 'path1') (line 76)
- `ok2` = await db.cache_asset('u1', 'path1') (line 79)
- `path` = await db.get_asset('u1') (line 82)

### ⚙️ Top-Level Functions

#### `async test_add_and_pop_and_done(tmp_path)` 🟢 (lines 11-35, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `StateDB, db.add_seed_urls, db.connect, db.mark_done, db.pending_count, db.pop_pending, db.reset_in_progress`
- 📊 Local variables: `db_path, db, urls, first, second` (+1 more)

#### `async test_record_error(tmp_path)` 🟢 (lines 39-50, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `StateDB, db.add_seed_urls, db.connect, db.pending_count, db.pop_pending, db.record_error, db.reset_in_progress`
- 📊 Local variables: `db, popped`

#### `async test_redirect_and_resolve(tmp_path)` 🟢 (lines 54-66, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `StateDB, db.add_redirect, db.connect, db.reset_in_progress, db.resolve`
- 📊 Local variables: `db, result`

#### `async test_asset_cache(tmp_path)` 🟢 (lines 70-83, complexity: 1) @pytest.mark.asyncio
- 🔗 Function calls: `StateDB, db.cache_asset, db.connect, db.get_asset, db.reset_in_progress`
- 📊 Local variables: `db, ok1, ok2, path`

### 🌐 External API Usage

- **db**: `db.add_redirect, db.add_seed_urls, db.cache_asset, db.connect, db.get_asset, db.mark_done, db.pending_count, db.pop_pending, db.record_error, db.reset_in_progress` (+1 more)

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `StateDB`

**External API calls:** `db.add_redirect, db.add_seed_urls, db.cache_asset, db.connect, db.get_asset, db.mark_done, db.pending_count, db.pop_pending, db.record_error, db.reset_in_progress, db.resolve`

### 🤖 AI Modification Hints

- **Documentation needed:** Functions `test_add_and_pop_and_done, test_record_error, test_redirect_and_resolve, test_asset_cache` lack docstrings

---

## 📄 File Analysis: `utils/timeit.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `utils/typing.py`

**Overview:** 0 lines, complexity: 0 🟢

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

## 🔍 Cross-Reference Analysis

*For AI understanding of code relationships and dependencies*

### 🌍 External Dependencies Summary

- **(settings**: 1 calls - `(settings.output_dir / local_path).write_text`
- **Path(path)**: 1 calls - `Path(path).read_text`
- **aiohttp**: 1 calls - `aiohttp.ClientSession`
- **aiosqlite**: 1 calls - `aiosqlite.connect`
- **asyncio**: 4 calls - `asyncio.Lock, asyncio.create_task, asyncio.gather, asyncio.sleep`
- **client**: 3 calls - `client.close, client.fetch_text, client.start`
- **config_path**: 1 calls - `config_path.write_text`
- **cookie_path**: 2 calls - `cookie_path.exists, cookie_path.read_text`
- **cursor**: 1 calls - `cursor.fetchone`
- **data**: 1 calls - `data.items`
- **db**: 11 calls - `db.add_redirect, db.add_seed_urls, db.cache_asset, db.connect, db.get_asset` (+6 more)
- **fp**: 1 calls - `fp.write_text`
- **href**: 1 calls - `href.startswith`
- **json**: 2 calls - `json.dumps, json.loads`
- **kwargs**: 1 calls - `kwargs.get`
- **lim**: 2 calls - `lim.after_response, lim.before_request`
- **logger**: 2 calls - `logger.debug, logger.exception`
- **logging**: 1 calls - `logging.getLogger`
- **m**: 1 calls - `m.get`
- **mapper**: 1 calls - `mapper.url_to_path`
- **pytest**: 1 calls - `pytest.raises`
- **resp**: 2 calls - `resp.read, resp.text`
- **session**: 1 calls - `session.get`
- **settings**: 2 calls - `settings.output_dir.mkdir, settings.temp_dir.mkdir`
- **soup**: 1 calls - `soup.find_all`
- **tomli_w**: 1 calls - `tomli_w.dumps`
- **tomllib**: 1 calls - `tomllib.loads`
- **visited**: 1 calls - `visited.add`

### 🏗️ Class Inheritance Map

- `CookieInvalidError` ← `Exception`
- `CookieNotFoundError` ← `Exception`
- `RateLimiter` ← `Protocol`
- `Settings` ← `BaseSettings`

---

## 📋 Report Generation Metadata

- **Generated on:** 2025-06-24 03:13:19
- **Script version:** AI Code Mapper v2.0
- **Analysis root:** `K:\O meu disco\Código\Fórum SMPT`
- **Files analyzed:** 21
- **Total errors:** 0
- **Self-awareness:** Skipped analysis of `Mapeador.py`

*This report is optimized for AI model comprehension and code modification assistance.*
