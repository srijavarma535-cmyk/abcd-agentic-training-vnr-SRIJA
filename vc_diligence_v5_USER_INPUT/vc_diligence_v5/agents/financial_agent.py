from agents.base_agent import BaseAgent
from config.settings import Settings

class FinancialAnalysisAgent(BaseAgent):
    name  = "FinancialAgent"
    role  = "Financial Due Diligence Specialist"
    emoji = "💰"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        self._emit(f"analysing financials for '{startup}'…")
        prompt = f"""Startup: {startup}
Description: {context.get('description', '')}
Financial data: {context.get('financial_data', '')}

Return JSON with EXACTLY these keys:
{{
  "revenue_model": "<SaaS|marketplace|transactional|freemium|advertising|other>",
  "arr_usd_estimate": <number or null>,
  "mrr_usd_estimate": <number or null>,
  "growth_rate_pct": <number or null>,
  "burn_rate_monthly_usd": <number or null>,
  "runway_months": <number or null>,
  "gross_margin_pct": <number or null>,
  "ltv_cac_ratio": <number or null>,
  "payback_months": <number or null>,
  "funding_rounds": [{{"round":"<string>","amount_usd":<number or null>,"year":<number or null>}}],
  "burn_risk": "<low|medium|high|critical>",
  "valuation_score": <1-10>,
  "overall_financial_score": <1-10>,
  "red_flags": ["<f1>"],
  "ai_insight": "<2 sentence VC-grade financial insight>",
  "summary": "<2 sentence summary>"
}}"""
        result = self._call_json(prompt)
        result["agent"] = "FinancialAnalysisAgent"
        return result
