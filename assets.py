import os
import hashlib
from urllib.parse import urljoin, urlparse
import mimetypes
from typing import Optional

BASE_DOMAIN = "sm-portugal.forumeiros.com"
BASE_URL = f"https://{BASE_DOMAIN}"

OUTPUT_DIR = os.getenv("FORUMSMPT_BACKUP_DIR", os.path.join(os.getcwd(), "ForumSMPT"))
IMAGES_INTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "imagens", "internal")
IMAGES_EXTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "imagens", "external")
FILES_INTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "files", "internal")
FILES_EXTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "files", "external")

for d in (IMAGES_INTERNAL_DIR, IMAGES_EXTERNAL_DIR, FILES_INTERNAL_DIR, FILES_EXTERNAL_DIR):
    os.makedirs(d, exist_ok=True)

IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}

async def download_asset(resource_url: str, fetcher, state) -> Optional[str]:
    """
    Download and cache an asset (image or file).
    Returns the local file path if successful, or None on failure.
    """
    abs_url = resource_url if resource_url.startswith("http") else urljoin(BASE_URL, resource_url)
    existing = state.get_asset(abs_url)
    if existing:
        print(f"[Asset] Already cached: {abs_url}")
        return existing
    print(f"[Asset] Downloading: {abs_url}")
    parsed = urlparse(abs_url)
    _, ext = os.path.splitext(parsed.path)
    ext = ext.lower()
    is_image = ext in IMAGE_EXTS
    if not ext:
        mime, _ = mimetypes.guess_type(parsed.path)
        ext = mimetypes.guess_extension(mime) or '.bin'
    if is_image:
        base_dir = IMAGES_INTERNAL_DIR if parsed.netloc == BASE_DOMAIN else IMAGES_EXTERNAL_DIR
    else:
        base_dir = FILES_INTERNAL_DIR if parsed.netloc == BASE_DOMAIN else FILES_EXTERNAL_DIR
    filename = hashlib.md5(abs_url.encode()).hexdigest() + ext
    local_path = os.path.join(base_dir, filename)
    status, data = await fetcher.fetch_bytes(abs_url)
    if status == 200 and data:
        try:
            with open(local_path, "wb") as f:
                f.write(data)
        except Exception as e:
            print(f"[Asset] Error writing asset to {local_path}: {e}")
            return None
        try:
            await state.add_asset(abs_url, local_path)
        except Exception as e:
            print(f"[Asset] Error caching asset URL {abs_url}: {e}")
        print(f"[Asset] Saved asset: {abs_url} -> {local_path}")
        return local_path
    else:
        print(f"[Asset] Failed to download {abs_url} (status {status})")
        return None