"""
Risk Assessment Agent
Identifies regulatory, operational, technology, and macro risks.
"""
from agents.base_agent import BaseAgent


class RiskAssessmentAgent(BaseAgent):
    name = "RiskAnalyst"
    role = "Risk & Compliance Specialist"
    emoji = "⚠️"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        description = context.get("description", "")
        all_agent_results = context.get("prior_results", {})

        self.log(f"Assessing risks for '{startup}'...")

        prior_summary = ""
        for k, v in all_agent_results.items():
            summary = v.get("summary", "")
            if summary:
                prior_summary += f"\n{k}: {summary}"

        prompt = f"""Perform comprehensive risk assessment for this startup investment:

Startup: {startup}
Description: {description}
Prior Analysis Summaries: {prior_summary}

Return a JSON object with this exact structure:
{{
  "agent": "RiskAssessmentAgent",
  "regulatory_risks": [
    {{
      "risk": "<string>",
      "severity": "<low|medium|high|critical>",
      "probability": "<low|medium|high>",
      "mitigation": "<string>"
    }}
  ],
  "technology_risks": [
    {{
      "risk": "<string>",
      "severity": "<low|medium|high|critical>"
    }}
  ],
  "market_risks": [
    {{
      "risk": "<string>",
      "severity": "<low|medium|high|critical>"
    }}
  ],
  "operational_risks": [
    {{
      "risk": "<string>",
      "severity": "<low|medium|high|critical>"
    }}
  ],
  "macro_risks": ["<risk1>", "<risk2>"],
  "esg_concerns": ["<concern1>"],
  "overall_risk_score": <1-10>,
  "risk_adjusted_return_potential": "<low|medium|high|exceptional>",
  "deal_breakers": ["<breaker1>"],
  "summary": "<2-3 sentence summary>"
}}"""

        result = self._call_llm_json(prompt)
        self.log(f"Risk score: {result.get('overall_risk_score', 'N/A')}/10")
        return result
