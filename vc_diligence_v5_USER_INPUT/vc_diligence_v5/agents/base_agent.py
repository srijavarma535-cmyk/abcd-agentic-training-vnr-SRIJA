"""
BaseAgent — calls Ollama REST API.
Includes robust JSON repair for imperfect llama3.2 output.
"""
import json, re, time, urllib.request, urllib.error
from abc import ABC, abstractmethod
from typing import Optional, Callable
from config.settings import Settings


class BaseAgent(ABC):
    name:  str = "BaseAgent"
    role:  str = "Analyst"
    emoji: str = "🤖"

    def __init__(self, settings: Settings):
        self.settings = settings
        self._status_cb: Optional[Callable] = None

    def set_status_callback(self, cb: Callable):
        self._status_cb = cb

    def _emit(self, msg: str):
        print(f"  [{self.emoji} {self.name}] {msg}")
        if self._status_cb:
            self._status_cb(self.name, msg)

    @property
    def system_prompt(self) -> str:
        return (
            f"You are {self.name}, an elite {self.role} at a world-class venture capital firm. "
            "You MUST return ONLY a single valid JSON object. "
            "No markdown, no code fences, no explanation before or after. "
            "Start your response with {{ and end with }}. "
            "All string values must use double quotes. "
            "All scores are integers 1-10."
        )

    @abstractmethod
    async def analyze(self, context: dict) -> dict:
        pass

    def _call_ollama(self, user_prompt: str, system_override: Optional[str] = None) -> str:
        system = system_override or self.system_prompt
        url = f"{self.settings.ollama_host}/api/chat"
        payload = json.dumps({
            "model":  self.settings.ollama_model,
            "stream": False,
            "options": {
                "temperature": self.settings.temperature,
                "num_predict": self.settings.max_tokens,
            },
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user_prompt},
            ],
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=self.settings.request_timeout) as r:
            data = json.loads(r.read())
        self._emit(f"done in {round(time.time()-t0,1)}s")
        return data["message"]["content"]

    def _repair_json(self, raw: str) -> str:
        """Attempt to repair common JSON issues from llama3.2 output."""
        # 1. Strip markdown fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?", "", raw).strip()
            raw = re.sub(r"```$", "", raw).strip()

        # 2. Extract first complete JSON object
        start = raw.find("{")
        if start == -1:
            raise ValueError("No JSON object found in response")

        # Find matching closing brace
        depth = 0
        end = -1
        in_str = False
        escape = False
        for i, ch in enumerate(raw[start:], start):
            if escape:
                escape = False
                continue
            if ch == "\\" and in_str:
                escape = True
                continue
            if ch == '"' and not escape:
                in_str = not in_str
                continue
            if not in_str:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
        if end == -1:
            # Try to close unclosed braces
            raw_slice = raw[start:]
            opens = raw_slice.count("{")
            closes = raw_slice.count("}")
            raw_slice += "}" * (opens - closes)
            return raw_slice
        return raw[start:end+1]

    def _call_json(self, user_prompt: str, system_override: Optional[str] = None) -> dict:
        raw = self._call_ollama(user_prompt, system_override)
        try:
            repaired = self._repair_json(raw)
            return json.loads(repaired)
        except (json.JSONDecodeError, ValueError):
            # Last resort: use regex to extract key-value pairs
            result = {}
            # Extract simple string values
            for m in re.finditer(r'"(\w+)"\s*:\s*"([^"]*)"', raw):
                result[m.group(1)] = m.group(2)
            # Extract numeric values
            for m in re.finditer(r'"(\w+)"\s*:\s*(-?\d+(?:\.\d+)?)', raw):
                try:
                    result[m.group(1)] = float(m.group(2)) if '.' in m.group(2) else int(m.group(2))
                except ValueError:
                    pass
            # Extract boolean values
            for m in re.finditer(r'"(\w+)"\s*:\s*(true|false)', raw):
                result[m.group(1)] = m.group(2) == "true"
            if result:
                return result
            # Absolute fallback: return empty dict with error
            return {"_parse_error": raw[:200]}
