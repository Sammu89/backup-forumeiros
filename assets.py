import os
import hashlib
from urllib.parse import urljoin, urlparse
import mimetypes
from typing import Optional

# Base URL/domain for internal vs external classification
BASE_DOMAIN = "sm-portugal.forumeiros.com"
BASE_URL = f"https://{BASE_DOMAIN}"

# Directory structure for assets
OUTPUT_DIR = os.getenv("FORUMSMPT_BACKUP_DIR", os.path.join(os.getcwd(), "ForumSMPT"))
IMAGES_INTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "imagens", "internal")
IMAGES_EXTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "imagens", "external")
FILES_INTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "files", "internal")
FILES_EXTERNAL_DIR = os.path.join(OUTPUT_DIR, "assets", "files", "external")

# Supported image extensions
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.bmp', '.ico'}

# Ensure directories exist
for d in (IMAGES_INTERNAL_DIR, IMAGES_EXTERNAL_DIR, FILES_INTERNAL_DIR, FILES_EXTERNAL_DIR):
    os.makedirs(d, exist_ok=True)

async def download_asset(resource_url: str, fetcher, state) -> Optional[str]:
    """
    Download and cache an asset (image or file).
    Returns local path or None on failure.
    """
    # Resolve relative URLs
    abs_url = resource_url if resource_url.startswith("http") else urljoin(BASE_URL, resource_url)
    # Check existing cache
    existing = state.get_asset(abs_url)
    if existing:
        return existing

    # Determine folder and file type
    parsed = urlparse(abs_url)
    _, ext = os.path.splitext(parsed.path)
    ext = ext.lower()
    is_image = ext in IMAGE_EXTS

    # Default ext if missing
    if not ext:
        # try guess from MIME
        mime, _ = mimetypes.guess_type(parsed.path)
        ext = mimetypes.guess_extension(mime) or '.bin'
    
    # Choose directory
    if is_image:
        base_dir = IMAGES_INTERNAL_DIR if parsed.netloc == BASE_DOMAIN else IMAGES_EXTERNAL_DIR
    else:
        base_dir = FILES_INTERNAL_DIR if parsed.netloc == BASE_DOMAIN else FILES_EXTERNAL_DIR

    # Unique filename via hash
    name = hashlib.md5(abs_url.encode()).hexdigest() + ext
    local_path = os.path.join(base_dir, name)

    # Fetch
    status, data = await fetcher.fetch_bytes(abs_url)
    if status == 200 and data:
        with open(local_path, "wb") as f:
            f.write(data)
    # state.add_asset é síncrono agora
        state.add_asset(abs_url, local_path)
    return local_path
