"""
Due Diligence Pipeline Orchestrator
Coordinates all agents with rate-limit-safe execution.
"""
import asyncio
import time
import json
from datetime import datetime
from typing import Optional

from config.settings import Settings
from agents import (
    MarketAnalysisAgent, TeamAnalysisAgent, ProductAnalysisAgent,
    FinancialAnalysisAgent, CompetitiveIntelligenceAgent,
    RiskAssessmentAgent, InvestmentCommitteeAgent,
)
from tools.web_scraper import WebScraper
from tools.pdf_parser import PDFParser
from tools.report_generator import ReportGenerator


class DueDiligencePipeline:
    """Orchestrates the multi-agent due diligence workflow."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.scraper = WebScraper(settings)
        self.pdf_parser = PDFParser(settings)
        self.report_gen = ReportGenerator()

        self.agents = {
            "market":      MarketAnalysisAgent(settings),
            "team":        TeamAnalysisAgent(settings),
            "product":     ProductAnalysisAgent(settings),
            "financials":  FinancialAnalysisAgent(settings),
            "competitive": CompetitiveIntelligenceAgent(settings),
        }
        self.risk_agent = RiskAssessmentAgent(settings)
        self.committee  = InvestmentCommitteeAgent(settings)

    async def run(
        self,
        startup_name: str,
        url: Optional[str] = None,
        deck_path: Optional[str] = None,
        mode: str = "full",
    ) -> dict:
        print(f"\n🔄 Phase 1: Data Collection")
        context = await self._collect_data(startup_name, url, deck_path)

        print(f"\n🔄 Phase 2: Agent Analysis")
        agent_results = await self._run_agents(context, mode)

        print(f"\n🔄 Phase 3: Risk Assessment")
        risk_context = {**context, "prior_results": agent_results}
        risk_result = await self._run_single(self.risk_agent, risk_context, "risk")
        agent_results["risk"] = risk_result

        print(f"\n🔄 Phase 4: Investment Committee Synthesis")
        committee_context = {
            "startup_name": startup_name,
            "all_results": agent_results,
            "scoring_weights": self.settings.scoring_weights,
        }
        committee_result = await self._run_single(self.committee, committee_context, "committee")

        print(f"\n🔄 Phase 5: Report Generation")
        return self._assemble_report(startup_name, context, agent_results, committee_result)

    async def _collect_data(self, startup_name, url, deck_path):
        context = {
            "startup_name": startup_name,
            "description": startup_name,
            "web_data": "", "deck_text": "",
            "team_info": "", "financial_data": "",
        }
        if url and self.settings.enable_web_search:
            print(f"  🌐 Scraping: {url}")
            context["web_data"] = (await self.scraper.scrape(url))[:3000]
        if deck_path and self.settings.enable_pdf_parsing:
            print(f"  📄 Parsing deck: {deck_path}")
            context["deck_text"] = self.pdf_parser.parse(deck_path)[:3000]
        return context

    async def _run_single(self, agent, context: dict, name: str) -> dict:
        """Run one agent, catching errors gracefully."""
        try:
            return await agent.analyze(context)
        except Exception as e:
            print(f"  ⚠️  Agent '{name}' failed: {e}")
            return {"error": str(e), "summary": "Analysis failed."}

    async def _run_agents(self, context: dict, mode: str) -> dict:
        """Run agents with a small delay between each to respect rate limits."""
        if mode == "market-only":
            active = {"market": self.agents["market"]}
        elif mode == "team-only":
            active = {"team": self.agents["team"]}
        elif mode == "quick":
            active = {k: self.agents[k] for k in ["market", "team", "product"]}
        else:
            active = self.agents

        results = {}
        items = list(active.items())

        # Run in small batches of 2 to avoid rate limits
        batch_size = 2
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            tasks = {name: agent.analyze(context) for name, agent in batch}
            batch_results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            for name, result in zip(tasks.keys(), batch_results):
                if isinstance(result, Exception):
                    print(f"  ⚠️  Agent '{name}' failed: {result}")
                    results[name] = {"error": str(result), "summary": "Analysis failed."}
                else:
                    results[name] = result

            # Small pause between batches to respect per-minute quota
            if i + batch_size < len(items):
                print(f"  ⏳ Pausing 5s between batches (rate limit protection)...")
                await asyncio.sleep(5)

        return results

    def _assemble_report(self, startup_name, context, agent_results, committee_result):
        return {
            "startup": startup_name,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "overall_score": committee_result.get("overall_score", 0),
            "verdict": committee_result.get("verdict", "N/A"),
            "conviction_level": committee_result.get("conviction_level", "N/A"),
            "agent_results": agent_results,
            "committee": committee_result,
            "markdown_report": self.report_gen.generate(
                startup_name, agent_results, committee_result
            ),
        }
