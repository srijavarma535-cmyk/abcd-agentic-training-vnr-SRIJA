from agents.base_agent import BaseAgent
from config.settings import Settings

class TeamAnalysisAgent(BaseAgent):
    name  = "TeamAgent"
    role  = "Talent & Leadership Evaluator"
    emoji = "👥"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        self._emit(f"evaluating team for '{startup}'…")
        prompt = f"""Startup: {startup}
Description: {context.get('description', '')}
Team info: {context.get('team_info', '')}

Return JSON with EXACTLY these keys:
{{
  "founders": [
    {{"name":"<inferred or Unknown>","role":"<CEO/CTO/etc>","background":"<1 line>","prior_exits":<number or 0>}}
  ],
  "team_size_estimate": "<1-10|11-50|51-200|200+>",
  "execution_score": <1-10>,
  "domain_expertise_score": <1-10>,
  "founder_market_fit_score": <1-10>,
  "team_completeness_score": <1-10>,
  "key_strengths": ["<s1>","<s2>"],
  "key_gaps": ["<g1>","<g2>"],
  "hiring_assessment": "<string>",
  "risk_level": "<low|medium|high>",
  "overall_team_score": <1-10>,
  "ai_insight": "<2 sentence VC-grade team insight>",
  "summary": "<2 sentence summary>"
}}"""
        result = self._call_json(prompt)
        result["agent"] = "TeamAnalysisAgent"
        return result
