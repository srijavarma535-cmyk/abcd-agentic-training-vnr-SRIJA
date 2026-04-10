"""
Product Analysis Agent
Evaluates product-market fit, technical moat, UX, and differentiation.
"""
from agents.base_agent import BaseAgent


class ProductAnalysisAgent(BaseAgent):
    name = "ProductAnalyst"
    role = "Product & Technology Evaluator"
    emoji = "🚀"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        description = context.get("description", "")
        web_data = context.get("web_data", "")
        deck_text = context.get("deck_text", "")

        self.log(f"Analyzing product for '{startup}'...")

        prompt = f"""Perform a detailed product and technology analysis for this startup:

Startup: {startup}
Description: {description}
Website/Pitch Deck Data: {web_data}
Deck Text: {deck_text}

Return a JSON object with this exact structure:
{{
  "agent": "ProductAnalysisAgent",
  "product_stage": "<idea|prototype|mvp|growth|scale>",
  "pmf_score": <1-10>,
  "technical_moat_score": <1-10>,
  "defensibility": {{
    "ip_protection": "<none|pending|granted>",
    "network_effects": <true|false>,
    "switching_costs": "<low|medium|high>",
    "data_moat": <true|false>
  }},
  "innovation_score": <1-10>,
  "ux_quality_score": <1-10>,
  "scalability_score": <1-10>,
  "key_features": ["<feature1>", "<feature2>", "<feature3>"],
  "product_risks": ["<risk1>", "<risk2>"],
  "overall_product_score": <1-10>,
  "summary": "<2-3 sentence summary>"
}}"""

        result = self._call_llm_json(prompt)
        self.log(f"Product score: {result.get('overall_product_score', 'N/A')}/10")
        return result
