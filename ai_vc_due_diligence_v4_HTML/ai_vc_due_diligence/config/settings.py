"""
Configuration & Settings — powered by Google Gemini (FREE tier)
Free tier: 1500 requests/day, no credit card needed
Get your free key at: https://aistudio.google.com/app/apikey
"""
import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    # Google Gemini (FREE - no credit card needed)
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))

    # Primary model — system auto-falls back if this one hits quota
    # Options tried in order: gemini-1.5-flash-latest → gemini-1.5-flash-8b
    #                       → gemini-1.5-pro-latest → gemini-2.0-flash-lite
    model: str = "gemini-1.5-flash-latest"
    max_tokens: int = 4096

    # Serper optional web search (free tier: 2500/month at serper.dev)
    serper_api_key: str = field(default_factory=lambda: os.getenv("SERPER_API_KEY", ""))

    # Pipeline
    max_concurrent_agents: int = 3   # lowered to 3 to reduce rate limit hits
    timeout_seconds: int = 120
    enable_web_search: bool = True
    enable_pdf_parsing: bool = True

    # Scoring weights
    scoring_weights: dict = field(default_factory=lambda: {
        "market": 0.20,
        "team": 0.25,
        "product": 0.20,
        "financials": 0.15,
        "competition": 0.10,
        "risk": 0.10,
    })

    def validate(self):
        if not self.gemini_api_key:
            raise ValueError(
                "\n❌ GEMINI_API_KEY not set!\n"
                "👉 Get your FREE key: https://aistudio.google.com/app/apikey\n"
                "👉 Windows CMD:  set GEMINI_API_KEY=your_key_here\n"
                "👉 Or add it to .env file:  GEMINI_API_KEY=your_key_here"
            )
        return self
