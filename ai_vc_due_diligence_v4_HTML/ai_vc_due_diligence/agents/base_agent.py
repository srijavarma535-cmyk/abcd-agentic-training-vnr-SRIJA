"""
Base Agent — all specialist agents inherit from this.
Uses Google Gemini API (100% FREE tier)
Auto-retries on 429 rate limits with backoff.
"""
import json
import time
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Optional
from config.settings import Settings


class BaseAgent(ABC):
    name: str = "BaseAgent"
    role: str = "Analyst"
    emoji: str = "🤖"

    # Models to try in order — first one that works is used
    FALLBACK_MODELS = [
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro-latest",
        "gemini-2.0-flash-lite",
    ]

    def __init__(self, settings: Settings):
        self.settings = settings
        self._results: dict = {}
        self._working_model: Optional[str] = None  # cached once found

    @property
    def system_prompt(self) -> str:
        return (
            f"You are {self.name}, a specialist {self.role} at a top-tier venture capital firm. "
            "You are part of a multi-agent due diligence team performing rigorous analysis on startup investment opportunities. "
            "Always respond with structured, evidence-backed analysis. "
            "Be direct, concise, and use a scoring system (1-10) for key dimensions. "
            "Output ONLY valid JSON when asked for structured output. No markdown fences, no extra text."
        )

    @abstractmethod
    async def analyze(self, context: dict) -> dict:
        pass

    def _make_request(self, model: str, full_prompt: str) -> str:
        """Make a single request to Gemini with a specific model."""
        api_key = self.settings.gemini_api_key
        # Try v1 first, then v1beta
        for api_ver in ["v1", "v1beta"]:
            url = (
                f"https://generativelanguage.googleapis.com/{api_ver}/models/"
                f"{model}:generateContent?key={api_key}"
            )
            payload = json.dumps({
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": self.settings.max_tokens,
                    "temperature": 0.3,
                }
            }).encode("utf-8")

            req = urllib.request.Request(
                url, data=payload,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["candidates"][0]["content"]["parts"][0]["text"]
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8")
                if e.code == 404:
                    break  # model not found on this api_ver, try next ver
                elif e.code == 429:
                    # Extract retry delay from error body if present
                    try:
                        err_data = json.loads(body)
                        details = err_data.get("error", {}).get("details", [])
                        retry_delay = 15
                        for d in details:
                            if d.get("@type", "").endswith("RetryInfo"):
                                delay_str = d.get("retryDelay", "15s")
                                retry_delay = int(delay_str.replace("s", "")) + 2
                        raise RateLimitError(retry_delay, body)
                    except RateLimitError:
                        raise
                    except Exception:
                        raise RateLimitError(15, body)
                else:
                    raise RuntimeError(f"Gemini API error {e.code}: {body}")
        raise ModelNotFoundError(model)

    def _call_llm(self, user_prompt: str, system_override: Optional[str] = None) -> str:
        """Call Gemini, trying multiple models with retry on rate limit."""
        system = system_override or self.system_prompt
        full_prompt = f"{system}\n\n{user_prompt}"

        # If we already found a working model, use it directly
        models_to_try = (
            [self._working_model] + self.FALLBACK_MODELS
            if self._working_model
            else self.FALLBACK_MODELS
        )
        # Deduplicate while preserving order
        seen = set()
        models_to_try = [m for m in models_to_try if not (m in seen or seen.add(m))]

        last_error = None
        for model in models_to_try:
            try:
                # Retry up to 3 times for rate limits on same model
                for attempt in range(3):
                    try:
                        result = self._make_request(model, full_prompt)
                        self._working_model = model  # cache working model
                        if model != self.settings.model:
                            print(f"    ℹ️  Using model: {model}")
                        return result
                    except RateLimitError as e:
                        if attempt < 2:
                            print(f"    ⏳ Rate limit hit on {model}, waiting {e.delay}s...")
                            time.sleep(e.delay)
                        else:
                            raise
            except ModelNotFoundError:
                continue  # try next model
            except RateLimitError as e:
                print(f"    ⚠️  Rate limit exhausted on {model}, trying next model...")
                last_error = e
                time.sleep(5)
                continue
            except RuntimeError as e:
                last_error = e
                continue

        raise RuntimeError(
            f"All Gemini models failed.\nLast error: {last_error}\n\n"
            "💡 Tips:\n"
            "  1. Wait 1 minute and try again (rate limit resets)\n"
            "  2. Use --mode quick instead of --mode full (fewer API calls)\n"
            "  3. Check https://ai.google.dev/gemini-api/docs/rate-limits"
        )

    def _call_llm_json(self, user_prompt: str, system_override: Optional[str] = None) -> dict:
        """LLM call that returns parsed JSON."""
        raw = self._call_llm(user_prompt, system_override).strip()
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    def score(self, value: float, label: str) -> dict:
        return {"score": round(value, 1), "label": label, "max": 10}

    def log(self, msg: str):
        print(f"  [{self.emoji} {self.name}] {msg}")


class RateLimitError(Exception):
    def __init__(self, delay: int, body: str = ""):
        self.delay = delay
        self.body = body
        super().__init__(f"Rate limited — retry after {delay}s")


class ModelNotFoundError(Exception):
    def __init__(self, model: str):
        self.model = model
        super().__init__(f"Model not found: {model}")
