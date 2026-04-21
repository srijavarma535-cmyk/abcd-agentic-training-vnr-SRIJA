from agents.base_agent import BaseAgent
from config.settings import Settings

class ProductAnalysisAgent(BaseAgent):
    name  = "ProductAgent"
    role  = "Product & Technology Evaluator"
    emoji = "🚀"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        self._emit(f"analysing product for '{startup}'…")
        prompt = f"""Startup: {startup}
Description: {context.get('description', '')}
Deck text: {context.get('deck_text', '')}

Return JSON with EXACTLY these keys:
{{
  "product_name": "<string>",
  "tagline": "<string>",
  "stage": "<idea|prototype|mvp|growth|scale>",
  "pmf_score": <1-10>,
  "innovation_score": <1-10>,
  "technical_moat_score": <1-10>,
  "scalability_score": <1-10>,
  "ux_score": <1-10>,
  "key_features": ["<f1>","<f2>","<f3>"],
  "tech_stack_inferred": ["<t1>","<t2>"],
  "defensibility": {{"ip":"<none|pending|granted>","network_effects":<true|false>,"data_moat":<true|false>}},
  "product_risks": ["<r1>","<r2>"],
  "overall_product_score": <1-10>,
  "ai_insight": "<2 sentence VC-grade product insight>",
  "summary": "<2 sentence summary>"
}}"""
        result = self._call_json(prompt)
        result["agent"] = "ProductAnalysisAgent"
        return result
