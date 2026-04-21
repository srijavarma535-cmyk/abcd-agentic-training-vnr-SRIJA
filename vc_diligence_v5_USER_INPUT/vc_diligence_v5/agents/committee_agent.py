import json
from agents.base_agent import BaseAgent
from config.settings import Settings

class CommitteeAgent(BaseAgent):
    name  = "CommitteeAgent"
    role  = "Managing Partner & Investment Decision Maker"
    emoji = "🏦"

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def analyze(self, context: dict) -> dict:
        startup  = context.get("startup_name", "Unknown")
        results  = context.get("all_results", {})
        weights  = context.get("scoring_weights", {})
        self._emit(f"synthesising final verdict for '{startup}'…")

        score_map = {
            "market":      results.get("market",      {}).get("overall_market_score",      5),
            "team":        results.get("team",         {}).get("overall_team_score",        5),
            "product":     results.get("product",      {}).get("overall_product_score",     5),
            "financials":  results.get("financials",   {}).get("overall_financial_score",   5),
            "competitive": results.get("competitive",  {}).get("overall_competitive_score", 5),
            "risk":        results.get("risk",         {}).get("overall_risk_score",        5),
        }
        weighted = round(sum(score_map[k] * weights.get(k, 1/6) for k in score_map), 2)
        summaries = {k: results.get(k, {}).get("summary", "") for k in results}

        prompt = f"""You are the Managing Partner of a top VC fund.
Startup: {startup}
Agent scores: {json.dumps(score_map)}
Weighted composite score: {weighted}/10
Agent summaries: {json.dumps(summaries)}

Return JSON with EXACTLY these keys:
{{
  "verdict": "<STRONG INVEST|INVEST|CONDITIONAL INVEST|HOLD|PASS>",
  "conviction": "<low|medium|high|very high>",
  "check_size_recommended": "<string or null>",
  "round_stage": "<Pre-seed|Seed|Series A|Series B|Growth>",
  "investment_thesis": "<3 sentence thesis>",
  "bull_case": "<2 sentence upside>",
  "bear_case": "<2 sentence downside>",
  "key_questions": ["<q1>","<q2>","<q3>","<q4>","<q5>"],
  "next_steps": ["<s1>","<s2>","<s3>"],
  "comparable_exits": ["<c1>","<c2>"],
  "worth_investing": <true|false>,
  "summary": "<3 sentence VC memo executive summary>"
}}"""
        result = self._call_json(prompt)
        result["overall_score"]   = weighted
        result["score_breakdown"] = score_map
        result["agent"]           = "CommitteeAgent"
        return result
