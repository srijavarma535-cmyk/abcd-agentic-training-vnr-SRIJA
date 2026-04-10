"""
Unit tests — mocked so no API key needed.
Run: pytest tests/test_agents.py -v
"""
import asyncio
import pytest
from unittest.mock import patch
from config.settings import Settings
from agents import (
    MarketAnalysisAgent, TeamAnalysisAgent, ProductAnalysisAgent,
    FinancialAnalysisAgent, CompetitiveIntelligenceAgent,
    RiskAssessmentAgent, InvestmentCommitteeAgent,
)

MOCK_SETTINGS = Settings()
MOCK_SETTINGS.gemini_api_key = "test-fake-key"

SAMPLE_CONTEXT = {
    "startup_name": "TestStartup AI",
    "description": "An AI-powered B2B SaaS platform for automating enterprise workflows.",
    "web_data": "TestStartup helps companies save 40% on ops cost.",
    "deck_text": "Series A. $2M ARR. 3x YoY growth.",
    "team_info": "CEO: ex-Google, CTO: ex-Meta, 10 engineers",
    "financial_data": "$2M ARR, 80% gross margin, 18 months runway",
}

MOCK_LLM_RESPONSE = {
    "overall_market_score": 8, "overall_team_score": 8,
    "overall_product_score": 7, "overall_financial_score": 7,
    "overall_competitive_score": 7, "overall_risk_score": 6,
    "summary": "Strong startup with solid fundamentals.",
    "tam": {"value_usd_billions": 50, "source_rationale": "IDC report"},
    "sam": {"value_usd_billions": 5, "rationale": "SMB segment"},
    "som": {"value_usd_billions": 0.5, "rationale": "First 3 years"},
    "market_growth_rate_pct": 22,
    "market_timing": {"score": 8, "rationale": "AI adoption wave"},
    "key_trends": ["LLM adoption", "workflow automation"],
    "market_risks": ["Recession slowdown"],
    "verdict": "PASS", "conviction_level": "high",
    "investment_thesis": "Strong PMF.", "bull_case": "10x in 3 years.",
    "bear_case": "Competitive pressure.", "key_diligence_questions": ["NRR?"],
    "next_steps": ["Founder call"], "overall_score": 7.5,
    "score_breakdown": {"market": 8, "team": 8},
    "founders": [], "team_completeness_score": 8,
    "domain_expertise_score": 8, "execution_track_record_score": 7,
    "founder_market_fit_score": 8, "key_strengths": ["Domain expertise"],
    "key_gaps": ["Sales hire needed"], "hiring_velocity_assessment": "Good",
    "product_stage": "mvp", "pmf_score": 7, "technical_moat_score": 7,
    "defensibility": {"ip_protection": "none", "network_effects": False,
                      "switching_costs": "medium", "data_moat": True},
    "innovation_score": 8, "ux_quality_score": 7, "scalability_score": 8,
    "key_features": ["AI workflow"], "product_risks": ["Competition"],
    "revenue_model": "SaaS", "current_arr_estimate_usd": 2000000,
    "growth_rate_estimate_pct": 200, "unit_economics": {"ltv_cac_ratio": 3.5},
    "burn_rate_assessment": "medium", "runway_months_estimate": 18,
    "fundraising_history": [], "valuation_reasonableness_score": 7,
    "financial_health_score": 7, "red_flags": [],
    "direct_competitors": [], "indirect_competitors": [],
    "market_concentration": "fragmented", "differentiation_score": 7,
    "competitive_moat_score": 7, "incumbent_threat_score": 5,
    "white_space_opportunities": ["Enterprise segment"],
    "competitive_risks": ["Big Tech entry"],
    "regulatory_risks": [], "technology_risks": [], "market_risks": [],
    "operational_risks": [], "macro_risks": ["Recession"],
    "esg_concerns": [], "risk_adjusted_return_potential": "high",
    "deal_breakers": [],
}

def mock_llm_json(self, prompt, system_override=None):
    return MOCK_LLM_RESPONSE

class TestMarketAgent:
    def test_analyze(self):
        agent = MarketAnalysisAgent(MOCK_SETTINGS)
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(SAMPLE_CONTEXT))
        assert result["overall_market_score"] == 8

class TestTeamAgent:
    def test_analyze(self):
        agent = TeamAnalysisAgent(MOCK_SETTINGS)
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(SAMPLE_CONTEXT))
        assert "overall_team_score" in result

class TestProductAgent:
    def test_analyze(self):
        agent = ProductAnalysisAgent(MOCK_SETTINGS)
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(SAMPLE_CONTEXT))
        assert "overall_product_score" in result

class TestFinancialAgent:
    def test_analyze(self):
        agent = FinancialAnalysisAgent(MOCK_SETTINGS)
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(SAMPLE_CONTEXT))
        assert "overall_financial_score" in result

class TestCompetitiveAgent:
    def test_analyze(self):
        agent = CompetitiveIntelligenceAgent(MOCK_SETTINGS)
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(SAMPLE_CONTEXT))
        assert "overall_competitive_score" in result

class TestRiskAgent:
    def test_analyze(self):
        agent = RiskAssessmentAgent(MOCK_SETTINGS)
        ctx = {**SAMPLE_CONTEXT, "prior_results": {}}
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(ctx))
        assert "overall_risk_score" in result

class TestCommitteeAgent:
    def test_analyze(self):
        agent = InvestmentCommitteeAgent(MOCK_SETTINGS)
        ctx = {
            "startup_name": "TestStartup AI",
            "all_results": {
                "market": {"summary": "Good.", "overall_market_score": 8},
                "team":   {"summary": "Strong.", "overall_team_score": 8},
            },
            "scoring_weights": MOCK_SETTINGS.scoring_weights,
        }
        with patch.object(agent, "_call_llm_json", side_effect=mock_llm_json):
            result = asyncio.run(agent.analyze(ctx))
        assert "verdict" in result

class TestSettings:
    def test_missing_api_key(self):
        s = Settings()
        s.gemini_api_key = ""
        with pytest.raises(ValueError):
            s.validate()

    def test_weights_keys(self):
        s = Settings()
        assert "market" in s.scoring_weights
        assert "team" in s.scoring_weights
