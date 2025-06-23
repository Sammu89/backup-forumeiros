#!/usr/bin/env python3

import argparse
import asyncio
import os
from os import path
import sys
import subprocess
import shutil

import aiohttp

from pathlib import Path

from urllib.parse import unquote, urlparse

import settings as st
from settings import (
    get_config_path,
    get_cookies_path,
    get_base_domain,
    load_config,
    set_cookies,
)

from auth import (
    load_cookies,
    is_logged_in,
    CookieNotFoundError,
    CookieInvalidError,
)
from state import State
from throttle import ThrottleController
from fetch import Fetcher
from crawler import DiscoverWorker


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



# Import the real settings module and basic paths


# Desktop folder variable
desktop_dir = Path.home() / "Desktop"



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
    default_url = "https://sm-portugal.forumeiros.com/"
    if args.forum:
        forum_url = args.forum.strip().rstrip("/")
    else:
        user_input = input(f"Forum base URL to backup (default {default_url}): ").strip()
        if not user_input:
            raw_url = default_url
        else:
            raw_url = user_input
        # normalize to HTTPS and drop any trailing slash
        if raw_url.startswith("http://"):
            raw_url = "https://" + raw_url[len("http://"):]
        forum_url = raw_url.rstrip("/")
    # ensure scheme
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
    import settings as config

    print("\n" + "="*70)
    print("🚀 FORUM BACKUP CRAWLER - Initialization")
    print("="*70)
    print(f"🎯 Target Forum  : {st.BASE_URL}")
    print(f"📁 Backup Folder : {st.BACKUP_ROOT}")
    print("="*70)

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

    # ─── COOKIE LOADING & AUTHENTICATION ─────────────────────────────────

    # Derive our FA cookie names
    domain_slug = get_base_domain().replace(".", "_")
    data_key    = f"fa_{domain_slug}_data"
    sid_key     = f"fa_{domain_slug}_sid"

        

    # Load saved cookies if the file exists; otherwise prompt once
    cookie_file = get_cookies_path()
    if path.exists(cookie_file):
        try:
            cookies = load_cookies(cookie_file)
            print("✅ [Cookies] Loaded saved cookies")
        except CookieInvalidError as e:
            print(f"⚠️ [Cookies] Invalid cookie file: {e}")
            cookies = {}
    else:
        # ─── INTERACTIVE COOKIE SETUP ─────────────────────────────────────
        print("\n" + "="*70)
        print("🔐 LOGIN REQUIRED - Cookie Authentication Setup")
        print("="*70)
        print(f"Domain: {get_base_domain()}\n")
        print("To obtain your login cookies:")
        print("┌─ Step 1: Login to your forum in a web browser")
        print("├─ Step 2: Open Developer Tools (F12 or Ctrl+Shift+I)")
        print("├─ Step 3: Go to 'Application' tab → 'Storage' → 'Cookies'")
        print(f"├─ Step 4: Find cookies for '{get_base_domain()}'")
        print("└─ Step 5: Copy the values for the cookies below")
        print("\n" + "-"*70)
        print("Required cookies:")
        print(f"• {data_key}")
        print(f"• {sid_key}")
        print("-"*70)

        cookies = {}
        cookies[data_key] = input(f"📋 Enter {data_key}: ").strip()
        cookies[sid_key]  = input(f"📋 Enter {sid_key}: ").strip()
        if not (cookies[data_key] and cookies[sid_key]):
            print("❌ Both cookies are required. Exiting…")
            sys.exit(1)

        set_cookies(cookies)
        print("✅ [Cookies] Saved to cookies.json")

    # 2) Delegate full login check to auth_async.is_logged_in
    async with aiohttp.ClientSession() as sess:
        sess.cookie_jar.update_cookies(cookies)
        try:
            logged = await is_logged_in(sess, st.BASE_URL + "/")
        except RuntimeError as e:
            print(f"⚠️ [Auth check error] {e}")
            logged = False

        if not logged:
            print("⚠️ [Authentication] Not authenticated (anonymous session)")
            choice = input("Authentication failed with saved cookies. Reconfigure cookies? (y/N): ")
            if choice.strip().lower() in ("y", "yes"):
                # ─── INTERACTIVE COOKIE RECONFIGURATION ──────────────────────────────
                print("\n" + "="*70)
                print("🔐 COOKIE RECONFIGURATION")
                print("="*70)
                print(f"Domain: {get_base_domain()}\n")
                print("To obtain your login cookies:")
                print("┌─ Step 1: Login to your forum in a web browser")
                print("├─ Step 2: Open Developer Tools (F12 or Ctrl+Shift+I)")
                print("├─ Step 3: Go to 'Application' tab → 'Storage' → 'Cookies'")
                print(f"├─ Step 4: Find cookies for '{get_base_domain()}'")
                print("└─ Step 5: Copy the values for the cookies below")
                print("\n" + "-"*70)
                print("Required cookies:")
                print(f"• {data_key}")
                print(f"• {sid_key}")
                print("-"*70)

                cookies = {}
                cookies[data_key] = input(f"📋 Enter {data_key}: ").strip()
                cookies[sid_key]  = input(f"📋 Enter {sid_key}: ").strip()
                if not (cookies[data_key] and cookies[sid_key]):
                    print("❌ Both cookies are required. Exiting…")
                    sys.exit(1)

                set_cookies(cookies)
                print("✅ [Cookies] Saved to cookies.json")
                # ─────────────────────────────────────────────────────────────────

                # Retry authentication
                sess.cookie_jar.clear()
                sess.cookie_jar.update_cookies(cookies)
                try:
                    logged = await is_logged_in(sess, st.BASE_URL + "/")
                except RuntimeError as e:
                    print(f"⚠️ [Auth check error] {e}")
                    logged = False

                if not logged:
                    print("❌ Authentication still failed. Exiting…")
                    sys.exit(1)
            else:
                print("⚠️ Proceeding anonymously.")
        else:
            print("✅ [Authentication] Login verified successfully")

    # Final status message (duplicate of above, you may keep or remove)
    if logged:
        print("✅ [Authentication] Login verified successfully")
    else:
        print("⚠️  [Warning] Not authenticated (anonymous session)")


    # Initialize crawl state (always load from main state; use final_file only to skip discovery)
    skip_crawling = args.resume or os.path.exists(final_file)
    state = State(config, state_path=state_file, cache_path=cache_file)

    # Show status and exit if requested
    if args.status:
        total = len(state.urls)
        done = sum(1 for v in state.urls.values() if v["status"] == "downloaded")
        pending = sum(1 for v in state.urls.values() if v["status"] == "pending")
        errors = sum(1 for v in state.urls.values() if v["status"] == "error")
        
        print("\n" + "="*50)
        print("📊 CRAWL STATUS REPORT")
        print("="*50)
        print(f"📋 Total URLs    : {total:,}")
        print(f"✅ Downloaded    : {done:,}")
        print(f"⏳ Pending       : {pending:,}")
        print(f"❌ Errors        : {errors:,}")
        print(f"📈 Progress      : {(done/total*100):.1f}%" if total > 0 else "📈 Progress      : 0.0%")
        print("="*50)
        sys.exit(0)

    # Seed initial URL if starting fresh
    if not state.urls and not skip_crawling:
        await state.add_url("/")  # usar só o path "/" como seed
        print(f"🌱 [Seed] Added initial URL: {st.BASE_URL}")

    throttle = ThrottleController(config)
    fetcher = Fetcher(config, throttle, cookies)

    if skip_crawling:
        print(f"\n⏭️  [Resume Mode] Skipping crawl phase")
        print(f"🔄 Starting download with {config.workers} workers...")
    else:
        print(f"\n🚀 [Fresh Start] Beginning crawl with {config.workers} workers...")

    shutdown_after_crawl = False
    if not skip_crawling:
        print("\n" + "-"*50)
        choice = input("💻 Shut down PC after crawling completes? (y/N): ")
        if choice.strip().lower() in ('y', 'yes'):
            shutdown_after_crawl = True
            print("✅ System will shutdown automatically after crawling")
        else:
            print("ℹ️  System will remain on after crawling")
        print("-"*50)

    # -------------------- FASE 1: DISCOVERY --------------------
    if not skip_crawling:
        print("\n" + "="*70)
        print("🔍 PHASE 1: URL DISCOVERY")
        print("="*70)
        print("🔄 Starting with 1 discovery worker...")

        from crawler import DiscoverWorker

        max_workers = 7   # total de crawlers de descoberta desejados

        # 1️⃣ Começa com só 1 DiscoverWorker
        tasks = [asyncio.create_task(DiscoverWorker(config, state, fetcher, worker_id=1).run())]
        escalated = False

        # Escala para max_workers quando pendentes ≥ 20 ou o primeiro terminar
        while not escalated:
            await asyncio.sleep(1)
            if state.pending_count() >= 20 or tasks[0].done():
                print(f"⚡ Scaling up to {max_workers} discovery workers...")
                for i in range(2, max_workers + 1):
                    tasks.append(asyncio.create_task(DiscoverWorker(config, state, fetcher, worker_id=i).run()))
                escalated = True

        # Espera todos os crawlers de discovery terminarem
        await asyncio.gather(*tasks)
        print("✅ Discovery phase completed!")
        print("="*70)

        # Marca estado final e copia
        await state.save()
        try:
            shutil.copy(state_file, final_file)
        except Exception as e:
            print(f"❌ [Error] Could not save final crawl state: {e}")

        if shutdown_after_crawl:
            print("\n🔄 Shutting down system as requested...")
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
        print("📦 [Setup] Installing progress bar library...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm", "-q"])
        from tqdm.asyncio import tqdm

    # Import DownloadWorker (assumindo que existe no módulo crawler)
    from crawler import DownloadWorker

    to_download = sum(1 for v in state.urls.values() if v["status"] == "listed")
    
    print("\n" + "="*70)
    print("📥 PHASE 2: CONTENT DOWNLOAD")
    print("="*70)
    print(f"📄 Pages to download: {to_download:,}")
    print(f"⚙️  Download workers: {config.workers}")
    print("="*70)
    
    progress = tqdm(total=to_download, unit="page", desc="Downloading")

    download_workers = [
        DownloadWorker(config, state, fetcher, progress, worker_id=i + 1)
        for i in range(config.workers)
    ]
    await asyncio.gather(*[asyncio.create_task(w.run()) for w in download_workers])
    progress.close()

    print("✅ Download phase completed!")
    print("="*70)

    # -------------------- FIM & LIMPEZA --------------------
    await state.save()
    await fetcher.close()
    try:
        shutil.copy(state_file, final_file)
    except Exception:
        pass
    
    print("\n" + "="*70)
    print("🎉 BACKUP COMPLETED SUCCESSFULLY!")
    print("="*70)
    print(f"📁 Backup saved to: {st.BACKUP_ROOT}")
    print("="*70)

    # ─── CLEAN UP TEMP FILES PROMPT ────────────────────────────────────────
    print("\n🧹 Cleanup Options:")
    print("The following temporary files can be safely deleted:")
    print("• crawl_state.json (crawl progress tracking)")
    print("• assets_cache.json (download cache)")
    print("• config.yaml (crawler configuration)")
    print("• cookies.json (authentication cookies)")
    print("\nNote: Main backup content will be preserved")
    print("-"*50)
    
    resp = input("🗑️  Delete temporary files? (y/N): ")
    if resp.strip().lower() in ('y', 'yes'):
        deleted_count = 0
        for f in (state_file, cache_file, get_config_path(), get_cookies_path()):
            try: 
                if os.path.exists(f):
                    os.remove(f)
                    deleted_count += 1
            except: 
                pass
        print(f"✅ Deleted {deleted_count} temporary files")
    else:
        print("ℹ️  Temporary files retained for future use")

if __name__ == "__main__":
    state = None
    fetcher = None  # Initialize fetcher variable for finally block
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Operation interrupted by user")
        print("💾 Attempting to save current progress...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("💾 Attempting to save current progress...")
    finally:
        # Final safety-save + close fetcher
        if 'state' in locals() and state is not None:
            try:
                asyncio.run(state.save())
                print("✅ Progress saved successfully")
            except:
                print("❌ Could not save progress")

        if 'fetcher' in locals() and fetcher is not None:
            try:
                asyncio.run(fetcher.close())
            except:
                pass
        
        print("👋 Goodbye!")
        
if __name__ == "__main__":
    asyncio.run(main())