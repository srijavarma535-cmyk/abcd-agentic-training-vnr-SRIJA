"""
Financial Analysis Agent
Evaluates revenue model, unit economics, burn rate, and fundraising history.
"""
from agents.base_agent import BaseAgent


class FinancialAnalysisAgent(BaseAgent):
    name = "FinancialAnalyst"
    role = "Financial Due Diligence Specialist"
    emoji = "💰"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        description = context.get("description", "")
        financial_data = context.get("financial_data", "")
        deck_text = context.get("deck_text", "")

        self.log(f"Analyzing financials for '{startup}'...")

        prompt = f"""Perform financial due diligence on this startup:

Startup: {startup}
Description: {description}
Financial Data: {financial_data}
Deck/Docs: {deck_text}

Return a JSON object with this exact structure:
{{
  "agent": "FinancialAnalysisAgent",
  "revenue_model": "<SaaS|marketplace|transactional|freemium|advertising|other>",
  "current_arr_estimate_usd": <number or null>,
  "growth_rate_estimate_pct": <number or null>,
  "unit_economics": {{
    "ltv_cac_ratio": <number or null>,
    "payback_months": <number or null>,
    "gross_margin_pct": <number or null>
  }},
  "burn_rate_assessment": "<low|medium|high|unknown>",
  "runway_months_estimate": <number or null>,
  "fundraising_history": [
    {{
      "round": "<Pre-seed|Seed|Series A/B/C>",
      "amount_usd": <number or null>,
      "year": <number or null>
    }}
  ],
  "valuation_reasonableness_score": <1-10>,
  "financial_health_score": <1-10>,
  "red_flags": ["<flag1>"],
  "overall_financial_score": <1-10>,
  "summary": "<2-3 sentence summary>"
}}"""

        result = self._call_llm_json(prompt)
        self.log(f"Financial score: {result.get('overall_financial_score', 'N/A')}/10")
        return result
