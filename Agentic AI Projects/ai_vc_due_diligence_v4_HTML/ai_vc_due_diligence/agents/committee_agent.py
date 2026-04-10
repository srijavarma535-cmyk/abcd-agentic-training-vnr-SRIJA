"""
Investment Committee Agent (Synthesis)
Aggregates all agent findings and produces final investment memo + verdict.
"""
import json
from agents.base_agent import BaseAgent
from config.settings import Settings


class InvestmentCommitteeAgent(BaseAgent):
    name = "InvestmentCommittee"
    role = "Managing Partner & Lead Decision Maker"
    emoji = "🏦"

    async def analyze(self, context: dict) -> dict:
        startup = context.get("startup_name", "Unknown")
        all_results = context.get("all_results", {})
        weights = context.get("scoring_weights", {})

        self.log(f"Synthesizing final investment decision for '{startup}'...")

        # Compute weighted score
        score_map = {
            "market": all_results.get("market", {}).get("overall_market_score", 5),
            "team": all_results.get("team", {}).get("overall_team_score", 5),
            "product": all_results.get("product", {}).get("overall_product_score", 5),
            "financials": all_results.get("financials", {}).get("overall_financial_score", 5),
            "competition": all_results.get("competitive", {}).get("overall_competitive_score", 5),
            "risk": all_results.get("risk", {}).get("overall_risk_score", 5),
        }

        weighted_score = sum(
            score_map.get(k, 5) * weights.get(k, 1 / len(score_map))
            for k in score_map
        )

        results_summary = json.dumps({k: v.get("summary", "") for k, v in all_results.items()}, indent=2)
        scores_json = json.dumps(score_map, indent=2)

        prompt = f"""You are the Managing Partner of a top VC fund presenting to the Investment Committee.

Startup: {startup}
Agent Scores: {scores_json}
Weighted Score: {round(weighted_score, 2)}/10
Analysis Summaries: {results_summary}

Write a complete investment memo and final decision. Return JSON:
{{
  "agent": "InvestmentCommitteeAgent",
  "overall_score": {round(weighted_score, 2)},
  "score_breakdown": {json.dumps(score_map)},
  "verdict": "<STRONG PASS|PASS|CONDITIONAL PASS|SOFT PASS|PASS WITH CONDITIONS|NO GO>",
  "conviction_level": "<low|medium|high|very high>",
  "recommended_check_size_usd": "<string or null>",
  "recommended_round_stage": "<string>",
  "investment_thesis": "<3-4 sentences on why to invest>",
  "bear_case": "<2-3 sentences on why this could fail>",
  "bull_case": "<2-3 sentences on the upside scenario>",
  "key_diligence_questions": [
    "<question1>",
    "<question2>",
    "<question3>",
    "<question4>",
    "<question5>"
  ],
  "next_steps": ["<step1>", "<step2>", "<step3>"],
  "comparable_exits": ["<comp1>", "<comp2>"],
  "summary": "<Executive summary 3-4 sentences>"
}}"""

        result = self._call_llm_json(prompt)
        result["overall_score"] = round(weighted_score, 2)
        self.log(f"Final verdict: {result.get('verdict', 'N/A')} | Score: {result.get('overall_score')}/10")
        return result
