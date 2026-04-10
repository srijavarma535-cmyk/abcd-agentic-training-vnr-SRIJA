import os
import httpx
from langchain_core.tools import tool

SERPER_KEY = os.getenv("SERPER_API_KEY", "")

@tool
def web_search(query: str) -> list:
    """Search the web using Serper. Returns list of title/snippet/link dicts."""
    if not SERPER_KEY:
        return [{"title": "No API key", "snippet": "SERPER_API_KEY not set in .env", "link": ""}]
    try:
        resp = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": 8},
            timeout=15,
        )
        resp.raise_for_status()
        return [{"title": r.get("title",""), "snippet": r.get("snippet",""), "link": r.get("link","")}
                for r in resp.json().get("organic", [])]
    except Exception as e:
        return [{"title": "Search error", "snippet": str(e), "link": ""}]
