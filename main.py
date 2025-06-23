#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

# Suppress pip version check
os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")

if sys.version_info < (3, 9):
    print("Python 3.9 or higher is required for this program.", file=sys.stderr)
    sys.exit(1)

# Dependency check and installation (if needed)
required = [("aiohttp", "aiohttp"), ("PyYAML", "yaml"), ("beautifulsoup4", "bs4"), ("tqdm", "tqdm")]

for pkg, imp in required:
    try:
        __import__(imp)
    except ImportError:
        print(f"[Setup] Installing: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

import argparse
import asyncio
import shutil
from pathlib import Path
from urllib.parse import urlparse

# Import the real settings module and basic paths
import settings as st
from pathlib import Path

# Desktop folder variable
desktop_dir = Path.home() / "Desktop"

from config import load_config, get_cookies, set_cookies
from state import State
from throttle import ThrottleController
from fetch import Fetcher
from crawler import DiscoverWorker

async def periodic_save(state: State, interval: int):
    while True:
        await asyncio.sleep(interval)
        await state.save()
        print("[Auto-save] State and cache saved.")

async def main():
    global state, fetcher
    
    parser = argparse.ArgumentParser(description="Forum backup crawler")
    parser.add_argument(
        "--resume", action="store_true", help="Resume from existing state"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Reset state and start fresh"
    )
    parser.add_argument(
        "--status", action="store_true", help="Show crawl status and exit"
    )
    parser.add_argument(
        "--workers", type=int, help="Override workers"
    )
    parser.add_argument(
        "--delay", type=float, help="Override base delay between requests"
    )
    parser.add_argument(
        "--forum",
        metavar="URL",
        help="Base forum URL to backup (e.g. https://myforum.forumeiros.com)",
    )
    
    args = parser.parse_args()

    # ----- resolve forum URL -----
    if args.forum:
        forum_url = args.forum.strip().rstrip("/")
    else:
        forum_url = input(
            "Forum base URL to backup (e.g. https://myforum.forumeiros.com): "
        ).strip().rstrip("/")

    if not forum_url.startswith(("http://", "https://")):
        forum_url = "https://" + forum_url
        
    from urllib.parse import urlparse

    # Store the forum URL in settings
    st.BASE_URL = forum_url

   # Now derive & store the domain
    st.BASE_DOMAIN = urlparse(st.BASE_URL).netloc


    # ----- choose backup folder on Desktop -----
    # derive the slug (subdomain) from the BASE_URL
    slug = st.get_base_domain().split(".")[0]
    st.BACKUP_ROOT = (desktop_dir / slug).resolve()
    st.BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    # ─── Redirect config/cookies into backup folder ───────────────────
    import config
    # point config.yaml and cookies.json into this forum's folder
    config.CONFIG_PATH  = str(st.BACKUP_ROOT / "config.yaml")
    config.COOKIES_PATH = str(st.BACKUP_ROOT / "cookies.json")

    print(f"[Init] Target forum  : {st.BASE_URL}")
    print(f"[Init] Backup folder : {st.BACKUP_ROOT}")

    config = load_config()

    if args.workers:
        config.workers = args.workers
    if args.delay:
        config.base_delay = args.delay

    # state & cache live inside the forum's backup folder
    state_file = str(st.BACKUP_ROOT / "crawl_state.json")
    final_file = str(st.BACKUP_ROOT / "crawl_state_final.json")
    cache_file = str(st.BACKUP_ROOT / "assets_cache.json")
    
    if args.reset:
        for fpath in (state_file, cache_file):
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[Reset] Removed {fpath}")
        sys.exit(0)

    # ─── COOKIE LOADING & LOGIN CHECK ──────────────────────────────────────
    # Only two cookies matter: fa_<domain>_data and fa_<domain>_sid
    from settings import get_base_domain
    raw = get_cookies()
    domain_slug = get_base_domain().replace(".", "_")
    data_key = f"fa_{domain_slug}_data"
    sid_key  = f"fa_{domain_slug}_sid"

    # Extract only those two (if present)
    cookies = {}
    if data_key in raw and sid_key in raw:
        cookies[data_key] = raw[data_key]
        cookies[sid_key]  = raw[sid_key]

    # Verify login by fetching "/", looking for "/register" (only guests see it)
    if cookies:
        tc = ThrottleController(config)
        fc = Fetcher(config, tc, cookies)
        status, html, *_ = await fc.fetch_text(f"{st.BASE_URL}/", allow_redirects=True)
        await fc.close()
        if status == 200 and "/register" not in html:
            print("[Cookies] Existing cookies are valid.")
        else:
            print("[Cookies] Cookies expired or invalid.")
            cookies = {}

    # Prompt only for the two needed cookies when missing/invalid
    if not cookies:
        print(f"Provide login cookies for domain '{get_base_domain()}':")
        cookies[data_key] = input(f"{data_key}: ").strip()
        cookies[sid_key]  = input(f"{sid_key}: ").strip()
        set_cookies(cookies)
        print("[Cookies] Saved to cookies.json")

    # ─── LOGIN VERIFICATION ─────────────────────────────────────────────────
    # Immediately after loading cookies, verify we're actually logged in.
    # If we still see a "/register" link, the session is anonymous.
    login_throttle = ThrottleController(config)
    login_fetcher  = Fetcher(config, login_throttle, cookies)
    status, root_html, *_ = await login_fetcher.fetch_text(f"{st.BASE_URL}/", allow_redirects=True)
    await login_fetcher.close()
    if status == 200:
        if '/register' in root_html:
            print("[Warning] Login appears to have failed (found '/register'); proceeding without authentication.")
    else:
        print(f"[Warning] Could not verify login (status {status}); proceeding without authentication.")

    # Initialize crawl state (always load from main state; use final_file only to skip discovery)
    skip_crawling = args.resume or os.path.exists(final_file)
    state = State(config, state_path=state_file, cache_path=cache_file)

    # Show status and exit if requested
    if args.status:
        total = len(state.urls)
        done = sum(1 for v in state.urls.values() if v["status"] == "downloaded")
        pending = sum(1 for v in state.urls.values() if v["status"] == "pending")
        errors = sum(1 for v in state.urls.values() if v["status"] == "error")
        print(
            f"Total URLs: {total}, Done: {done}, Pending: {pending}, Errors: {errors}"
        )
        sys.exit(0)

    # Seed initial URL if starting fresh
    if not state.urls and not skip_crawling:
        await state.add_url("/")  # usar só o path "/" como seed
        print(f"[Seed] Added initial URL to crawl: {st.BASE_URL}")

    throttle = ThrottleController(config)
    fetcher = Fetcher(config, throttle, cookies)

    if skip_crawling:
        print(f"[Init] Skipping crawl phase. Proceeding to download with {config.workers} workers...")
    else:
        print(f"[Init] Starting crawl with {config.workers} workers...")

    shutdown_after_crawl = False
    if not skip_crawling:
        choice = input("Do you want to shut down the PC after crawling? (y/N): ")
        if choice.strip().lower() in ('y', 'yes'):
            shutdown_after_crawl = True

    # -------------------- FASE 1: DISCOVERY --------------------
    if not skip_crawling:
        print("[Phase-1] Starting discovery with 1 worker…")

        from crawler import DiscoverWorker

        max_workers = 7   # total de crawlers de descoberta desejados

        # 1️⃣ Começa com só 1 DiscoverWorker
        tasks = [asyncio.create_task(DiscoverWorker(config, state, fetcher, worker_id=1).run())]
        escalated = False

        # Escala para max_workers quando pendentes ≥ 20 ou o primeiro terminar
        while not escalated:
            await asyncio.sleep(1)
            if state.pending_count() >= 20 or tasks[0].done():
                print(f"[Phase-1] Escalando para {max_workers} trabalhadores…")
                for i in range(2, max_workers + 1):
                    tasks.append(asyncio.create_task(DiscoverWorker(config, state, fetcher, worker_id=i).run()))
                escalated = True

        # Espera todos os crawlers de discovery terminarem
        await asyncio.gather(*tasks)
        print("[Phase-1] Descoberta terminada.")

        # Marca estado final e copia
        await state.save()
        try:
            shutil.copy(state_file, final_file)
        except Exception as e:
            print(f"[Error] Could not save final crawl state: {e}")

        if shutdown_after_crawl:
            print("Shutting down system as requested…")
            await fetcher.close()
            if os.name == "nt":
                os.system("shutdown /s /t 5")
            else:
                os.system("shutdown -h now")
            return

    # -------------------- FASE 2: DOWNLOAD --------------------
    try:
        from tqdm.asyncio import tqdm  # garante pip install tqdm
    except ImportError:
        print("[Setup] Installing: tqdm")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm", "-q"])
        from tqdm.asyncio import tqdm

    # Import DownloadWorker (assumindo que existe no módulo crawler)
    from crawler import DownloadWorker

    to_download = sum(1 for v in state.urls.values() if v["status"] == "listed")
    print(f"[Phase-2] Need to download {to_download} pages...")
    progress = tqdm(total=to_download, unit="page")

    download_workers = [
        DownloadWorker(config, state, fetcher, progress, worker_id=i + 1)
        for i in range(config.workers)
    ]
    await asyncio.gather(*[asyncio.create_task(w.run()) for w in download_workers])
    progress.close()

    # -------------------- FIM & LIMPEZA --------------------
    await state.save()
    await fetcher.close()
    try:
        shutil.copy(state_file, final_file)
    except Exception:
        pass
    print("Crawl complete. All state saved.")

    # ─── CLEAN UP TEMP FILES PROMPT ────────────────────────────────────────
    resp = input("Delete temporary files (crawl_state.json, assets_cache.json, config.yaml, cookies.json)? (y/N): ")
    if resp.strip().lower() in ('y', 'yes'):
        for f in (state_file, cache_file, config.CONFIG_PATH, config.COOKIES_PATH):
            try: 
                os.remove(f)
            except: 
                pass
        print("Temporary files deleted.")
    else:
        print("Temporary files retained in backup folder.")

if __name__ == "__main__":
    state = None
    fetcher = None  # Initialize fetcher variable for finally block
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
    finally:
        # Final safety-save + close fetcher
        if 'state' in locals() and state is not None:
            try:
                asyncio.run(state.save())
            except:
                pass

        if 'fetcher' in locals() and fetcher is not None:
            try:
                asyncio.run(fetcher.close())
            except:
                pass