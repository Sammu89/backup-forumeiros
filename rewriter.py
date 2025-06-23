import os
import hashlib
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import mimetypes

from redirects import redirects
from state import State
from fetch import Fetcher
import settings


def url_to_local_path(path: str) -> str:
    """
    Convert a relative URL path (with optional ?query) into a local file path.
    Root path "/" becomes "index.html" at backup root.
    E.g. "/t1234-topic" → "backup/topicos/t1234-topic.html"
    """
    if not path or path == "/":
        return os.path.join(settings.BACKUP_ROOT, "index.html")
    
    parsed = urlparse(path)
    route = parsed.path.lstrip("/")
    prefix = route.split("/", 1)[0].lower() if route else ""

    if prefix.startswith("f"):
        folder = "categorias"
    elif prefix.startswith("t"):
        folder = "topicos"
    elif prefix.startswith("u"):
        folder = "users"
    elif prefix.startswith("g"):
        folder = "grupos"
    elif prefix.startswith("privmsg"):
        folder = "privmsg"
    elif prefix.startswith("profile"):
        folder = "profile"
    else:
        folder = "misc"

    slug = route.replace("/", "_") if route else "index"
    if parsed.query:
        slug += "_" + parsed.query.replace("=", "-").replace("&", "_")
    filename = f"{slug}.html"

    local_dir = os.path.join(settings.BACKUP_ROOT, folder)
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, filename)


async def download_external_asset(url: str, fetcher: Fetcher, asset_type: str = "misc") -> str:
    """
    Download an external asset and return the local relative path.
    asset_type: 'css', 'js', 'fonts', 'images', 'misc'
    """
    # Create hash-based filename to avoid conflicts
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    parsed = urlparse(url)
    
    # Try to get original extension
    _, ext = os.path.splitext(parsed.path)
    if not ext:
        # Guess extension based on asset type
        if asset_type == "css":
            ext = ".css"
        elif asset_type == "js":
            ext = ".js"
        elif asset_type == "fonts":
            # Common font extensions
            ext = ".woff2"  # default, will be corrected by content-type if possible
        elif asset_type == "images":
            ext = ".jpg"  # default
        else:
            ext = ".bin"
    
    filename = f"{url_hash}{ext}"
    local_dir = os.path.join(settings.BACKUP_ROOT, "external_files", asset_type)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    
    # Check if already downloaded
    if os.path.exists(local_path):
        return os.path.relpath(local_path, os.path.dirname(url_to_local_path("/")))
    
    # Download the asset
    status, data = await fetcher.fetch_bytes(url)
    if status == 200 and data:
        try:
            with open(local_path, "wb") as f:
                f.write(data)
            print(f"[Rewriter] Downloaded external {asset_type}: {url} -> {local_path}")
        except Exception as e:
            print(f"[Rewriter] Failed to save {url}: {e}")
            return url  # Return original URL on failure
    else:
        print(f"[Rewriter] Failed to download {url} (status: {status})")
        return url  # Return original URL on failure
    
    return os.path.relpath(local_path, os.path.dirname(url_to_local_path("/")))


async def download_internal_asset(url: str, fetcher: Fetcher, asset_type: str = "misc") -> str:
    """
    Download an internal asset and return the local relative path.
    """
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path) or "asset"
    
    # Ensure filename has extension
    if "." not in filename:
        if asset_type == "images":
            filename += ".jpg"
        elif asset_type == "css":
            filename += ".css"
        elif asset_type == "js":
            filename += ".js"
        else:
            filename += ".bin"
    
    local_dir = os.path.join(settings.BACKUP_ROOT, "assets", asset_type)
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    
    # Check if already downloaded
    if os.path.exists(local_path):
        return os.path.relpath(local_path, os.path.dirname(url_to_local_path("/")))
    
    # Download the asset
    status, data = await fetcher.fetch_bytes(url)
    if status == 200 and data:
        try:
            with open(local_path, "wb") as f:
                f.write(data)
            print(f"[Rewriter] Downloaded internal {asset_type}: {url} -> {local_path}")
        except Exception as e:
            print(f"[Rewriter] Failed to save {url}: {e}")
            return url  # Return original URL on failure
    else:
        print(f"[Rewriter] Failed to download {url} (status: {status})")
        return url  # Return original URL on failure
    
    return os.path.relpath(local_path, os.path.dirname(url_to_local_path("/")))


async def process_css_for_fonts(css_content: str, css_url: str, fetcher: Fetcher) -> str:
    """
    Process CSS content to download any external fonts and rewrite URLs.
    """
    import re
    
    # Find all url() references in CSS
    url_pattern = r'url\s*\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)'
    urls = re.findall(url_pattern, css_content)
    
    for url in urls:
        # Skip data: URLs
        if url.startswith('data:'):
            continue
            
        # Make absolute URL
        abs_url = url if url.startswith('http') else urljoin(css_url, url)
        parsed = urlparse(abs_url)
        
        # Check if it's a font or external resource
        _, ext = os.path.splitext(parsed.path)
        ext = ext.lower()
        
        if ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot'] or 'font' in url.lower():
            # Download font
            local_path = await download_external_asset(abs_url, fetcher, "fonts")
            # Replace in CSS
            css_content = css_content.replace(f'url({url})', f'url({local_path})')
            css_content = css_content.replace(f'url("{url}")', f'url("{local_path}")')
            css_content = css_content.replace(f"url('{url}')", f"url('{local_path}')")
    
    return css_content


async def process_html(
    page_url: str, html: str, fetcher: Fetcher, state: State
) -> str:
    """
    Rewrite an HTML page:
    - Download ALL external resources in <head> (CSS, JS, fonts, etc.)
    - Download and rewrite internal assets (images, CSS, JS)
    - Download only internal images in <body> (not external links)
    - Rewrite <a href> to local paths, resolving redirects
    Returns rewritten HTML as string.
    """
    soup = BeautifulSoup(html, "html.parser")
    current_page_path = url_to_local_path(page_url)
    base_path = os.path.dirname(current_page_path)

    # -- HEAD SECTION: Download ALL external resources --
    head = soup.find('head')
    if head:
        print(f"[Rewriter] Processing <head> resources for {page_url}")
        
        # Process <link> tags (stylesheets, fonts, preloads, etc.)
        for link in head.find_all("link", href=True):
            href = link["href"]
            abs_href = href if href.startswith("http") else urljoin(settings.BASE_URL, href)
            parsed = urlparse(abs_href)
            
            # Determine if it's internal or external
            is_internal = parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc
            
            rel_attr = link.get("rel", [])
            if isinstance(rel_attr, str):
                rel_attr = [rel_attr]
            
            # Handle different link types
            if "stylesheet" in rel_attr:
                if is_internal:
                    local_path = await download_internal_asset(abs_href, fetcher, "css")
                    link["href"] = local_path
                    
                    # Also process the CSS file for fonts
                    status, css_content = await fetcher.fetch_text(abs_href)
                    if status == 200 and css_content:
                        processed_css = await process_css_for_fonts(css_content, abs_href, fetcher)
                        # Save processed CSS (ensure parent dirs exist)
                        full_local_path = os.path.join(settings.BACKUP_ROOT, local_path)
                        os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
                        try:
                            with open(full_local_path, "w", encoding="utf-8") as f:
                                f.write(processed_css)
                        except Exception as e:
                            print(f"[Rewriter] Failed to save processed CSS: {e}")
                else:
                    # External stylesheet - download and process
                    local_path = await download_external_asset(abs_href, fetcher, "css")
                    link["href"] = local_path
                    
                    # Process CSS for fonts
                    status, css_content = await fetcher.fetch_text(abs_href)
                    if status == 200 and css_content:
                        processed_css = await process_css_for_fonts(css_content, abs_href, fetcher)
                        # Save processed CSS (ensure parent dirs exist)
                        full_local_path = os.path.join(settings.BACKUP_ROOT, local_path)
                        os.makedirs(os.path.dirname(full_local_path), exist_ok=True)
                        try:
                            with open(full_local_path, "w", encoding="utf-8") as f:
                                f.write(processed_css)
                        except Exception as e:
                            print(f"[Rewriter] Failed to save processed CSS: {e}")
            
            elif any(r in rel_attr for r in ["preload", "prefetch", "dns-prefetch", "preconnect"]):
                # Handle preload/prefetch resources
                as_attr = link.get("as", "")
                if as_attr in ["font", "style", "script"]:
                    if is_internal:
                        asset_type = "fonts" if as_attr == "font" else ("css" if as_attr == "style" else "js")
                        local_path = await download_internal_asset(abs_href, fetcher, asset_type)
                        link["href"] = local_path
                    else:
                        asset_type = "fonts" if as_attr == "font" else ("css" if as_attr == "style" else "js")
                        local_path = await download_external_asset(abs_href, fetcher, asset_type)
                        link["href"] = local_path
            
            elif "icon" in rel_attr or "shortcut icon" in rel_attr:
                # Handle favicons
                if is_internal:
                    local_path = await download_internal_asset(abs_href, fetcher, "images")
                    link["href"] = local_path
                else:
                    local_path = await download_external_asset(abs_href, fetcher, "images")
                    link["href"] = local_path
        
        # Process <script> tags in head
        for script in head.find_all("script", src=True):
            src = script["src"]
            abs_src = src if src.startswith("http") else urljoin(settings.BASE_URL, src)
            parsed = urlparse(abs_src)
            
            is_internal = parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc
            
            if is_internal:
                local_path = await download_internal_asset(abs_src, fetcher, "js")
                script["src"] = local_path
            else:
                # External script - download it
                local_path = await download_external_asset(abs_src, fetcher, "js")
                script["src"] = local_path
        
        # Process <style> tags for embedded CSS (check for external fonts)
        for style in head.find_all("style"):
            if style.string:
                processed_css = await process_css_for_fonts(style.string, page_url, fetcher)
                style.string = processed_css

    # -- BODY SECTION: Only internal assets --
    
    # Process images
    for img in soup.find_all("img", src=True):
        src = img["src"]
        abs_src = src if src.startswith("http") else urljoin(settings.BASE_URL, src)
        parsed = urlparse(abs_src)
        
        # Only download internal images OR external images that are embedded/hotlinked
        if parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc:
            local_path = await download_internal_asset(abs_src, fetcher, "images")
            img["src"] = local_path
        # For external images in body, we keep them as-is (hotlinked)
        # unless they're embedded in a way that suggests they're part of the content
        elif img.get('class') or img.get('id') or img.parent.name in ['figure', 'picture']:
            # These seem like content images, download them
            local_path = await download_external_asset(abs_src, fetcher, "images")
            img["src"] = local_path

    # Process stylesheets in body (unusual but possible)
    for link in soup.find_all("link", href=True, rel=["stylesheet"]):
        if link.find_parent('head'):
            continue  # Already processed in head section
            
        href = link["href"]
        abs_href = href if href.startswith("http") else urljoin(settings.BASE_URL, href)
        parsed = urlparse(abs_href)
        
        if parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc:
            local_path = await download_internal_asset(abs_href, fetcher, "css")
            link["href"] = local_path

    # Process scripts in body
    for script in soup.find_all("script", src=True):
        if script.find_parent('head'):
            continue  # Already processed in head section
            
        src = script["src"]
        abs_src = src if src.startswith("http") else urljoin(settings.BASE_URL, src)
        parsed = urlparse(abs_src)
        
        if parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc:
            local_path = await download_internal_asset(abs_src, fetcher, "js")
            script["src"] = local_path

    # -- LINKS (<a>) --
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue

        abs_href = href if href.startswith("http") else urljoin(settings.BASE_URL, href)
        base, *frag = abs_href.split("#", 1)
        
        # Only rewrite internal links
        parsed = urlparse(base)
        if parsed.netloc == settings.BASE_DOMAIN or not parsed.netloc:
            rel_path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
            # Resolve redirects
            rel_path = redirects.resolve(rel_path)
            # Map to local file
            local_target = url_to_local_path(rel_path)
            rel = os.path.relpath(local_target, base_path)
            if frag:
                rel += "#" + frag[0]
            a["href"] = rel
        # External links are left as-is

    return str(soup)