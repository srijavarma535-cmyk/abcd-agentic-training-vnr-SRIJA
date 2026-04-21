import asyncio, urllib.request
from typing import Optional

try:
    import httpx
    from bs4 import BeautifulSoup
    _HAS_DEPS = True
except ImportError:
    _HAS_DEPS = False

class WebScraper:
    async def scrape(self, url: str) -> str:
        if not _HAS_DEPS:
            return "[WebScraper] install httpx beautifulsoup4"
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=True) as c:
                r = await c.get(url, headers={"User-Agent":"Mozilla/5.0"})
                soup = __import__("bs4").BeautifulSoup(r.text,"html.parser")
                for t in soup(["script","style","nav","footer"]): t.decompose()
                return soup.get_text(" ", strip=True)
        except Exception as e:
            return f"[WebScraper error] {e}"
