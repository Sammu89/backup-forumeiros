import os
import re
from urllib.parse import urlparse, urljoin, parse_qsl
from bs4 import BeautifulSoup
from assets import download_asset
from config import CONFIG_PATH, COOKIES_PATH  # To find OUTPUT_DIR use environment or default
from redirects import redirects



# Default output folder consistent with assets.py
OUTPUT_DIR = os.getenv("FORUMSMPT_BACKUP_DIR", os.path.join(os.getcwd(), "ForumSMPT"))

# Folder mapping based on URL first segment
PREFIX_MAP = {
    'f': 'categorias',
    't': 'topicos',
    'u': 'users',
    'g': 'grupos',
    'admin': 'admin',
    'privmsg': 'privmsg',
    'profile': 'profile'
}

def url_to_local_path(url: str) -> str:
    """
    Convert a full URL into a local HTML file path inside OUTPUT_DIR.
    """
    parsed = urlparse(url)
    path = parsed.path.lstrip('/')
    slug = path.replace('/', '_')
    
    if parsed.query:
        parts = parse_qsl(parsed.query)
        qp = '_'.join(f"{k}-{v}" for k, v in parts)
        slug = f"{slug}_{qp}"
    
    first_seg = path.split('/', 1)[0]
    folder = PREFIX_MAP.get(first_seg, 'misc')
    filename = f"{slug}.html"
    
    local_dir = os.path.join(OUTPUT_DIR, folder)
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, filename)

async def process_html(url: str, html: str, fetcher, state) -> str:
    """
    Rewrite HTML: download embed assets and rewrite links to local paths.
    Returns modified HTML.
    """
    soup = BeautifulSoup(html, 'html.parser')
    base_path = os.path.dirname(url_to_local_path(url))
    
    # Process images
    for img in soup.find_all('img', src=True):
        src = img['src']
        abs_url = src if src.startswith('http') else urljoin(url, src)
        local = await download_asset(abs_url, fetcher, state)
        if local:
            rel = os.path.relpath(local, base_path)
            img['src'] = rel
    
    # Process stylesheets
    for link in soup.find_all('link', href=True):
        if 'stylesheet' in (link.get('rel') or []):
            href = link['href']
            abs_url = href if href.startswith('http') else urljoin(url, href)
            local = await download_asset(abs_url, fetcher, state)
            if local:
                rel = os.path.relpath(local, base_path)
                link['href'] = rel
    
    # Process scripts
    for script in soup.find_all('script', src=True):
        src = script['src']
        abs_url = src if src.startswith('http') else urljoin(url, src)
        local = await download_asset(abs_url, fetcher, state)
        if local:
            rel = os.path.relpath(local, base_path)
            script['src'] = rel
    
    # Rewrite internal links
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
            continue
        
        abs_href = href if href.startswith('http') else urljoin(url, href)
        
        # 1) separa fragmento
        base, *frag = abs_href.split('#', 1)
        rel_path = urlparse(base).path + ("?"+urlparse(base).query if urlparse(base).query else "")
        # resolve via redirect map
        rel_path = redirects.resolve(rel_path)
        local_target = url_to_local_path(rel_path)
        parsed = urlparse(base)
        
        if parsed.netloc.endswith(BASE_DOMAIN):
            local_target = url_to_local_path(base)
            rel = os.path.relpath(local_target, base_path)
            # 2) reanexa o anchor se existir
            if frag:
                rel = f"{rel}#{frag[0]}"
            a['href'] = rel
    
    return str(soup)