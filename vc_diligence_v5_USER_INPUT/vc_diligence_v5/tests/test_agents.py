"""
Unit tests — all LLM calls are mocked, no Ollama needed.
Run: pytest tests/ -v
"""
import asyncio, pytest
from unittest.mock import patch
from config.settings import Settings
from agents import (MarketAnalysisAgent, TeamAnalysisAgent, ProductAnalysisAgent,
                    FinancialAnalysisAgent, CompetitiveAgent, RiskAgent, CommitteeAgent)

S = Settings()
S.ollama_host  = "http://localhost:11434"
S.ollama_model = "llama3.2"

CTX = {"startup_name":"TestCo","description":"AI SaaS platform",
       "web_data":"","deck_text":"","team_info":"","financial_data":""}

MOCK = {
    "tam_usd_billions":50,"sam_usd_billions":5,"som_usd_billions":0.5,
    "cagr_pct":22,"market_stage":"growing","timing_score":8,"geography":"Global",
    "key_trends":["AI adoption"],"market_risks":["Competition"],"regulation_risk":"medium",
    "overall_market_score":8,"ai_insight":"Strong market.","summary":"Growing market.",
    "founders":[{"name":"CEO","role":"CEO","background":"ex-Google","prior_exits":1}],
    "team_size_estimate":"11-50","execution_score":8,"domain_expertise_score":8,
    "founder_market_fit_score":8,"team_completeness_score":7,"key_strengths":["Tech"],
    "key_gaps":["Sales"],"hiring_assessment":"Good","risk_level":"medium","overall_team_score":8,
    "product_name":"TestProduct","tagline":"AI for everyone","stage":"mvp","pmf_score":7,
    "innovation_score":8,"technical_moat_score":7,"scalability_score":8,"ux_score":7,
    "key_features":["AI","Analytics"],"tech_stack_inferred":["Python","React"],
    "defensibility":{"ip":"none","network_effects":False,"data_moat":True},
    "product_risks":["Competition"],"overall_product_score":8,
    "revenue_model":"SaaS","arr_usd_estimate":2000000,"mrr_usd_estimate":166666,
    "growth_rate_pct":200,"burn_rate_monthly_usd":150000,"runway_months":18,
    "gross_margin_pct":80,"ltv_cac_ratio":3.5,"payback_months":12,"funding_rounds":[],
    "burn_risk":"medium","valuation_score":7,"overall_financial_score":7,"red_flags":[],
    "direct_competitors":[{"name":"CompA","strength":"Brand","weakness":"Price","stage":"growth","threat":"medium"}],
    "indirect_competitors":[],"market_concentration":"fragmented","differentiation_score":7,
    "moat_score":7,"incumbent_threat_score":6,"positioning":{},"white_space":["SMB"],
    "competitive_risks":["Big Tech"],"overall_competitive_score":7,
    "regulatory_risks":[],"technology_risks":[],"market_risks":[],"operational_risks":[],
    "macro_risks":["Recession"],"esg_concerns":[],"deal_breakers":[],
    "risk_adjusted_return":"high","overall_risk_score":6,
    "verdict":"INVEST","conviction":"high","check_size_recommended":"$500K-2M",
    "round_stage":"Seed","investment_thesis":"Strong PMF.","bull_case":"10x potential.",
    "bear_case":"Competitive pressure.","key_questions":["NRR?"],"next_steps":["Call founders"],
    "comparable_exits":["Salesforce"],"worth_investing":True,
    "overall_score":7.6,"score_breakdown":{"market":8,"team":8,"product":8,"financials":7,"competitive":7,"risk":6},
}

def mock_json(self, p, s=None): return MOCK

def run(coro): return asyncio.get_event_loop().run_until_complete(coro)

class TestAgents:
    def test_market(self):
        a = MarketAnalysisAgent(S)
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(CTX))
        assert r["overall_market_score"] == 8

    def test_team(self):
        a = TeamAnalysisAgent(S)
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(CTX))
        assert r["overall_team_score"] == 8

    def test_product(self):
        a = ProductAnalysisAgent(S)
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(CTX))
        assert r["overall_product_score"] == 8

    def test_financial(self):
        a = FinancialAnalysisAgent(S)
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(CTX))
        assert r["overall_financial_score"] == 7

    def test_competitive(self):
        a = CompetitiveAgent(S)
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(CTX))
        assert r["overall_competitive_score"] == 7

    def test_risk(self):
        a = RiskAgent(S)
        ctx = {**CTX, "prior_results":{}}
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(ctx))
        assert r["overall_risk_score"] == 6

    def test_committee(self):
        a = CommitteeAgent(S)
        ctx = {"startup_name":"TestCo","all_results":{"market":MOCK,"team":MOCK},
               "scoring_weights":S.scoring_weights}
        with patch.object(a,"_call_json",mock_json):
            r = run(a.analyze(ctx))
        assert r["verdict"] == "INVEST"

class TestSettings:
    def test_missing_host(self):
        s = Settings(); s.ollama_host = ""
        # validate checks connectivity, will raise RuntimeError
        import urllib.request
        with patch("urllib.request.urlopen", side_effect=Exception("no conn")):
            with pytest.raises(RuntimeError):
                s.validate()
