import os
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from redirects import redirects
from state import State
from fetch import Fetcher


def url_to_local_path(path: str) -> str:
    """
    Convert a relative URL path (with optional ?query) into a local file path.
    E.g. "/t1234-topic" → "backup/topicos/t1234-topic.html"
    """
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

    local_dir = os.path.join("backup", folder)
    os.makedirs(local_dir, exist_ok=True)
    return os.path.join(local_dir, filename)


async def process_html(
    page_url: str, html: str, fetcher: Fetcher, state: State
) -> str:
    """
    Rewrite an HTML page:
    - Download and rewrite <img> tags
    - Download and rewrite <link rel="stylesheet"> tags
    - Download and rewrite <script src=...> tags
    - Rewrite <a href> to local paths, resolving redirects
    Returns rewritten HTML as string.
    """
    soup = BeautifulSoup(html, "html.parser")
    base_path = os.path.dirname(url_to_local_path(page_url))

    # -- IMAGES --
    for img in soup.find_all("img", src=True):
        src = img["src"]
        abs_src = src if src.startswith("http") else urljoin(page_url, src)
        # only internal or embedded images
        parsed = urlparse(abs_src)
        if parsed.netloc.endswith(BASE_DOMAIN):
            # download via fetcher
            status, data = await fetcher.fetch_bytes(abs_src)
            if status == 200 and data:
                # save to assets/images
                fname = os.path.basename(parsed.path)
                local = os.path.join("backup", "assets", "imagens", fname)
                os.makedirs(os.path.dirname(local), exist_ok=True)
                if not os.path.exists(local):
                    with open(local, "wb") as f:
                        f.write(data)
                # rewrite src to relative
                rel = os.path.relpath(local, base_path)
                img["src"] = rel

    # -- STYLESHEETS --
    for link in soup.find_all("link", href=True, rel=["stylesheet"]):
        href = link["href"]
        abs_href = href if href.startswith("http") else urljoin(page_url, href)
        parsed = urlparse(abs_href)
        if parsed.netloc.endswith(BASE_DOMAIN):
            status, data = await fetcher.fetch_bytes(abs_href)
            if status == 200 and data:
                fname = os.path.basename(parsed.path)
                local = os.path.join("backup", "assets", "css", fname)
                os.makedirs(os.path.dirname(local), exist_ok=True)
                if not os.path.exists(local):
                    with open(local, "wb") as f:
                        f.write(data)
                rel = os.path.relpath(local, base_path)
                link["href"] = rel

    # -- SCRIPTS --
    for script in soup.find_all("script", src=True):
        src = script["src"]
        abs_src = src if src.startswith("http") else urljoin(page_url, src)
        parsed = urlparse(abs_src)
        if parsed.netloc.endswith(BASE_DOMAIN):
            status, data = await fetcher.fetch_bytes(abs_src)
            if status == 200 and data:
                fname = os.path.basename(parsed.path)
                local = os.path.join("backup", "assets", "js", fname)
                os.makedirs(os.path.dirname(local), exist_ok=True)
                if not os.path.exists(local):
                    with open(local, "wb") as f:
                        f.write(data)
                rel = os.path.relpath(local, base_path)
                script["src"] = rel

    # -- LINKS (<a>) --
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue

        abs_href = href if href.startswith("http") else urljoin(page_url, href)
        base, *frag = abs_href.split("#", 1)
        # construct rel_path
        parsed = urlparse(base)
        rel_path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        # resolve redirects
        rel_path = redirects.resolve(rel_path)
        # map to local file
        local_target = url_to_local_path(rel_path)
        rel = os.path.relpath(local_target, base_path)
        if frag:
            rel += "#" + frag[0]
        a["href"] = rel

    return str(soup)
