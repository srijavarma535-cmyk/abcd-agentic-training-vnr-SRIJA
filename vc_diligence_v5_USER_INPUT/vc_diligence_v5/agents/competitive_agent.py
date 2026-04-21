from agents.base_agent import BaseAgent
from config.settings import Settings

class CompetitiveAgent(BaseAgent):
    name  = "CompetitiveAgent"
    role  = "Competitive Intelligence Analyst"
    emoji = "🔍"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        self._emit(f"mapping competitive landscape for '{startup}'…")
        prompt = f"""Startup: {startup}
Description: {context.get('description', '')}

Return JSON with EXACTLY these keys:
{{
  "direct_competitors": [
    {{"name":"<string>","strength":"<string>","weakness":"<string>","stage":"<early|growth|public>","threat":"<low|medium|high>"}}
  ],
  "indirect_competitors": [{{"name":"<string>","overlap":"<string>"}}],
  "market_concentration": "<fragmented|consolidated|duopoly|monopoly>",
  "differentiation_score": <1-10>,
  "moat_score": <1-10>,
  "incumbent_threat_score": <1-10>,
  "positioning": {{"price_position":"<low|mid|premium>","feature_position":"<basic|mid|advanced>"}},
  "white_space": ["<opp1>","<opp2>"],
  "competitive_risks": ["<r1>","<r2>"],
  "overall_competitive_score": <1-10>,
  "ai_insight": "<2 sentence VC-grade competitive insight>",
  "summary": "<2 sentence summary>"
}}"""
        result = self._call_json(prompt)
        result["agent"] = "CompetitiveAgent"
        return result
