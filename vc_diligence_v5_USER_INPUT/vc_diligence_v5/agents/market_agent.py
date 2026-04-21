from agents.base_agent import BaseAgent
from config.settings import Settings

class MarketAnalysisAgent(BaseAgent):
    name  = "MarketAgent"
    role  = "Market Research Specialist"
    emoji = "📊"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        self._emit(f"analysing market for '{startup}'…")
        prompt = f"""Startup: {startup}
Description: {context.get('description', '')}
Extra context: {context.get('web_data', '')}

Return JSON with EXACTLY these keys:
{{
  "tam_usd_billions": <number>,
  "sam_usd_billions": <number>,
  "som_usd_billions": <number>,
  "cagr_pct": <number>,
  "market_stage": "<emerging|growing|mature|declining>",
  "timing_score": <1-10>,
  "geography": "<string>",
  "key_trends": ["<trend1>","<trend2>","<trend3>"],
  "market_risks": ["<risk1>","<risk2>"],
  "regulation_risk": "<low|medium|high>",
  "overall_market_score": <1-10>,
  "ai_insight": "<2 sentence VC-grade market insight>",
  "summary": "<2 sentence summary>"
}}"""
        result = self._call_json(prompt)
        result["agent"] = "MarketAnalysisAgent"
        return result
