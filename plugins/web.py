"""Web plugin: fetch page text, quick search, and file download."""
import os
from urllib.parse import quote_plus

import httpx
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

from tools.registry import Tool, ToolRegistry

DOWNLOAD_DIR = "downloads"
SEARCH_ENDPOINT = "https://html.duckduckgo.com/html/"


async def fetch_url(url: str, max_chars: int = 5000):
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        r = await client.get(url, headers={"User-Agent": "HOMA/1.0"})
    tree = HTMLParser(r.text)
    for tag in tree.css("script, style, noscript"):
        tag.decompose()
    text = tree.body.text(separator=" ", strip=True) if tree.body else ""
    return {"status": r.status_code, "url": str(r.url), "text": text[:max_chars]}


async def search(query: str, limit: int = 6):
    """Lightweight search via DuckDuckGo's HTML endpoint (no API key)."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
        r = await client.get(SEARCH_ENDPOINT, params={"q": query},
                             headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.select("a.result__a")[:limit]:
        results.append({"title": a.get_text(strip=True), "url": a.get("href")})
    return {"query": query, "results": results}


async def download(url: str, filename: str = ""):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    name = filename or url.split("/")[-1].split("?")[0] or "download.bin"
    dest = os.path.join(DOWNLOAD_DIR, name)
    async with httpx.AsyncClient(follow_redirects=True, timeout=120) as client:
        r = await client.get(url)
        with open(dest, "wb") as f:
            f.write(r.content)
    return {"saved": os.path.abspath(dest), "bytes": len(r.content)}


def register(r: ToolRegistry) -> None:
    C = "web"
    r.register(Tool("web.fetch", "Fetch and extract text from a web page (news/prices).",
        {"type": "object", "properties": {"url": {"type": "string"},
         "max_chars": {"type": "integer", "default": 5000}}, "required": ["url"]}, fetch_url, category=C))
    r.register(Tool("web.search", "Search the web and return top result titles + links.",
        {"type": "object", "properties": {"query": {"type": "string"},
         "limit": {"type": "integer", "default": 6}}, "required": ["query"]}, search, category=C))
    r.register(Tool("web.download", "Download a file from a URL into the downloads folder.",
        {"type": "object", "properties": {"url": {"type": "string"}, "filename": {"type": "string"}},
         "required": ["url"]}, download, category=C))
