#!/usr/bin/env python3
import os
import sys
import subprocess

# Suppress pip version check
os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")

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
from urllib.parse import urlparse

from config import load_config, get_cookies, set_cookies
from state import State
from throttle import ThrottleController
from fetch import Fetcher
from crawler import DiscoverWorker

BASE_URL = "https://sm-portugal.forumeiros.com/"

async def periodic_save(state: State, interval: int):
    while True:
        await asyncio.sleep(interval)
        await state.save()
        print("[Auto-save] State and cache saved.")

async def main():
    parser = argparse.ArgumentParser(description="Backup ForumSMPTCrawler")
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
        "--workers", type=int, help="Override number of concurrent workers"
    )
    parser.add_argument(
        "--delay", type=float, help="Override base delay between requests"
    )
    args = parser.parse_args()

    config = load_config()
    if args.workers:
        config.workers = args.workers
    if args.delay:
        config.base_delay = args.delay

    state_file = os.path.join(os.getcwd(), "crawl_state.json")
    cache_file = os.path.join(os.getcwd(), "assets_cache.json")
    if args.reset:
        for fpath in (state_file, cache_file):
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[Reset] Removed {fpath}")
        sys.exit(0)

    final_file = state_file.replace(".json", "_final.json")

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
        print("Provide the 4 cookies (_fa-screen, fa_sm-portugal_forumeiros_com_data,")
        print("fa_sm-portugal_forumeiros_com_sid, fa_sm-portugal_forumeiros_com_t):")
        cookies["_fa-screen"] = input("_fa-screen: ").strip()
        cookies["fa_sm-portugal_forumeiros_com_data"] = input(
            "fa_sm-portugal_forumeiros_com_data: "
        ).strip()
        cookies["fa_sm-portugal_forumeiros_com_sid"] = input(
            "fa_sm-portugal_forumeiros_com_sid: "
        ).strip()
        cookies["fa_sm-portugal_forumeiros_com_t"] = input(
            "fa_sm-portugal_forumeiros_com_t: "
        ).strip()
        set_cookies(cookies)
        print("[Cookies] Saved to cookies.json")

    # Initialize crawl state
    skip_crawling = False
    if os.path.exists(final_file):
        print("[Resume] Detected final crawl state file. Skipping discovery phase.")
        skip_crawling = True
        state_path_to_use = final_file
    else:
        state_path_to_use = state_file

    state = State(config, state_path=state_path_to_use, cache_path=cache_file)

    # Show status and exit if requested
    if args.status:
        total = len(state.urls)
        done = sum(1 for v in state.urls.values() if v["status"] == "done")
        pending = sum(1 for v in state.urls.values() if v["status"] == "pending")
        errors = sum(1 for v in state.urls.values() if v["status"] == "error")
        print(
            f"Total URLs: {total}, Done: {done}, Pending: {pending}, Errors: {errors}"
        )
        sys.exit(0)

    # Seed initial URL if starting fresh
    if not state.urls and not skip_crawling:
        await state.add_url(BASE_URL)
        print(f"[Seed] Added initial URL to crawl: {BASE_URL}")

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
        print("[Phase-1] Discovering links...")

        # Import DiscoverWorker (assumindo que existe no módulo crawler)
        from crawler import DiscoverWorker

        # Começamos apenas com 1 DiscoverWorker
        discover_tasks = []
        first_worker = DiscoverWorker(config, state, fetcher, worker_id=1)
        discover_tasks.append(asyncio.create_task(first_worker.run()))

        additional_started = False

        # Monitoriza a fila a cada segundo
        while not additional_started:
            await asyncio.sleep(1)
            pending = state.pending_count()  # novo método em state.py
            if pending >= 20:
                print(f"[Phase-1] {pending} links pendentes → activando restantes workers…")
                for i in range(2, config.workers + 1):
                    w = DiscoverWorker(config, state, fetcher, worker_id=i)
                    discover_tasks.append(asyncio.create_task(w.run()))
                additional_started = True

            # Caso o worker 1 acabe antes de chegar a 20 links, lançamos os outros mesmo assim
            if discover_tasks[0].done() and not additional_started:
                print("[Phase-1] Lista estabilizou antes dos 20 links → lançando restantes.")
                for i in range(2, config.workers + 1):
                    w = DiscoverWorker(config, state, fetcher, worker_id=i)
                    discover_tasks.append(asyncio.create_task(w.run()))
                additional_started = True

        # Espera todos os DiscoverWorkers terminarem
        await asyncio.gather(*discover_tasks)
        print("[Phase-1] Descoberta terminada.")

        await state.save()
        try:
            shutil.copy(state_file, final_file)
        except Exception as e:
            print(f"[Error] Could not save final crawl state: {e}")
        if shutdown_after_crawl:
            print("Shutting down system as requested...")
            await fetcher.close()
            if os.name == 'nt':
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

    to_download = sum(1 for v in state.urls.values() if v["status"] == "discovered")
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
