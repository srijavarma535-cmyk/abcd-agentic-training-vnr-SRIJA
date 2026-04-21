from agents.base_agent import BaseAgent
from config.settings import Settings

class RiskAgent(BaseAgent):
    name  = "RiskAgent"
    role  = "Risk & Compliance Specialist"
    emoji = "⚠️"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        self._emit(f"assessing risks for '{startup}'…")
        prior = {k: v.get("summary", "") for k, v in context.get("prior_results", {}).items()}
        prompt = f"""Startup: {startup}
Description: {context.get('description', '')}
Prior agent summaries: {prior}

Return JSON with EXACTLY these keys:
{{
  "regulatory_risks": [{{"risk":"<string>","severity":"<low|medium|high|critical>","mitigation":"<string>"}}],
  "technology_risks": [{{"risk":"<string>","severity":"<low|medium|high>"}}],
  "market_risks": [{{"risk":"<string>","severity":"<low|medium|high>"}}],
  "operational_risks": [{{"risk":"<string>","severity":"<low|medium|high>"}}],
  "macro_risks": ["<r1>","<r2>"],
  "esg_concerns": ["<c1>"],
  "deal_breakers": [],
  "risk_adjusted_return": "<low|medium|high|exceptional>",
  "overall_risk_score": <1-10>,
  "ai_insight": "<2 sentence VC-grade risk insight>",
  "summary": "<2 sentence summary>"
}}"""
        result = self._call_json(prompt)
        result["agent"] = "RiskAgent"
        return result
