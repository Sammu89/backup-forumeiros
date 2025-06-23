# 🧠 AI-Friendly Code Structure Analysis

*Generated for AI model comprehension and code modification assistance*

## 🌲 Project Structure & Complexity Map

```text
📊 Legend:
🟢 Low Complexity (≤10)  🟡 Medium (11-20)  🔴 High (>20)
📃 Small (<100 lines)   📄 Medium (100-500)  📚 Large (>500)
🏛️ Class  ⚙️ Function  ⚡ Async  🔶 Abstract  📁 Directory

PROJECT_ROOT/
├── 📃 assets.py 🟢 (75 lines, complexity: 0)
│   └── ⚙️ _ensure_dirs 🟢 (line 9, complexity: 3)
│   └── ⚡ download_asset 🟡 (line 21, complexity: 9)
├── 📃 auth.py 🟢 (90 lines, complexity: 0)
│   ├── 🏛️ CookieNotFoundError (line 11, 0 methods)
│   ├── 🏛️ CookieInvalidError (line 15, 0 methods)
│   └── ⚙️ load_cookies 🟢 (line 23, complexity: 4)
│   └── ⚡ is_logged_in 🟢 (line 47, complexity: 3)
├── 📄 crawler.py 🟢 (315 lines, complexity: 0)
│   ├── 🏛️ DiscoverWorker (line 166, 1 methods)
│   ├── 🏛️ DownloadWorker (line 259, 1 methods)
│   └── ⚙️ strip_fragment 🟢 (line 17, complexity: 1)
│   └── ⚙️ is_valid_link 🟡 (line 22, complexity: 9)
│   └── ⚙️ url_to_local_path 🟢 (line 63, complexity: 5)
│   └── ⚙️ write_file 🟢 (line 115, complexity: 1)
│   └── ⚡ safe_file_write 🟢 (line 112, complexity: 2)
│   └── ⚙️ write_file 🟢 (line 115, complexity: 1)
│   └── ⚙️ read_file 🟢 (line 132, complexity: 1)
│   └── ⚡ safe_file_read 🟢 (line 129, complexity: 2)
│   └── ⚙️ read_file 🟢 (line 132, complexity: 1)
│   └── ⚙️ extract_path_from_url 🟢 (line 142, complexity: 1)
│   └── ⚡ handle_redirect 🟢 (line 148, complexity: 3)
├── 📄 fetch.py 🟢 (311 lines, complexity: 0)
│   ├── 🏛️ Fetcher (line 17, 1 methods)
├── 📄 main.py 🟢 (461 lines, complexity: 0)
│   └── ⚡ periodic_save 🟢 (line 64, complexity: 2)
│   └── ⚡ main 🔴 (line 70, complexity: 43)
├── 📃 redirects.py 🟢 (46 lines, complexity: 0)
│   ├── 🏛️ RedirectMap (line 6, 2 methods)
├── 📄 rewriter.py 🟢 (360 lines, complexity: 0)
│   └── ⚙️ url_to_local_path 🟡 (line 13, complexity: 10)
│   └── ⚡ download_external_asset 🟡 (line 51, complexity: 10)
│   └── ⚡ download_internal_asset 🟡 (line 102, complexity: 10)
│   └── ⚡ process_css_for_fonts 🟢 (line 145, complexity: 5)
│   └── ⚡ process_html 🔴 (line 179, complexity: 43)
├── 📄 settings.py 🟢 (106 lines, complexity: 0)
│   ├── 🏛️ Config (line 64, 1 methods)
│   └── ⚙️ get_base_url 🟢 (line 25, complexity: 3)
│   └── ⚙️ get_base_domain 🟢 (line 33, complexity: 3)
│   └── ⚙️ get_config_path 🟢 (line 53, complexity: 2)
│   └── ⚙️ get_cookies_path 🟢 (line 58, complexity: 2)
│   └── ⚙️ load_config 🟢 (line 75, complexity: 3)
│   └── ⚙️ get_cookies 🟢 (line 94, complexity: 2)
│   └── ⚙️ set_cookies 🟢 (line 102, complexity: 1)
├── 📄 state.py 🟢 (361 lines, complexity: 0)
│   ├── 🏛️ State (line 37, 4 methods)
│   └── ⚙️ base_path 🟢 (line 25, complexity: 1)
└── 📃 throttle.py 🟢 (54 lines, complexity: 0)
    ├── 🏛️ ThrottleController (line 3, 4 methods)
```

## 📊 Comprehensive Project Metrics

- **Python Files Analyzed:** 10
- **Total Lines of Code:** 2,179
- **Classes Defined:** 9
- **Top-Level Functions:** 30
- **Class Methods:** 14
- **Average File Complexity:** 0.0
- **External Dependencies:** 26
- **Most Complex Files:** assets.py, auth.py, crawler.py

## 🔗 Dependency Overview

- **aiohttp** → Used in 3 files
- **argparse** → Used in 1 files
- **asyncio** → Used in 6 files
- **auth** → Used in 1 files
- **bs4** → Used in 3 files
- **crawler** → Used in 1 files
- **fetch** → Used in 3 files
- **hashlib** → Used in 2 files
- **json** → Used in 4 files
- **mimetypes** → Used in 2 files
- **os** → Used in 7 files
- **pathlib** → Used in 4 files
- **re** → Used in 2 files
- **redirects** → Used in 2 files
- **rewriter** → Used in 1 files
- **settings** → Used in 5 files
- **shutil** → Used in 1 files
- **state** → Used in 3 files
- **subprocess** → Used in 1 files
- **sys** → Used in 1 files
- **throttle** → Used in 1 files
- **tqdm** → Used in 1 files
- **traceback** → Used in 1 files
- **typing** → Used in 5 files
- **urllib** → Used in 7 files
- **yaml** → Used in 1 files

---

## 📄 File Analysis: `assets.py`

**Overview:** 75 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `hashlib`
- `mimetypes`
- `os`
- `settings`

**From Imports:**
- `from pathlib import Path`
- `from typing import Optional`
- `from urllib.parse import urljoin, urlparse`

### 🌐 Global Scope Variables

**Constants:**
- `IMAGE_EXTS` = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'} (line 19)

**Global Variables:**
- `output_dir` = settings.BACKUP_ROOT or Path('backup') (line 10)
- `images_dir` = output_dir / 'assets' / 'imagens' / 'internal' (line 11)
- `files_dir` = output_dir / 'assets' / 'files' / 'internal' (line 12)
- `external_dir` = output_dir / 'external_files' (line 13)
- `abs_url` = resource_url if resource_url.startswith('http') else urljoin(BASE_URL, resource_url) (line 28)
- `existing` = state.get_asset(abs_url) (line 30)
- `parsed` = urlparse(abs_url) (line 36)
- `ext` = ext.lower() (line 38)
- `guessed` = mimetypes.guess_extension(mime or '') (line 43)
- `ext` = guessed.lower() if guessed else '.bin' (line 44)
- `ext` = ext.lower() (line 46)
- `is_image` = ext in IMAGE_EXTS (line 47)
- `base_dir` = IMAGES_INTERNAL_DIR if parsed.netloc == BASE_DOMAIN else EXTERNAL_FILES_DIR (line 50)
- `base_dir` = FILES_INTERNAL_DIR if parsed.netloc == BASE_DOMAIN else EXTERNAL_FILES_DIR (line 52)
- `filename` = hashlib.md5(abs_url.encode()).hexdigest() + ext (line 54)
- `local_path` = os.path.join(base_dir, filename) (line 55)

### ⚙️ Top-Level Functions

#### `_ensure_dirs()` 🟢 (lines 9-16, complexity: 3)
- 🔗 Function calls: `Path, d.mkdir`
- 📊 Local variables: `output_dir, images_dir, files_dir, external_dir`

#### `async download_asset(resource_url: str, fetcher, state) -> Optional[str]` 🟡 (lines 21-75, complexity: 9)
**Purpose:** Download and cache an asset (image or file).
Returns the local file path if successful, or None on failure.
- 🔗 Function calls: `_ensure_dirs, abs_url.encode, ext.lower, f.write, fetcher.fetch_bytes, guessed.lower, hashlib.md5, hashlib.md5(abs_url.encode()).hexdigest` (+11 more)
- 📊 Local variables: `abs_url, existing, parsed, ext, guessed` (+7 more)

### 🌐 External API Usage

- **abs_url**: `abs_url.encode`
- **d**: `d.mkdir`
- **ext**: `ext.lower`
- **f**: `f.write`
- **fetcher**: `fetcher.fetch_bytes`
- **guessed**: `guessed.lower`
- **hashlib**: `hashlib.md5, hashlib.md5(abs_url.encode()).hexdigest`
- **mimetypes**: `mimetypes.guess_extension, mimetypes.guess_type`
- **os**: `os.path.join, os.path.splitext`
- **resource_url**: `resource_url.startswith`
- **state**: `state.add_asset, state.get_asset`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `Path, _ensure_dirs, urljoin, urlparse`

**External API calls:** `abs_url.encode, d.mkdir, ext.lower, f.write, fetcher.fetch_bytes, guessed.lower, hashlib.md5, hashlib.md5(abs_url.encode()).hexdigest, mimetypes.guess_extension, mimetypes.guess_type, os.path.join, os.path.splitext, resource_url.startswith, state.add_asset, state.get_asset`

**Built-in functions:** `open, print`

### 🤖 AI Modification Hints

- **Documentation needed:** Functions `_ensure_dirs` lack docstrings

---

## 📄 File Analysis: `auth.py`

**Overview:** 90 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiohttp`
- `json`
- `re`

**From Imports:**
- `from bs4 import BeautifulSoup`
- `from settings import get_cookies_path, get_cookies_path`
- `from urllib.parse import urlparse`

### 🌐 Global Scope Variables

**Global Variables:**
- `path` = get_cookies_path() (line 33)
- `resp` = await session.get(url) (line 53)
- `html` = await resp.text() (line 55)
- `m` = re.search('_userdata\\["session_logged_in"\\]\\s*=\\s*([01])', html) (line 60)
- `flag` = m.group(1) (line 62)
- `soup` = BeautifulSoup(html, 'html.parser') (line 69)
- `nav` = soup.find('nav') (line 70)
- `anchors` = nav.find_all('a', href=True) if nav else soup.find_all('a', href=True) (line 71)
- `login_segs` = ('/login', '/signin', '/sign-in', '/register', '/signup', '/sign-up') (line 74)
- `logout_segs` = ('/logout', '/signout', '/sign-out', '/profile', '/account') (line 75)
- `saw_login` = any((seg in urlparse(a['href']).path.lower() for a in anchors for seg in login_segs)) (line 76)
- `saw_logout` = any((seg in urlparse(a['href']).path.lower() for a in anchors for seg in logout_segs)) (line 81)
- `result` = saw_logout and (not saw_login) (line 88)

### 🏛️ Class Definitions

#### `CookieNotFoundError` extends RuntimeError - lines 11-13
**Purpose:** Raised when the cookies file does not exist.

#### `CookieInvalidError` extends RuntimeError - lines 15-17
**Purpose:** Raised when the cookies file contains invalid JSON.

### ⚙️ Top-Level Functions

#### `load_cookies(path: str) -> dict` 🟢 (lines 23-41, complexity: 4)
**Purpose:** Load cookies from JSON at `path`.
If `path` is None, uses settings.get_cookies_path().
Raises:
  - CookieNotFoundError if the file does not exist.
  -...
- 🔗 Function calls: `get_cookies_path, json.load, open`
- 📊 Local variables: `path`

#### `async is_logged_in(session: aiohttp.ClientSession, url: str) -> bool` 🟢 (lines 47-90, complexity: 3)
**Purpose:** Return True if fetching `url` with this session appears authenticated.
Verbose debug prints every step.
- 🔗 Function calls: `BeautifulSoup, any, html[:500].replace, len, m.group, nav.find_all, print, re.search` (+6 more)
- 📊 Local variables: `resp, html, m, flag, soup` (+7 more)

### 🌐 External API Usage

- **html[:500]**: `html[:500].replace`
- **json**: `json.load`
- **m**: `m.group`
- **nav**: `nav.find_all`
- **re**: `re.search`
- **resp**: `resp.text`
- **session**: `session.get`
- **soup**: `soup.find, soup.find_all`
- **urlparse(a['href'])**: `urlparse(a['href']).path.lower`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `BeautifulSoup, get_cookies_path, urlparse`

**External API calls:** `html[:500].replace, json.load, m.group, nav.find_all, re.search, resp.text, session.get, soup.find, soup.find_all, urlparse(a['href']).path.lower`

**Built-in functions:** `any, len, open, print`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `crawler.py`

**Overview:** 315 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`
- `os`
- `st`
- `traceback`

**From Imports:**
- `from bs4 import BeautifulSoup`
- `from fetch import Fetcher`
- `from pathlib import Path`
- `from redirects import redirects`
- `from rewriter import process_html`
- `from settings import get_base_domain, ALLOWED_PARAMS, BLACKLIST_PARAMS, IGNORED_PREFIXES, load_config`
- `from state import State`
- `from urllib.parse import urljoin, urlparse, parse_qsl`

### 🌐 Global Scope Variables

**Global Variables:**
- `abs_url` = urljoin(st.BASE_URL, href) (line 36)
- `no_frag` = strip_fragment(abs_url) (line 37)
- `parsed` = urlparse(no_frag) (line 38)
- `params` = dict(parse_qsl(parsed.query)) (line 55)
- `parsed` = urlparse(url) (line 68)
- `path` = parsed.path.lstrip('/') (line 69)
- `first` = path.split('/', 1)[0].lower() if path else '' (line 70)
- `folder_mapping` = {'f': 'categorias', 't': 'topicos', 'u': 'users', 'g': 'grupos', 'admin': 'admin', 'privmsg': 'privmsg', 'profile': 'profile'} (line 73)
- `folder` = 'misc' (line 83)
- `folder` = folder_name (line 86)
- `slug` = path.replace('/', '_') if path else 'index' (line 90)
- `query_slug` = parsed.query.replace('=', '-').replace('&', '_').replace('/', '_') (line 93)
- `outfile` = f'{slug}.html' (line 102)
- `backup_root` = st.BACKUP_ROOT or Path('backup') (line 105)
- `local_dir` = backup_root / folder (line 106)
- `parsed` = urlparse(url) (line 144)
- `src_path` = extract_path_from_url(original_url) (line 156)
- `dst_path` = extract_path_from_url(final_url) (line 157)

### 🏛️ Class Definitions

#### `DiscoverWorker` - lines 166-256
**Purpose:** Phase-1: Only fetch HTML, extract links, map redirects—no assets.

**Methods:**
- `__init__(self, config, state: State, fetcher: Fetcher, worker_id: int)` 🟢 (lines 169-173, complexity: 1)

#### `DownloadWorker` - lines 259-315
**Purpose:** Phase-2: Fetch HTML, rewrite & download assets, then save.

**Methods:**
- `__init__(self, config, state: State, fetcher: Fetcher, progress, worker_id: int)` 🟢 (lines 262-267, complexity: 1)

### ⚙️ Top-Level Functions

#### `strip_fragment(url: str) -> str` 🟢 (lines 17-19, complexity: 1)
**Purpose:** Remove the #fragment from a URL.
- 🔗 Function calls: `url.split`

#### `is_valid_link(href: str) -> bool` 🟡 (lines 22-60, complexity: 9)
**Purpose:** Determine if an href should be included in the crawl:
- Must be within st.BASE_URL domain.
- Must not be an action (e.g. mode=reply).
- Ignore admin/m...
- 🔗 Function calls: `dict, get_base_domain, href.startswith, parse_qsl, parsed.path.startswith, strip_fragment, urljoin, urlparse`
- 📊 Local variables: `abs_url, no_frag, parsed, params`

#### `url_to_local_path(url: str) -> str` 🟢 (lines 63-109, complexity: 5)
**Purpose:** Map a full URL to a folder/filename under ./backup/.
Categories (f*), topics (t*), users (u*), groups (g*), etc.
- 🔗 Function calls: `Path, first.startswith, folder_mapping.items, local_dir.mkdir, parsed.path.lstrip, parsed.query.replace, parsed.query.replace('=', '-').replace, parsed.query.replace('=', '-').replace('&', '_').replace` (+5 more)
- 📊 Local variables: `parsed, path, first, folder_mapping, folder` (+6 more)

#### `write_file()` 🟢 (lines 115-119, complexity: 1)
- 🔗 Function calls: `f.write, open, os.makedirs, os.path.dirname`

#### `async safe_file_write(filepath: str, content: str) -> bool` 🟢 (lines 112-126, complexity: 2)
**Purpose:** Safely write content to file asynchronously.
- 🔗 Function calls: `asyncio.to_thread, f.write, open, os.makedirs, os.path.dirname, print`
- 🔧 Nested functions: `write_file`

#### `write_file()` 🟢 (lines 115-119, complexity: 1)
- 🔗 Function calls: `f.write, open, os.makedirs, os.path.dirname`

#### `read_file()` 🟢 (lines 132-134, complexity: 1)
- 🔗 Function calls: `f.read, open`

#### `async safe_file_read(filepath: str) -> str` 🟢 (lines 129-139, complexity: 2)
**Purpose:** Safely read content from file asynchronously.
- 🔗 Function calls: `asyncio.to_thread, f.read, open, print`
- 🔧 Nested functions: `read_file`

#### `read_file()` 🟢 (lines 132-134, complexity: 1)
- 🔗 Function calls: `f.read, open`

#### `extract_path_from_url(url: str) -> str` 🟢 (lines 142-145, complexity: 1)
**Purpose:** Extract path and query from URL for state management.
- 🔗 Function calls: `urlparse`
- 📊 Local variables: `parsed`

#### `async handle_redirect(worker_id: int, original_url: str, final_url: str, state: State) -> bool` 🟢 (lines 148-163, complexity: 3)
**Purpose:** Handle URL redirects and update state.
- 🔗 Function calls: `extract_path_from_url, print, redirects.add, state.add_url, state.update_after_fetch, urlparse`
- 📊 Local variables: `src_path, dst_path`

### 🌐 External API Usage

- **asyncio**: `asyncio.sleep, asyncio.to_thread`
- **f**: `f.read, f.write`
- **first**: `first.startswith`
- **folder_mapping**: `folder_mapping.items`
- **href**: `href.startswith`
- **local_dir**: `local_dir.mkdir`
- **os**: `os.makedirs, os.path.dirname`
- **parsed**: `parsed.path.lstrip, parsed.path.startswith, parsed.query.replace, parsed.query.replace('=', '-').replace, parsed.query.replace('=', '-').replace('&', '_').replace`
- **path**: `path.replace, path.split, path.split('/', 1)[0].lower`
- **redirects**: `redirects.add`
- **soup**: `soup.find_all`
- **state**: `state.add_url, state.update_after_fetch`
- **traceback**: `traceback.print_exc`
- **url**: `url.split`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `BeautifulSoup, Path, extract_path_from_url, get_base_domain, handle_redirect, is_valid_link, parse_qsl, process_html, safe_file_write, self._extract_links, self._process_download, self._process_url, self.fetcher.fetch_text, self.progress.update, self.state.add_url`
 (+8 more)

**External API calls:** `asyncio.sleep, asyncio.to_thread, f.read, f.write, first.startswith, folder_mapping.items, href.startswith, local_dir.mkdir, os.makedirs, os.path.dirname, parsed.path.lstrip, parsed.path.startswith, parsed.query.replace, parsed.query.replace('=', '-').replace, parsed.query.replace('=', '-').replace('&', '_').replace`
 (+9 more)

**Built-in functions:** `dict, open, print, str`

### 🤖 AI Modification Hints

- **Documentation needed:** Functions `write_file, write_file, read_file, read_file` lack docstrings

---

## 📄 File Analysis: `fetch.py`

**Overview:** 311 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiohttp`
- `asyncio`

**From Imports:**
- `from typing import Tuple, Optional`

### 🏛️ Class Definitions

#### `Fetcher` - lines 17-311
**Purpose:** Performs HTTP GET requests with cookies, user-agent, timeouts, and throttling.



Provides methods to fetch text (HTML) and binary (assets).

**Methods:**
- `__init__(self, config, throttle, cookies: dict)` 🟢 (lines 37-77, complexity: 1)
  - 📝 :param config: Config object with user_agent, etc.



:param throttle: ThrottleController instance.
...

### 🌐 External API Usage

- **aiohttp**: `aiohttp.ClientSession, aiohttp.ClientTimeout`
- **response**: `response.read, response.text`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `self._ensure_session, self.session.close, self.session.get, self.throttle.after_response, self.throttle.before_request`

**External API calls:** `aiohttp.ClientSession, aiohttp.ClientTimeout, response.read, response.text`

**Built-in functions:** `str`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `main.py`

**Overview:** 461 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `aiohttp`
- `argparse`
- `asyncio`
- `config`
- `os`
- `shutil`
- `st`
- `subprocess`
- `sys`

**From Imports:**
- `from auth import load_cookies, is_logged_in, CookieNotFoundError, CookieInvalidError`
- `from crawler import DiscoverWorker, DiscoverWorker, DownloadWorker, DiscoverWorker, DownloadWorker`
- `from fetch import Fetcher`
- `from os import path`
- `from pathlib import Path`
- `from settings import get_config_path, get_cookies_path, get_base_domain, load_config, set_cookies`
- `from state import State`
- `from throttle import ThrottleController`
- `from tqdm.asyncio import tqdm, tqdm, tqdm, tqdm`
- `from urllib.parse import unquote, urlparse, urlparse, urlparse`

### 🌐 Global Scope Variables

**Global Variables:**
- `required` = [('aiohttp', 'aiohttp'), ('PyYAML', 'yaml'), ('beautifulsoup4', 'bs4'), ('tqdm', 'tqdm')] (line 45)
- `desktop_dir` = Path.home() / 'Desktop' (line 60)
- `parser` = argparse.ArgumentParser(description='Forum backup crawler') (line 73)
- `args` = parser.parse_args() (line 95)
- `default_url` = 'https://sm-portugal.forumeiros.com/' (line 98)
- `forum_url` = args.forum.strip().rstrip('/') (line 100)
- `user_input` = input(f'Forum base URL to backup (default {default_url}): ').strip() (line 102)
- `raw_url` = default_url (line 104)
- `raw_url` = user_input (line 106)
- `raw_url` = 'https://' + raw_url[len('http://'):] (line 109)
- `forum_url` = raw_url.rstrip('/') (line 110)
- `forum_url` = 'https://' + forum_url (line 113)
- `slug` = st.get_base_domain().split('.')[0] (line 126)
- `config` = load_config() (line 140)
- `state_file` = str(st.BACKUP_ROOT / 'crawl_state.json') (line 148)
- `final_file` = str(st.BACKUP_ROOT / 'crawl_state_final.json') (line 149)
- `cache_file` = str(st.BACKUP_ROOT / 'assets_cache.json') (line 150)
- `domain_slug` = get_base_domain().replace('.', '_') (line 162)
- `data_key` = f'fa_{domain_slug}_data' (line 163)
- `sid_key` = f'fa_{domain_slug}_sid' (line 164)
- `cookie_file` = get_cookies_path() (line 169)
- `cookies` = load_cookies(cookie_file) (line 172)
- `cookies` = {} (line 176)
- `cookies` = {} (line 195)
- `logged` = await is_logged_in(sess, st.BASE_URL + '/') (line 209)
- `logged` = False (line 212)
- `choice` = input('Authentication failed with saved cookies. Reconfigure cookies? (y/N): ') (line 216)
- `cookies` = {} (line 235)
- `logged` = await is_logged_in(sess, st.BASE_URL + '/') (line 250)
- `logged` = False (line 253)
- `skip_crawling` = args.resume or os.path.exists(final_file) (line 271)
- `state` = State(config, state_path=state_file, cache_path=cache_file) (line 272)
- `total` = len(state.urls) (line 276)
- `done` = sum((1 for v in state.urls.values() if v['status'] == 'downloaded')) (line 277)
- `pending` = sum((1 for v in state.urls.values() if v['status'] == 'pending')) (line 278)
- `errors` = sum((1 for v in state.urls.values() if v['status'] == 'error')) (line 279)
- `throttle` = ThrottleController(config) (line 297)
- `fetcher` = Fetcher(config, throttle, cookies) (line 298)
- `shutdown_after_crawl` = False (line 306)
- `choice` = input('💻 Shut down PC after crawling completes? (y/N): ') (line 309)
- `shutdown_after_crawl` = True (line 311)
- `max_workers` = 7 (line 326)
- `tasks` = [asyncio.create_task(DiscoverWorker(config, state, fetcher, worker_id=1).run())] (line 329)
- `escalated` = False (line 330)
- `escalated` = True (line 339)
- `to_download` = sum((1 for v in state.urls.values() if v['status'] == 'listed')) (line 373)
- `progress` = tqdm(total=to_download, unit='page', desc='Downloading') (line 382)
- `download_workers` = [DownloadWorker(config, state, fetcher, progress, worker_id=i + 1) for i in range(config.workers)] (line 384)
- `resp` = input('🗑️  Delete temporary files? (y/N): ') (line 418)
- `deleted_count` = 0 (line 420)
- `state` = None (line 433)
- `fetcher` = None (line 434)

### ⚙️ Top-Level Functions

#### `async periodic_save(state: State, interval: int)` 🟢 (lines 64-68, complexity: 2)
- 🔗 Function calls: `asyncio.sleep, print, state.save`

#### `async main()` 🔴 (lines 70-430, complexity: 43)
- 🔗 Function calls: `(desktop_dir / slug).resolve, DiscoverWorker, DiscoverWorker(config, state, fetcher, worker_id=1).run, DiscoverWorker(config, state, fetcher, worker_id=i).run, DownloadWorker, Fetcher, State, ThrottleController` (+56 more)
- 📊 Local variables: `parser, args, default_url, forum_url, user_input` (+43 more)

### 🌐 External API Usage

- **(desktop_dir / slug)**: `(desktop_dir / slug).resolve`
- **DiscoverWorker(config, state, fetcher, worker_id=1)**: `DiscoverWorker(config, state, fetcher, worker_id=1).run`
- **DiscoverWorker(config, state, fetcher, worker_id=i)**: `DiscoverWorker(config, state, fetcher, worker_id=i).run`
- **Path**: `Path.home`
- **aiohttp**: `aiohttp.ClientSession`
- **argparse**: `argparse.ArgumentParser`
- **args**: `args.forum.strip, args.forum.strip().rstrip`
- **asyncio**: `asyncio.create_task, asyncio.gather, asyncio.run, asyncio.sleep`
- **choice**: `choice.strip, choice.strip().lower`
- **fetcher**: `fetcher.close`
- **forum_url**: `forum_url.startswith`
- **get_base_domain()**: `get_base_domain().replace`
- **input(f'Forum base URL to backup (default {default_url}): ')**: `input(f'Forum base URL to backup (default {default_url}): ').strip`
- **input(f'📋 Enter {data_key}: ')**: `input(f'📋 Enter {data_key}: ').strip`
- **input(f'📋 Enter {sid_key}: ')**: `input(f'📋 Enter {sid_key}: ').strip`
- **os**: `os.environ.setdefault, os.path.exists, os.remove, os.system`
- **parser**: `parser.add_argument, parser.parse_args`
- **path**: `path.exists`
- **progress**: `progress.close`
- **raw_url**: `raw_url.rstrip, raw_url.startswith`
- **resp**: `resp.strip, resp.strip().lower`
- **sess**: `sess.cookie_jar.clear, sess.cookie_jar.update_cookies`
- **shutil**: `shutil.copy`
- **st**: `st.BACKUP_ROOT.mkdir, st.get_base_domain, st.get_base_domain().split`
- **state**: `state.add_url, state.pending_count, state.save, state.urls.values`
- **subprocess**: `subprocess.check_call`
- **sys**: `sys.exit`
- **tasks**: `tasks.append`
- **tasks[0]**: `tasks[0].done`
- **w**: `w.run`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `DiscoverWorker, DownloadWorker, Fetcher, State, ThrottleController, __import__, get_base_domain, get_config_path, get_cookies_path, input, is_logged_in, load_config, load_cookies, locals, main`
 (+3 more)

**External API calls:** `(desktop_dir / slug).resolve, DiscoverWorker(config, state, fetcher, worker_id=1).run, DiscoverWorker(config, state, fetcher, worker_id=i).run, Path.home, aiohttp.ClientSession, argparse.ArgumentParser, args.forum.strip, args.forum.strip().rstrip, asyncio.create_task, asyncio.gather, asyncio.run, asyncio.sleep, choice.strip, choice.strip().lower, fetcher.close`
 (+32 more)

**Built-in functions:** `len, print, range, str, sum`

### 🤖 AI Modification Hints

- **Refactoring candidates:** Functions `main` have high complexity and could benefit from decomposition
- **Documentation needed:** Functions `periodic_save, main` lack docstrings

---

## 📄 File Analysis: `redirects.py`

**Overview:** 46 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`
- `json`
- `os`

**From Imports:**
- `from typing import Dict`

### 🌐 Global Scope Variables

**Global Variables:**
- `redirects` = RedirectMap() (line 46)

### 🏛️ Class Definitions

#### `RedirectMap` - lines 6-43
**Purpose:** Thread-safe map of src_path → dst_path, persisted in redirects.json.

**Methods:**
- `__init__(self, filename)` 🟢 (lines 8-19, complexity: 3)
  - 🔗 Calls: `asyncio.Lock, json.load, open, os.getcwd, os.path.exists` (+1 more)
- `resolve(self, path: str) -> str` 🟢 (lines 39-43, complexity: 2)
  - 📝 Segue a cadeia de redirects até ao destino final.

### 🌐 External API Usage

- **asyncio**: `asyncio.Lock, asyncio.to_thread`
- **json**: `json.dump, json.load`
- **os**: `os.getcwd, os.makedirs, os.path.dirname, os.path.exists, os.path.join`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `RedirectMap, self.map.get`

**External API calls:** `asyncio.Lock, asyncio.to_thread, json.dump, json.load, os.getcwd, os.makedirs, os.path.dirname, os.path.exists, os.path.join`

**Built-in functions:** `open`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `rewriter.py`

**Overview:** 360 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `hashlib`
- `mimetypes`
- `os`
- `re`
- `settings`

**From Imports:**
- `from bs4 import BeautifulSoup`
- `from fetch import Fetcher`
- `from redirects import redirects`
- `from state import State`
- `from urllib.parse import urljoin, urlparse`

### 🌐 Global Scope Variables

**Global Variables:**
- `parsed` = urlparse(path) (line 22)
- `route` = parsed.path.lstrip('/') (line 23)
- `prefix` = route.split('/', 1)[0].lower() if route else '' (line 24)
- `folder` = 'categorias' (line 27)
- `folder` = 'topicos' (line 29)
- `folder` = 'users' (line 31)
- `folder` = 'grupos' (line 33)
- `folder` = 'privmsg' (line 35)
- `folder` = 'profile' (line 37)
- `folder` = 'misc' (line 39)
- `slug` = route.replace('/', '_') if route else 'index' (line 41)
- `filename` = f'{slug}.html' (line 44)
- `local_dir` = os.path.join(settings.BACKUP_ROOT, folder) (line 46)
- `url_hash` = hashlib.md5(url.encode()).hexdigest()[:12] (line 57)
- `parsed` = urlparse(url) (line 58)
- `ext` = '.css' (line 65)
- `ext` = '.js' (line 67)
- `ext` = '.woff2' (line 70)
- `ext` = '.jpg' (line 72)
- `ext` = '.bin' (line 74)
- `filename` = f'{url_hash}{ext}' (line 76)
- `local_dir` = os.path.join(settings.BACKUP_ROOT, 'external_files', asset_type) (line 77)
- `local_path` = os.path.join(local_dir, filename) (line 79)
- `parsed` = urlparse(url) (line 106)
- `filename` = os.path.basename(parsed.path) or 'asset' (line 107)
- `local_dir` = os.path.join(settings.BACKUP_ROOT, 'assets', asset_type) (line 120)
- `local_path` = os.path.join(local_dir, filename) (line 122)
- `url_pattern` = 'url\\s*\\(\\s*[\\\'"]?([^\\\'")]+)[\\\'"]?\\s*\\)' (line 152)
- `urls` = re.findall(url_pattern, css_content) (line 153)
- `abs_url` = url if url.startswith('http') else urljoin(css_url, url) (line 161)
- `parsed` = urlparse(abs_url) (line 162)
- `ext` = ext.lower() (line 166)
- `local_path` = await download_external_asset(abs_url, fetcher, 'fonts') (line 170)
- `css_content` = css_content.replace(f'url({url})', f'url({local_path})') (line 172)
- `css_content` = css_content.replace(f'url("{url}")', f'url("{local_path}")') (line 173)
- `css_content` = css_content.replace(f"url('{url}')", f"url('{local_path}')") (line 174)
- `soup` = BeautifulSoup(html, 'html.parser') (line 190)
- `current_page_path` = url_to_local_path(page_url) (line 191)
- `base_path` = os.path.dirname(current_page_path) (line 192)
- `head` = soup.find('head') (line 195)
- `href` = link['href'] (line 201)
- `abs_href` = href if href.startswith('http') else urljoin(settings.BASE_URL, href) (line 202)
- `parsed` = urlparse(abs_href) (line 203)
- `is_internal` = parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc (line 206)
- `rel_attr` = link.get('rel', []) (line 208)
- `rel_attr` = [rel_attr] (line 210)
- `local_path` = await download_internal_asset(abs_href, fetcher, 'css') (line 215)
- `processed_css` = await process_css_for_fonts(css_content, abs_href, fetcher) (line 221)
- `full_local_path` = os.path.join(settings.BACKUP_ROOT, local_path) (line 223)
- `local_path` = await download_external_asset(abs_href, fetcher, 'css') (line 232)
- `processed_css` = await process_css_for_fonts(css_content, abs_href, fetcher) (line 238)
- `full_local_path` = os.path.join(settings.BACKUP_ROOT, local_path) (line 240)
- `as_attr` = link.get('as', '') (line 250)
- `asset_type` = 'fonts' if as_attr == 'font' else 'css' if as_attr == 'style' else 'js' (line 253)
- `local_path` = await download_internal_asset(abs_href, fetcher, asset_type) (line 254)
- `asset_type` = 'fonts' if as_attr == 'font' else 'css' if as_attr == 'style' else 'js' (line 257)
- `local_path` = await download_external_asset(abs_href, fetcher, asset_type) (line 258)
- `local_path` = await download_internal_asset(abs_href, fetcher, 'images') (line 264)
- `local_path` = await download_external_asset(abs_href, fetcher, 'images') (line 267)
- `src` = script['src'] (line 272)
- `abs_src` = src if src.startswith('http') else urljoin(settings.BASE_URL, src) (line 273)
- `parsed` = urlparse(abs_src) (line 274)
- `is_internal` = parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc (line 276)
- `local_path` = await download_internal_asset(abs_src, fetcher, 'js') (line 279)
- `local_path` = await download_external_asset(abs_src, fetcher, 'js') (line 283)
- `processed_css` = await process_css_for_fonts(style.string, page_url, fetcher) (line 289)
- `src` = img['src'] (line 296)
- `abs_src` = src if src.startswith('http') else urljoin(settings.BASE_URL, src) (line 297)
- `parsed` = urlparse(abs_src) (line 298)
- `local_path` = await download_internal_asset(abs_src, fetcher, 'images') (line 302)
- `local_path` = await download_external_asset(abs_src, fetcher, 'images') (line 308)
- `href` = link['href'] (line 316)
- `abs_href` = href if href.startswith('http') else urljoin(settings.BASE_URL, href) (line 317)
- `parsed` = urlparse(abs_href) (line 318)
- `local_path` = await download_internal_asset(abs_href, fetcher, 'css') (line 321)
- `src` = script['src'] (line 329)
- `abs_src` = src if src.startswith('http') else urljoin(settings.BASE_URL, src) (line 330)
- `parsed` = urlparse(abs_src) (line 331)
- `local_path` = await download_internal_asset(abs_src, fetcher, 'js') (line 334)
- `href` = a['href'] (line 339)
- `abs_href` = href if href.startswith('http') else urljoin(settings.BASE_URL, href) (line 343)
- `parsed` = urlparse(base) (line 347)
- `rel_path` = parsed.path + (f'?{parsed.query}' if parsed.query else '') (line 349)
- `rel_path` = redirects.resolve(rel_path) (line 351)
- `local_target` = url_to_local_path(rel_path) (line 353)
- `rel` = os.path.relpath(local_target, base_path) (line 354)

### ⚙️ Top-Level Functions

#### `url_to_local_path(path: str) -> str` 🟡 (lines 13-48, complexity: 10)
**Purpose:** Convert a relative URL path (with optional ?query) into a local file path.
Root path "/" becomes "index.html" at backup root.
E.g. "/t1234-topic" → "b...
- 🔗 Function calls: `os.makedirs, os.path.join, parsed.path.lstrip, parsed.query.replace, parsed.query.replace('=', '-').replace, prefix.startswith, route.replace, route.split` (+2 more)
- 📊 Local variables: `parsed, route, prefix, folder, folder` (+8 more)

#### `async download_external_asset(url: str, fetcher: Fetcher, asset_type: str) -> str` 🟡 (lines 51-99, complexity: 10)
**Purpose:** Download an external asset and return the local relative path.
asset_type: 'css', 'js', 'fonts', 'images', 'misc'
- 🔗 Function calls: `f.write, fetcher.fetch_bytes, hashlib.md5, hashlib.md5(url.encode()).hexdigest, open, os.makedirs, os.path.dirname, os.path.exists` (+7 more)
- 📊 Local variables: `url_hash, parsed, ext, ext, ext` (+5 more)

#### `async download_internal_asset(url: str, fetcher: Fetcher, asset_type: str) -> str` 🟡 (lines 102-142, complexity: 10)
**Purpose:** Download an internal asset and return the local relative path.
- 🔗 Function calls: `f.write, fetcher.fetch_bytes, open, os.makedirs, os.path.basename, os.path.dirname, os.path.exists, os.path.join` (+4 more)
- 📊 Local variables: `parsed, filename, local_dir, local_path`

#### `async process_css_for_fonts(css_content: str, css_url: str, fetcher: Fetcher) -> str` 🟢 (lines 145-176, complexity: 5)
**Purpose:** Process CSS content to download any external fonts and rewrite URLs.
- 🔗 Function calls: `css_content.replace, download_external_asset, ext.lower, os.path.splitext, re.findall, url.lower, url.startswith, urljoin` (+1 more)
- 📊 Local variables: `url_pattern, urls, abs_url, parsed, ext` (+4 more)

#### `async process_html(page_url: str, html: str, fetcher: Fetcher, state: State) -> str` 🔴 (lines 179-360, complexity: 43)
**Purpose:** Rewrite an HTML page:
- Download ALL external resources in <head> (CSS, JS, fonts, etc.)
- Download and rewrite internal assets (images, CSS, JS)
- Do...
- 🔗 Function calls: `BeautifulSoup, abs_href.split, any, download_external_asset, download_internal_asset, f.write, fetcher.fetch_text, head.find_all` (+21 more)
- 📊 Local variables: `soup, current_page_path, base_path, head, href` (+45 more)

### 🌐 External API Usage

- **abs_href**: `abs_href.split`
- **css_content**: `css_content.replace`
- **ext**: `ext.lower`
- **f**: `f.write`
- **fetcher**: `fetcher.fetch_bytes, fetcher.fetch_text`
- **hashlib**: `hashlib.md5, hashlib.md5(url.encode()).hexdigest`
- **head**: `head.find_all`
- **href**: `href.startswith`
- **img**: `img.get`
- **link**: `link.find_parent, link.get`
- **os**: `os.makedirs, os.path.basename, os.path.dirname, os.path.exists, os.path.join, os.path.relpath, os.path.splitext`
- **parsed**: `parsed.path.lstrip, parsed.query.replace, parsed.query.replace('=', '-').replace`
- **prefix**: `prefix.startswith`
- **re**: `re.findall`
- **redirects**: `redirects.resolve`
- **route**: `route.replace, route.split, route.split('/', 1)[0].lower`
- **script**: `script.find_parent`
- **soup**: `soup.find, soup.find_all`
- **src**: `src.startswith`
- **url**: `url.encode, url.lower, url.startswith`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `BeautifulSoup, download_external_asset, download_internal_asset, process_css_for_fonts, url_to_local_path, urljoin, urlparse`

**External API calls:** `abs_href.split, css_content.replace, ext.lower, f.write, fetcher.fetch_bytes, fetcher.fetch_text, hashlib.md5, hashlib.md5(url.encode()).hexdigest, head.find_all, href.startswith, img.get, link.find_parent, link.get, os.makedirs, os.path.basename`
 (+21 more)

**Built-in functions:** `any, isinstance, open, print, str`

### 🤖 AI Modification Hints

- **Refactoring candidates:** Functions `process_html` have high complexity and could benefit from decomposition

---

## 📄 File Analysis: `settings.py`

**Overview:** 106 lines, complexity: 0 🟢

**File Purpose:** Runtime configuration shared by all modules.
Set dynamically by main.py before crawling starts.

### 📦 Import Analysis

**Direct Imports:**
- `json`
- `os`
- `yaml`

**From Imports:**
- `from pathlib import Path`
- `from typing import Any, Dict`
- `from urllib.parse import urlparse`

### 🌐 Global Scope Variables

**Constants:**
- `ALLOWED_PARAMS` = {'start', 'folder', 'page_profil'} (line 45)
- `BLACKLIST_PARAMS` = {'vote', 'mode', 'friend', 'foe', 'profil_tabs'} (line 46)
- `IGNORED_PREFIXES` = ('/admin', '/modcp', '/profile') (line 47)

**Global Variables:**
- `default` = {'workers': 5, 'base_delay': 0.5, 'min_delay': 0.3, 'max_delay': 8.0, 'retry_limit': 3, 'save_every': 100, 'user_agent': 'ForumSMPTBackup/1.0'} (line 77)
- `path` = get_config_path() (line 86)
- `data` = yaml.safe_load(f) or default (line 91)
- `path` = get_cookies_path() (line 96)
- `path` = get_cookies_path() (line 104)

### 🏛️ Class Definitions

#### `Config` - lines 64-73
**Purpose:** Immutable configuration object loaded from config.yaml.

**Methods:**
- `__init__(self, data: Dict[str, Any])` 🟢 (lines 66-73, complexity: 1)
  - 🔗 Calls: `data.get`

### ⚙️ Top-Level Functions

#### `get_base_url() -> str` 🟢 (lines 25-31, complexity: 3)
**Purpose:** Return BASE_URL or derive it from BASE_DOMAIN.

#### `get_base_domain() -> str` 🟢 (lines 33-39, complexity: 3)
**Purpose:** Return BASE_DOMAIN or derive it from BASE_URL.
- 🔗 Function calls: `urlparse`

#### `get_config_path() -> str` 🟢 (lines 53-56, complexity: 2)
- 🔗 Function calls: `str`

#### `get_cookies_path() -> str` 🟢 (lines 58-61, complexity: 2)
- 🔗 Function calls: `str`

#### `load_config() -> Config` 🟢 (lines 75-92, complexity: 3)
**Purpose:** Load config from YAML or create with defaults.
- 🔗 Function calls: `Config, get_config_path, open, os.path.exists, yaml.dump, yaml.safe_load`
- 📊 Local variables: `default, path, data`

#### `get_cookies() -> Dict[str, str]` 🟢 (lines 94-100, complexity: 2)
**Purpose:** Read cookies from file or return empty dict.
- 🔗 Function calls: `get_cookies_path, json.load, open, os.path.exists`
- 📊 Local variables: `path`

#### `set_cookies(cookies: Dict[str, str]) -> None` 🟢 (lines 102-106, complexity: 1)
**Purpose:** Write cookies to file, overwriting existing.
- 🔗 Function calls: `get_cookies_path, json.dump, open`
- 📊 Local variables: `path`

### 🌐 External API Usage

- **data**: `data.get`
- **json**: `json.dump, json.load`
- **os**: `os.path.exists`
- **yaml**: `yaml.dump, yaml.safe_load`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `Config, get_config_path, get_cookies_path, urlparse`

**External API calls:** `data.get, json.dump, json.load, os.path.exists, yaml.dump, yaml.safe_load`

**Built-in functions:** `open, str`

### 🤖 AI Modification Hints

- **Documentation needed:** Functions `get_config_path, get_cookies_path` lack docstrings

---

## 📄 File Analysis: `state.py`

**Overview:** 361 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`
- `json`
- `os`

**From Imports:**
- `from typing import Dict, List, Optional`
- `from urllib.parse import urlparse`

### 🌐 Global Scope Variables

**Constants:**
- `CODE2TEXT` = {'p': 'pending', 'i': 'in_progress', 'l': 'listed', 'd': 'downloaded', 'e': 'error'} (line 17)
- `TEXT2CODE` = {v: k for k, v in CODE2TEXT.items()} (line 21)

**Global Variables:**
- `parsed` = urlparse(full_url) (line 29)

### 🏛️ Class Definitions

#### `State` - lines 37-361
**Purpose:** Manages crawl state (URLs) and asset cache.

crawl_state.json format: [

    ["url", "status", retries, "last_error"],

    ...

]

assets_cache.json ...

**Methods:**
- `__init__(self, config, state_path: Optional[str], cache_path: Optional[str])` 🟢 (lines 63-79, complexity: 3)
  - 🔗 Calls: `asyncio.Lock, os.getcwd, os.path.join, self._load`
- `_load(self)` 🟢 (lines 83-113, complexity: 4)
  - 🔗 Calls: `json.load, json.loads, open, os.path.exists`
- `get_asset(self, resource_url: str) -> Optional[str]` 🟢 (lines 333-337, complexity: 1)
  - 📝 If asset URL already downloaded, return local path, else None.
  - 🔗 Calls: `self.assets_cache.get`
- `pending_count(self) -> int` 🟢 (lines 341-345, complexity: 1)
  - 📝 Return the number of URLs still in 'pending' status.
  - 🔗 Calls: `self.urls.values, sum`

### ⚙️ Top-Level Functions

#### `base_path(full_url: str) -> str` 🟢 (lines 25-31, complexity: 1)
**Purpose:** Return only '/f1…' part – drop scheme, host and fragment.
- 🔗 Function calls: `urlparse`
- 📊 Local variables: `parsed`

### 🌐 External API Usage

- **'\n'**: `'\n'.join`
- **CODE2TEXT**: `CODE2TEXT.items`
- **asyncio**: `asyncio.Lock, asyncio.to_thread`
- **json**: `json.dump, json.dumps, json.load, json.loads`
- **lines**: `lines.append, lines.sort`
- **os**: `os.getcwd, os.makedirs, os.path.dirname, os.path.exists, os.path.join`
- **sf**: `sf.write`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**Internal calls:** `self._load, self._maybe_save, self.assets_cache.get, self.pending_count, self.save, self.urls.get, self.urls.items, self.urls.values, urlparse`

**External API calls:** `'\n'.join, CODE2TEXT.items, asyncio.Lock, asyncio.to_thread, json.dump, json.dumps, json.load, json.loads, lines.append, lines.sort, os.getcwd, os.makedirs, os.path.dirname, os.path.exists, os.path.join`
 (+1 more)

**Built-in functions:** `list, open, print, sum`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

---

## 📄 File Analysis: `throttle.py`

**Overview:** 54 lines, complexity: 0 🟢

### 📦 Import Analysis

**Direct Imports:**
- `asyncio`

### 🏛️ Class Definitions

#### `ThrottleController` - lines 3-54
**Purpose:** Controls dynamic back-off and concurrency for HTTP requests.
Adjusts delay and worker count based on response status codes.

**Methods:**
- `__init__(self, config)` 🟢 (lines 8-15, complexity: 1)
- `after_response(self, status_code: int)` 🟢 (lines 24-42, complexity: 5)
  - 📝 Adjust delay and worker count based on the status code.
- On 429 or 5xx: exponential back-off (delay...
  - 🔗 Calls: `max, min`
- `get_current_delay(self) -> float` 🟢 (lines 44-48, complexity: 1)
  - 📝 Return the current inter-request delay.
- `get_current_workers(self) -> int` 🟢 (lines 50-54, complexity: 1)
  - 📝 Return the current recommended number of concurrent workers.

### 🌐 External API Usage

- **asyncio**: `asyncio.sleep`

### 📞 Function Call Graph

*All function calls detected in this file (for AI dependency analysis)*

**External API calls:** `asyncio.sleep`

**Built-in functions:** `max, min`

### 🤖 AI Modification Hints

- ✅ Code structure appears well-organized for AI modifications

## 🔍 Cross-Reference Analysis

*For AI understanding of code relationships and dependencies*

### 🌍 External Dependencies Summary

- **'\n'**: 1 calls - `'\n'.join`
- **(desktop_dir / slug)**: 1 calls - `(desktop_dir / slug).resolve`
- **CODE2TEXT**: 1 calls - `CODE2TEXT.items`
- **DiscoverWorker(config, state, fetcher, worker_id=1)**: 1 calls - `DiscoverWorker(config, state, fetcher, worker_id=1).run`
- **DiscoverWorker(config, state, fetcher, worker_id=i)**: 1 calls - `DiscoverWorker(config, state, fetcher, worker_id=i).run`
- **Path**: 1 calls - `Path.home`
- **abs_href**: 1 calls - `abs_href.split`
- **abs_url**: 1 calls - `abs_url.encode`
- **aiohttp**: 2 calls - `aiohttp.ClientSession, aiohttp.ClientTimeout`
- **argparse**: 1 calls - `argparse.ArgumentParser`
- **args**: 2 calls - `args.forum.strip, args.forum.strip().rstrip`
- **asyncio**: 6 calls - `asyncio.Lock, asyncio.create_task, asyncio.gather, asyncio.run, asyncio.sleep` (+1 more)
- **choice**: 2 calls - `choice.strip, choice.strip().lower`
- **css_content**: 1 calls - `css_content.replace`
- **d**: 1 calls - `d.mkdir`
- **data**: 1 calls - `data.get`
- **ext**: 1 calls - `ext.lower`
- **f**: 2 calls - `f.read, f.write`
- **fetcher**: 3 calls - `fetcher.close, fetcher.fetch_bytes, fetcher.fetch_text`
- **first**: 1 calls - `first.startswith`
- **folder_mapping**: 1 calls - `folder_mapping.items`
- **forum_url**: 1 calls - `forum_url.startswith`
- **get_base_domain()**: 1 calls - `get_base_domain().replace`
- **guessed**: 1 calls - `guessed.lower`
- **hashlib**: 3 calls - `hashlib.md5, hashlib.md5(abs_url.encode()).hexdigest, hashlib.md5(url.encode()).hexdigest`
- **head**: 1 calls - `head.find_all`
- **href**: 1 calls - `href.startswith`
- **html[:500]**: 1 calls - `html[:500].replace`
- **img**: 1 calls - `img.get`
- **input(f'Forum base URL to backup (default {default_url}): ')**: 1 calls - `input(f'Forum base URL to backup (default {default_url}): ').strip`
- **input(f'📋 Enter {data_key}: ')**: 1 calls - `input(f'📋 Enter {data_key}: ').strip`
- **input(f'📋 Enter {sid_key}: ')**: 1 calls - `input(f'📋 Enter {sid_key}: ').strip`
- **json**: 4 calls - `json.dump, json.dumps, json.load, json.loads`
- **lines**: 2 calls - `lines.append, lines.sort`
- **link**: 2 calls - `link.find_parent, link.get`
- **local_dir**: 1 calls - `local_dir.mkdir`
- **m**: 1 calls - `m.group`
- **mimetypes**: 2 calls - `mimetypes.guess_extension, mimetypes.guess_type`
- **nav**: 1 calls - `nav.find_all`
- **os**: 11 calls - `os.environ.setdefault, os.getcwd, os.makedirs, os.path.basename, os.path.dirname` (+6 more)
- **parsed**: 5 calls - `parsed.path.lstrip, parsed.path.startswith, parsed.query.replace, parsed.query.replace('=', '-').replace, parsed.query.replace('=', '-').replace('&', '_').replace`
- **parser**: 2 calls - `parser.add_argument, parser.parse_args`
- **path**: 4 calls - `path.exists, path.replace, path.split, path.split('/', 1)[0].lower`
- **prefix**: 1 calls - `prefix.startswith`
- **progress**: 1 calls - `progress.close`
- **raw_url**: 2 calls - `raw_url.rstrip, raw_url.startswith`
- **re**: 2 calls - `re.findall, re.search`
- **redirects**: 2 calls - `redirects.add, redirects.resolve`
- **resource_url**: 1 calls - `resource_url.startswith`
- **resp**: 3 calls - `resp.strip, resp.strip().lower, resp.text`
- **response**: 2 calls - `response.read, response.text`
- **route**: 3 calls - `route.replace, route.split, route.split('/', 1)[0].lower`
- **script**: 1 calls - `script.find_parent`
- **sess**: 2 calls - `sess.cookie_jar.clear, sess.cookie_jar.update_cookies`
- **session**: 1 calls - `session.get`
- **sf**: 1 calls - `sf.write`
- **shutil**: 1 calls - `shutil.copy`
- **soup**: 2 calls - `soup.find, soup.find_all`
- **src**: 1 calls - `src.startswith`
- **st**: 3 calls - `st.BACKUP_ROOT.mkdir, st.get_base_domain, st.get_base_domain().split`
- **state**: 7 calls - `state.add_asset, state.add_url, state.get_asset, state.pending_count, state.save` (+2 more)
- **subprocess**: 1 calls - `subprocess.check_call`
- **sys**: 1 calls - `sys.exit`
- **tasks**: 1 calls - `tasks.append`
- **tasks[0]**: 1 calls - `tasks[0].done`
- **traceback**: 1 calls - `traceback.print_exc`
- **url**: 4 calls - `url.encode, url.lower, url.split, url.startswith`
- **urlparse(a['href'])**: 1 calls - `urlparse(a['href']).path.lower`
- **w**: 1 calls - `w.run`
- **yaml**: 2 calls - `yaml.dump, yaml.safe_load`

### 🏗️ Class Inheritance Map

- `CookieInvalidError` ← `RuntimeError`
- `CookieNotFoundError` ← `RuntimeError`

---

## 📋 Report Generation Metadata

- **Generated on:** 2025-06-23 23:28:57
- **Script version:** AI Code Mapper v2.0
- **Analysis root:** `K:\O meu disco\Código\Fórum SMPT`
- **Files analyzed:** 10
- **Total errors:** 0
- **Self-awareness:** Skipped analysis of `Mapeador.py`

*This report is optimized for AI model comprehension and code modification assistance.*
