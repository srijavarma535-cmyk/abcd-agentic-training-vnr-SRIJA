"""
DueDiligencePipeline — async orchestrator with streaming + graceful error handling.
"""
import asyncio, json
from datetime import datetime
from typing import Optional, Callable
from config.settings import Settings
from agents import (
    MarketAnalysisAgent, TeamAnalysisAgent, ProductAnalysisAgent,
    FinancialAnalysisAgent, CompetitiveAgent, RiskAgent, CommitteeAgent,
)
from tools.web_scraper      import WebScraper
from tools.pdf_parser       import PDFParser
from tools.report_generator import ReportGenerator
from tools.html_generator   import HTMLReportGenerator

# Default scores used when an agent fails
_DEFAULTS = {
    "market":      {"overall_market_score":5,      "summary":"Analysis unavailable.","ai_insight":""},
    "team":        {"overall_team_score":5,         "summary":"Analysis unavailable.","ai_insight":""},
    "product":     {"overall_product_score":5,      "summary":"Analysis unavailable.","ai_insight":""},
    "financials":  {"overall_financial_score":5,    "summary":"Analysis unavailable.","ai_insight":""},
    "competitive": {"overall_competitive_score":5,  "summary":"Analysis unavailable.","ai_insight":""},
    "risk":        {"overall_risk_score":5,         "summary":"Analysis unavailable.","ai_insight":""},
}


class DueDiligencePipeline:
    def __init__(self, settings: Settings, on_event: Optional[Callable] = None):
        self.settings   = settings
        self.on_event   = on_event or (lambda e: None)
        self.scraper    = WebScraper()
        self.pdf_parser = PDFParser()
        self.report_gen = ReportGenerator()
        self.html_gen   = HTMLReportGenerator()

        self._batch1 = {
            "market":      MarketAnalysisAgent(settings),
            "team":        TeamAnalysisAgent(settings),
            "product":     ProductAnalysisAgent(settings),
            "financials":  FinancialAnalysisAgent(settings),
            "competitive": CompetitiveAgent(settings),
        }
        self._risk_agent      = RiskAgent(settings)
        self._committee_agent = CommitteeAgent(settings)

        for name, agent in self._batch1.items():
            n = name
            agent.set_status_callback(
                lambda ag, msg, _n=n: self._emit("agent_log", {"agent": _n, "msg": msg}))
        self._risk_agent.set_status_callback(
            lambda ag, msg: self._emit("agent_log", {"agent": "risk", "msg": msg}))
        self._committee_agent.set_status_callback(
            lambda ag, msg: self._emit("agent_log", {"agent": "committee", "msg": msg}))

    def _emit(self, event: str, data: dict):
        self.on_event({"event": event, "data": data,
                       "ts": datetime.utcnow().isoformat()})

    async def run(self, startup_name: str, description: str = "",
                  url: Optional[str] = None,
                  deck_path: Optional[str] = None, mode: str = "full") -> dict:

        self._emit("phase", {"phase": 1, "label": "Data Collection"})
        context = await self._collect(startup_name, description, url, deck_path)

        self._emit("phase", {"phase": 2, "label": "Parallel Agent Analysis"})
        agent_results = await self._run_batch1(context, mode)

        self._emit("phase", {"phase": 3, "label": "Risk Assessment"})
        risk_ctx = {**context, "prior_results": agent_results}
        risk_result = await self._safe_run(self._risk_agent, risk_ctx, "risk")
        agent_results["risk"] = risk_result
        self._emit("agent_done", {"agent": "risk", "result": risk_result})

        self._emit("phase", {"phase": 4, "label": "Investment Committee"})
        committee_result = await self._safe_run(
            self._committee_agent,
            {"startup_name": startup_name, "all_results": agent_results,
             "scoring_weights": self.settings.scoring_weights},
            "committee"
        )
        self._emit("agent_done", {"agent": "committee", "result": committee_result})

        self._emit("phase", {"phase": 5, "label": "Generating Report"})
        report = self._assemble(startup_name, context, agent_results, committee_result)
        self._emit("complete", {"score": report["overall_score"],
                                "verdict": report["verdict"]})
        return report

    async def _collect(self, name, description, url, deck_path):
        ctx = {
            "startup_name": name,
            "description":  description if description else name,
            "web_data": "", "deck_text": "", "team_info": "", "financial_data": ""
        }
        if url:
            self._emit("log", {"msg": f"Scraping {url}…"})
            ctx["web_data"] = (await self.scraper.scrape(url))[:3000]
        if deck_path:
            self._emit("log", {"msg": "Parsing PDF…"})
            ctx["deck_text"] = self.pdf_parser.parse(deck_path)[:3000]
        return ctx

    async def _safe_run(self, agent, context, name):
        """Run an agent — on any error return safe defaults instead of crashing."""
        try:
            result = await agent.analyze(context)
            # Ensure the result is a dict (repair if _parse_error present)
            if not isinstance(result, dict):
                raise ValueError(f"Agent returned non-dict: {type(result)}")
            if result.get("_parse_error"):
                self._emit("agent_error", {"agent": name,
                           "error": f"JSON parse error: {result['_parse_error'][:80]}"})
                fallback = dict(_DEFAULTS.get(name, {}))
                fallback["error"] = "JSON parse failed"
                return fallback
            return result
        except Exception as ex:
            self._emit("agent_error", {"agent": name, "error": str(ex)})
            fallback = dict(_DEFAULTS.get(name, {}))
            fallback["error"] = str(ex)
            return fallback

    async def _run_batch1(self, context, mode):
        if mode == "market-only":
            active = {"market": self._batch1["market"]}
        elif mode == "team-only":
            active = {"team": self._batch1["team"]}
        elif mode == "quick":
            active = {k: self._batch1[k] for k in ["market", "team", "product"]}
        else:
            active = self._batch1

        results = {}

        async def run_one(name, agent):
            self._emit("agent_start", {"agent": name})
            r = await self._safe_run(agent, context, name)
            results[name] = r
            self._emit("agent_done", {"agent": name, "result": r})

        await asyncio.gather(*[run_one(n, a) for n, a in active.items()])

        # Fill missing agents with defaults
        for k in ["market", "team", "product", "financials", "competitive"]:
            if k not in results:
                results[k] = dict(_DEFAULTS.get(k, {}))
        return results

    def _assemble(self, name, context, agent_results, committee):
        # Safe score extraction
        def safe_score(v, default=5.0):
            try: return float(v)
            except (TypeError, ValueError): return default

        score   = safe_score(committee.get("overall_score", 0))
        verdict = committee.get("verdict", "N/A") or "N/A"
        worth   = committee.get("worth_investing", score >= 6.5)
        if isinstance(worth, str):
            worth = worth.lower() == "true"

        report = {
            "startup":        name,
            "generated_at":   datetime.utcnow().isoformat() + "Z",
            "overall_score":  round(score, 2),
            "verdict":        verdict,
            "worth_investing": bool(worth),
            "conviction":     committee.get("conviction", "N/A") or "N/A",
            "agent_results":  agent_results,
            "committee":      committee,
            "markdown_report": self.report_gen.generate(name, agent_results, committee),
        }
        try:
            report["html_report"] = self.html_gen.generate(report)
        except Exception as ex:
            report["html_report"] = f"<html><body><h1>Report Error</h1><pre>{ex}</pre></body></html>"
            print(f"  ⚠️  HTML generation error: {ex}")
        return report
