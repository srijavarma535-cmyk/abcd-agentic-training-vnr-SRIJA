"""
Settings — AI VC Due Diligence v5
Backend: Ollama (local, free, fast)
"""
import os
from dataclasses import dataclass, field

@dataclass
class Settings:
    # ── Ollama ──────────────────────────────────────────────
    ollama_host: str  = field(default_factory=lambda: os.getenv("OLLAMA_HOST","http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL","llama3.2"))

    # ── Pipeline ────────────────────────────────────────────
    request_timeout: int  = 120
    max_tokens: int       = 2048
    temperature: float    = 0.2       # low = more deterministic JSON

    # ── Scoring weights ─────────────────────────────────────
    scoring_weights: dict = field(default_factory=lambda: {
        "market":      0.20,
        "team":        0.25,
        "product":     0.20,
        "financials":  0.15,
        "competitive": 0.10,
        "risk":        0.10,
    })

    def validate(self):
        import urllib.request, urllib.error
        try:
            urllib.request.urlopen(f"{self.ollama_host}/api/tags", timeout=4)
        except Exception as e:
            raise RuntimeError(
                f"\n❌  Cannot reach Ollama at {self.ollama_host}\n"
                "👉  Install: https://ollama.com/download\n"
                f"👉  Then run:  ollama pull {self.ollama_model}\n"
                "👉  Then start: ollama serve"
            ) from e
        return self
