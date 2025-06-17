#!/usr/bin/env python3
"""
Verifica e instala automaticamente aiohttp, PyYAML e beautifulsoup4 se não estiverem presentes.
"""

import os, sys, subprocess

# Suprimir aviso de versão do pip
os.environ.setdefault("PIP_DISABLE_PIP_VERSION_CHECK", "1")

# -------------------- Dependency Check & Installation --------------------
required = [("aiohttp","aiohttp"), ("PyYAML","PyYAML"), ("beautifulsoup4","bs4")]
for pkg, imp in required:
    try:
        __import__(imp)
    except ImportError:
        print(f"[Setup] Instalando: {pkg}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg, "-q"]
        )

# imports normais

import argparse
import asyncio
import os
import sys

from config import load_config, get_cookies, set_cookies
from state import State
from throttle import ThrottleController
from fetch import Fetcher
from crawler import CrawlWorker

BASE_URL = "https://sm-portugal.forumeiros.com/"

async def periodic_save(state: State, interval: int):
    while True:
        await asyncio.sleep(interval)
        # chama o save de modo não-bloqueante
        await asyncio.to_thread(state.save)
        print("[Auto-save] State and cache saved.")


async def main():
    parser = argparse.ArgumentParser(description="Backup ForumSMPTCrawler")
    parser.add_argument("--resume", action="store_true", help="Resume from existing state")
    parser.add_argument("--reset", action="store_true", help="Reset state and start fresh")
    parser.add_argument("--status", action="store_true", help="Show crawl status and exit")
    parser.add_argument("--workers", type=int, help="Override number of concurrent workers")
    parser.add_argument("--delay", type=float, help="Override base delay between requests")
    args = parser.parse_args()

    # Load config
    config = load_config()
    # Override if provided
    if args.workers:
        config.workers = args.workers
    if args.delay:
        config.base_delay = args.delay

    # Handle reset
    state_file = os.path.join(os.getcwd(), "crawl_state.json")
    cache_file = os.path.join(os.getcwd(), "assets_cache.json")
    if args.reset:
        for fpath in (state_file, cache_file):
            if os.path.exists(fpath):
                os.remove(fpath)
                print(f"[Reset] Removed {fpath}")
        sys.exit(0)

    # Load/set cookies
# Load existing cookies from cookies.json
    cookies = get_cookies()

    # Se houver cookies, testa-os antes de perguntar de novo
    if cookies:
        # Cria um fetcher temporário só para testar
        throttle_test = ThrottleController(config)
        fetcher_test = Fetcher(config, throttle_test, cookies)
        status, _ = await fetcher_test.fetch_text(
            "https://sm-portugal.forumeiros.com/privmsg?folder=inbox",
            allow_redirects=False
        )
        await fetcher_test.close()
        if status == 200:
            print("[Cookies] Cookies existentes válidos, usando-os.")
        else:
            print("[Cookies] Cookies expirados ou inválidos.")
            cookies = {}  # força redigitação

    # Se não tiver cookies válidos, pede de novo
    if not cookies:
        print("Fornece os 4 cookies (_fa-screen, fa_sm-portugal_forumeiros_com_data,")
        print("fa_sm-portugal_forumeiros_com_sid e fa_sm-portugal_forumeiros_com_t):")
        cookies["_fa-screen"] = input("_fa-screen: ").strip()
        cookies["fa_sm-portugal_forumeiros_com_data"] = input("fa_sm-portugal_forumeiros_com_data: ").strip()
        cookies["fa_sm-portugal_forumeiros_com_sid"] = input("fa_sm-portugal_forumeiros_com_sid: ").strip()
        cookies["fa_sm-portugal_forumeiros_com_t"] = input("fa_sm-portugal_forumeiros_com_t: ").strip()
        set_cookies(cookies)
        print("[Cookies] Gravados em cookies.json")

    # Initialize state
    state = State(config, state_path=state_file, cache_path=cache_file)

    # Show status and exit
    if args.status:
        total = len(state.urls)
        done = sum(1 for v in state.urls.values() if v["status"] == "done")
        pending = sum(1 for v in state.urls.values() if v["status"] == "pending")
        errors = sum(1 for v in state.urls.values() if v["status"] == "error")
        print(f"Total URLs: {total}, Done: {done}, Pending: {pending}, Errors: {errors}")
        sys.exit(0)

    # Seed initial URL if fresh
    if not state.urls:
        state.add_url(BASE_URL)


    # Initialize throttle and fetcher
    throttle = ThrottleController(config)
    fetcher = Fetcher(config, throttle, cookies)

    # Start periodic saving task
    save_task = asyncio.create_task(periodic_save(state, config.save_every * 1))

    # Spawn crawler workers
    workers = [CrawlWorker(config, state, fetcher) for _ in range(config.workers)]
    tasks = [asyncio.create_task(w.run()) for w in workers]

    # Wait for all workers to finish
    await asyncio.gather(*tasks)

    # Cleanup
    save_task.cancel()
    await fetcher.close()
    # state.save é síncrono — chama sem await
    state.save()
    print("Crawl complete. All state saved.")



if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")