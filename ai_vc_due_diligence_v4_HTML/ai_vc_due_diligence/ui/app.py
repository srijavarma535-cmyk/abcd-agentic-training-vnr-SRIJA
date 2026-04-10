"""
Streamlit Web UI — AI VC Due Diligence Agent Team
Powered by Google Gemini (FREE tier)
Run: streamlit run ui/app.py
"""
import streamlit as st
import asyncio
import json
import sys
import os

# Load .env automatically
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.pipeline import DueDiligencePipeline
from config.settings import Settings

st.set_page_config(
    page_title="AI VC Due Diligence",
    page_icon="🏦",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("🏦 AI VC Due Diligence Agent Team")
st.caption("⚡ Powered by **Google Gemini** — 100% FREE (1500 requests/day)")

with st.sidebar:
    st.header("⚙️ Configuration")

    st.markdown("""
    **🆓 Get FREE Gemini API Key:**
    1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
    2. Sign in with Google
    3. Click **Create API Key**
    4. Paste below ↓
    """)

    api_key = st.text_input(
        "Gemini API Key (FREE)",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        placeholder="AIza..."
    )
    serper_key = st.text_input(
        "Serper API Key (optional, free tier)",
        type="password",
        value=os.getenv("SERPER_API_KEY", ""),
        placeholder="Optional web search"
    )
    mode = st.selectbox("Analysis Mode", ["full", "quick", "market-only", "team-only"])

    st.divider()
    st.markdown("**Scoring Weights**")
    w_market  = st.slider("Market",      0.0, 1.0, 0.20)
    w_team    = st.slider("Team",        0.0, 1.0, 0.25)
    w_product = st.slider("Product",     0.0, 1.0, 0.20)
    w_fin     = st.slider("Financials",  0.0, 1.0, 0.15)
    w_comp    = st.slider("Competition", 0.0, 1.0, 0.10)
    w_risk    = st.slider("Risk",        0.0, 1.0, 0.10)

# Input
col1, col2 = st.columns(2)
with col1:
    startup_name = st.text_input("Startup Name *", placeholder="e.g. Stripe, Notion, Figma")
    startup_url  = st.text_input("Website URL (optional)", placeholder="https://startup.com")
with col2:
    description  = st.text_area("Description / Pitch (optional)",
                                 placeholder="Describe what the startup does...", height=100)
    deck_file    = st.file_uploader("Pitch Deck PDF (optional)", type=["pdf"])

run_btn = st.button("🚀 Run Due Diligence", type="primary", use_container_width=True)

if run_btn:
    if not startup_name:
        st.error("Please enter a startup name.")
        st.stop()
    if not api_key:
        st.error(
            "❌ Gemini API Key required!\n\n"
            "👉 Get yours FREE at: https://aistudio.google.com/app/apikey  (no credit card)"
        )
        st.stop()

    deck_path = None
    if deck_file:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(deck_file.read())
            deck_path = tmp.name

    settings = Settings()
    settings.gemini_api_key = api_key
    settings.serper_api_key = serper_key
    settings.scoring_weights = {
        "market": w_market, "team": w_team, "product": w_product,
        "financials": w_fin, "competition": w_comp, "risk": w_risk,
    }

    pipeline = DueDiligencePipeline(settings)

    with st.spinner("🤖 Agent team analyzing with Gemini..."):
        report = asyncio.run(pipeline.run(
            startup_name=startup_name,
            url=startup_url or None,
            deck_path=deck_path,
            mode=mode,
        ))

    st.success("✅ Analysis complete!")

    committee     = report.get("committee", {})
    overall_score = report.get("overall_score", 0)
    verdict       = report.get("verdict", "N/A")

    st.markdown("---")
    st.subheader("📊 Investment Decision")

    m1, m2, m3 = st.columns(3)
    m1.metric("Overall Score", f"{overall_score}/10")
    m2.metric("Verdict",       verdict)
    m3.metric("Conviction",    committee.get("conviction_level", "N/A").title())

    agent_results = report.get("agent_results", {})
    tabs = st.tabs(["📋 Summary", "📈 Market", "👥 Team", "🚀 Product",
                    "💰 Financials", "🔍 Competitive", "⚠️ Risk", "📄 Full Report"])

    def show_agent(tab, key, score_key, extra_keys=None):
        r = agent_results.get(key, {})
        with tab:
            if not r:
                st.info("Not analyzed in this mode.")
                return
            st.metric("Score", f"{r.get(score_key, 'N/A')}/10")
            st.write(r.get("summary", ""))
            if extra_keys:
                for ek, label in extra_keys:
                    val = r.get(ek)
                    if val:
                        st.markdown(f"**{label}:** {val}")
            with st.expander("Full Data"):
                st.json(r)

    with tabs[0]:
        st.markdown(f"**{committee.get('summary', '')}**")
        st.markdown("#### 🐂 Bull Case");  st.write(committee.get("bull_case", ""))
        st.markdown("#### 🐻 Bear Case");  st.write(committee.get("bear_case", ""))
        st.markdown("#### 💡 Investment Thesis"); st.write(committee.get("investment_thesis", ""))
        st.markdown("#### ❓ Key Diligence Questions")
        for q in committee.get("key_diligence_questions", []):
            st.markdown(f"- {q}")
        st.markdown("#### 🔜 Next Steps")
        for s in committee.get("next_steps", []):
            st.markdown(f"1. {s}")

    show_agent(tabs[1], "market",      "overall_market_score",
               [("market_growth_rate_pct","Growth Rate %"), ("key_trends","Key Trends")])
    show_agent(tabs[2], "team",        "overall_team_score",
               [("key_strengths","Strengths"), ("key_gaps","Gaps")])
    show_agent(tabs[3], "product",     "overall_product_score",
               [("product_stage","Stage"), ("pmf_score","PMF Score")])
    show_agent(tabs[4], "financials",  "overall_financial_score",
               [("revenue_model","Revenue Model"), ("burn_rate_assessment","Burn Rate")])
    show_agent(tabs[5], "competitive", "overall_competitive_score",
               [("market_concentration","Market Concentration")])
    show_agent(tabs[6], "risk",        "overall_risk_score",
               [("deal_breakers","Deal Breakers"), ("risk_adjusted_return_potential","Return Potential")])

    with tabs[7]:
        st.markdown(report.get("markdown_report", ""))
        st.download_button("⬇️ Download Markdown",
                           report.get("markdown_report", ""),
                           file_name=f"{startup_name.replace(' ','_')}_report.md",
                           mime="text/markdown")
        st.download_button("⬇️ Download JSON",
                           json.dumps(report, indent=2),
                           file_name=f"{startup_name.replace(' ','_')}_report.json",
                           mime="application/json")
