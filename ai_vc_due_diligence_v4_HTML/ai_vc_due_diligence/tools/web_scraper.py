"""
Web Scraper Tool
Fetches and extracts content from startup websites.
"""
import asyncio
from typing import Optional
from config.settings import Settings

try:
    import httpx
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


class WebScraper:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def scrape(self, url: str) -> str:
        """Fetch and extract text from a URL."""
        if not HAS_DEPS:
            return f"[WebScraper] httpx/bs4 not installed. Install with: pip install httpx beautifulsoup4"

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                # Remove scripts and styles
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                text = soup.get_text(separator=" ", strip=True)
                return text[:5000]
        except Exception as e:
            return f"[WebScraper] Could not fetch {url}: {e}"

    async def search_web(self, query: str) -> str:
        """Search the web using Serper API."""
        if not self.settings.serper_api_key:
            return f"[WebSearch] No SERPER_API_KEY set. Query was: {query}"

        if not HAS_DEPS:
            return "[WebSearch] httpx not installed."

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={"X-API-KEY": self.settings.serper_api_key, "Content-Type": "application/json"},
                    json={"q": query, "num": 5},
                )
                data = response.json()
                results = data.get("organic", [])
                snippets = [f"• {r.get('title')}: {r.get('snippet')}" for r in results[:5]]
                return "\n".join(snippets)
        except Exception as e:
            return f"[WebSearch] Error: {e}"
