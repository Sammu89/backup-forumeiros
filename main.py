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

    # Set URL into settings
    st.BASE_URL = forum_url

    # ----- choose backup folder on Desktop -----
    # derive the slug (subdomain) from the BASE_URL
    slug = st.get_base_domain().split(".")[0]
    st.BACKUP_ROOT = (desktop_dir / slug).resolve()
    st.BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    print(f"[Init] Target forum  : {st.BASE_URL}")
    print(f"[Init] Backup folder : {st.BACKUP_ROOT}")

    config = load_config()

    if args.workers:
        config.workers = args.workers
    if args.delay:
        config.base_delay = args.delay

    state_file = os.path.join(os.getcwd(), "crawl_state.json")
    final_file = state_file.replace(".json", "_final.json")
    cache_file = os.path.join(os.getcwd(), "assets_cache.json")
    
    if args.reset:
        for fpath in (state_file, cache_file):
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[Reset] Removed {fpath}")
        sys.exit(0)

    cookies = get_cookies()
    # Validate existing cookies if present
    if cookies:
        throttle_test = ThrottleController(config)
        fetcher_test = Fetcher(config, throttle_test, cookies)
        status, _, _ = await fetcher_test.fetch_text(
            "https://sm-portugal.forumeiros.com/privmsg?folder=inbox",
            allow_redirects=False,
        )
        await fetcher_test.close()
        if status == 200:
            print("[Cookies] Existing cookies are valid.")
        else:
            print("[Cookies] Cookies expired or invalid.")
            cookies = {}

    # Prompt for cookies if not valid
    if not cookies:
        print("Provide the 4 cookies (_fa-screen, fa_data,")
        print("fa_sid, fa_t):")
        cookies["_fa-screen"] = input("_fa-screen: ").strip()
        cookies["fa_data"] = input(
            "fa_data: "
        ).strip()
        cookies["fa_sid"] = input(
            "fa_sid: "
        ).strip()
        cookies["fa_t"] = input(
            "fa_t: "
        ).strip()
        set_cookies(cookies)
        print("[Cookies] Saved to cookies.json")

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