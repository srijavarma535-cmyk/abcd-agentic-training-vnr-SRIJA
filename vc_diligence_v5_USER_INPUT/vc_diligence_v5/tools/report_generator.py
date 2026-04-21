from datetime import datetime

class ReportGenerator:
    def generate(self, startup: str, agents: dict, committee: dict) -> str:
        score   = committee.get("overall_score","N/A")
        verdict = committee.get("verdict","N/A")
        now     = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        lines   = [
            f"# VC Due Diligence — {startup}",
            f"> {now} | Score: **{score}/10** | Verdict: **{verdict}**","",
            "## Executive Summary","",committee.get("summary",""),"",
            "## Investment Thesis","",committee.get("investment_thesis",""),"",
            "**Bull:** "+committee.get("bull_case",""),"",
            "**Bear:** "+committee.get("bear_case",""),"",
            "## Score Breakdown","","| Dimension | Score |","|---|---|",
        ]
        for k,v in committee.get("score_breakdown",{}).items():
            lines.append(f"| {k.title()} | {v}/10 |")
        lines += [f"| **Overall** | **{score}/10** |",""]
        for key,sk in [("market","overall_market_score"),("team","overall_team_score"),
                       ("product","overall_product_score"),("financials","overall_financial_score"),
                       ("competitive","overall_competitive_score"),("risk","overall_risk_score")]:
            r = agents.get(key,{})
            if r and not r.get("error"):
                lines += [f"## {key.title()} — {r.get(sk,'?')}/10","",r.get("summary",""),""]
        lines += ["---","*AI VC Due Diligence Agent Team — Ollama Edition*"]
        return "\n".join(lines)
