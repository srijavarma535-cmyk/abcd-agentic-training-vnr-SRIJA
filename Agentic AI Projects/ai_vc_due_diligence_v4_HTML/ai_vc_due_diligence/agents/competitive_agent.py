"""
Competitive Intelligence Agent
Maps the competitive landscape, identifies direct/indirect competitors, and moat strength.
"""
from agents.base_agent import BaseAgent


class CompetitiveIntelligenceAgent(BaseAgent):
    name = "CompetitiveIntel"
    role = "Competitive Intelligence Analyst"
    emoji = "🔍"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        description = context.get("description", "")
        web_data = context.get("web_data", "")

        self.log(f"Mapping competitive landscape for '{startup}'...")

        prompt = f"""Map the competitive landscape for this startup:

Startup: {startup}
Description: {description}
Web Data: {web_data}

Return a JSON object with this exact structure:
{{
  "agent": "CompetitiveIntelligenceAgent",
  "direct_competitors": [
    {{
      "name": "<string>",
      "stage": "<early|growth|public>",
      "estimated_funding_usd_millions": <number or null>,
      "threat_level": "<low|medium|high>"
    }}
  ],
  "indirect_competitors": [
    {{
      "name": "<string>",
      "overlap": "<string>"
    }}
  ],
  "market_concentration": "<fragmented|consolidated|duopoly|monopoly>",
  "differentiation_score": <1-10>,
  "competitive_moat_score": <1-10>,
  "incumbent_threat_score": <1-10>,
  "white_space_opportunities": ["<opportunity1>", "<opportunity2>"],
  "competitive_risks": ["<risk1>", "<risk2>"],
  "overall_competitive_score": <1-10>,
  "summary": "<2-3 sentence summary>"
}}"""

        result = self._call_llm_json(prompt)
        self.log(f"Competitive score: {result.get('overall_competitive_score', 'N/A')}/10")
        return result
