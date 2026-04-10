"""
Market Analysis Agent
Analyzes TAM/SAM/SOM, market trends, growth rate, and timing.
"""
from agents.base_agent import BaseAgent


class MarketAnalysisAgent(BaseAgent):
    name = "MarketAnalyst"
    role = "Market Research Specialist"
    emoji = "📊"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        description = context.get("description", "")
        web_data = context.get("web_data", "")

        self.log(f"Analyzing market for '{startup}'...")

        prompt = f"""Perform a deep market analysis for the following startup:

Startup: {startup}
Description: {description}
Additional Context: {web_data}

Return a JSON object with this exact structure:
{{
  "agent": "MarketAnalysisAgent",
  "tam": {{
    "value_usd_billions": <number>,
    "source_rationale": "<string>"
  }},
  "sam": {{
    "value_usd_billions": <number>,
    "rationale": "<string>"
  }},
  "som": {{
    "value_usd_billions": <number>,
    "rationale": "<string>"
  }},
  "market_growth_rate_pct": <number>,
  "market_timing": {{
    "score": <1-10>,
    "rationale": "<string>"
  }},
  "key_trends": ["<trend1>", "<trend2>", "<trend3>"],
  "market_risks": ["<risk1>", "<risk2>"],
  "overall_market_score": <1-10>,
  "summary": "<2-3 sentence summary>"
}}"""

        result = self._call_llm_json(prompt)
        self.log(f"Market score: {result.get('overall_market_score', 'N/A')}/10")
        return result
