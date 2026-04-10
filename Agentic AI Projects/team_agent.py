"""
Team Analysis Agent
Evaluates founding team, experience, domain expertise, and execution ability.
"""
from agents.base_agent import BaseAgent


class TeamAnalysisAgent(BaseAgent):
    name = "TeamAnalyst"
    role = "Talent & Leadership Evaluator"
    emoji = "👥"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        description = context.get("description", "")
        team_info = context.get("team_info", "")
        web_data = context.get("web_data", "")

        self.log(f"Evaluating team for '{startup}'...")

        prompt = f"""Evaluate the founding team and leadership of this startup:

Startup: {startup}
Description: {description}
Team Info: {team_info}
Web Data: {web_data}

Return a JSON object with this exact structure:
{{
  "agent": "TeamAnalysisAgent",
  "founders": [
    {{
      "inferred_role": "<CEO/CTO/etc>",
      "domain_expertise_score": <1-10>,
      "prior_exits": <number or null>,
      "notes": "<string>"
    }}
  ],
  "team_completeness_score": <1-10>,
  "domain_expertise_score": <1-10>,
  "execution_track_record_score": <1-10>,
  "founder_market_fit_score": <1-10>,
  "key_strengths": ["<strength1>", "<strength2>"],
  "key_gaps": ["<gap1>", "<gap2>"],
  "hiring_velocity_assessment": "<string>",
  "overall_team_score": <1-10>,
  "summary": "<2-3 sentence summary>"
}}"""

        result = self._call_llm_json(prompt)
        self.log(f"Team score: {result.get('overall_team_score', 'N/A')}/10")
        return result
