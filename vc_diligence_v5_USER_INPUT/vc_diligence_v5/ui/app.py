"""
Streamlit UI — AI VC Due Diligence v5
User enters ANY startup name → agents analyse it → live results dashboard.
Run: streamlit run ui/app.py
"""
import streamlit as st
import asyncio, json, os, sys, threading, queue
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

from orchestrator.pipeline import DueDiligencePipeline
from config.settings import Settings

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI VC Due Diligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif!important}
.stApp{background:#080c10}
[data-testid="stSidebar"]{background:#0d1117;border-right:1px solid #1e293b}
.block-container{padding-top:1rem}
h1,h2,h3,h4{color:#f1f5f9!important}
p,li{color:#cbd5e1}
.stTextInput>div>div>input{
  background:#1e293b!important;border:1px solid #7c3aed!important;
  color:#f1f5f9!important;border-radius:8px!important;font-size:16px!important}
.stTextArea>div>div>textarea{
  background:#1e293b!important;border:1px solid #334155!important;
  color:#cbd5e1!important;border-radius:8px!important}
.stSelectbox>div>div{background:#1e293b!important;border:1px solid #334155!important;color:#cbd5e1!important}
.stButton>button{border-radius:8px!important;font-weight:700!important;font-size:15px!important}
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#7c3aed,#4f46e5)!important;
  border:none!important;padding:14px!important;font-size:16px!important}
.stButton>button[kind="primary"]:hover{background:linear-gradient(135deg,#6d28d9,#4338ca)!important}
.stProgress>div>div>div>div{background:linear-gradient(90deg,#7c3aed,#4ade80)!important}
div[data-testid="metric-container"]{
  background:#111827;border:1px solid #1e293b;border-radius:12px;padding:14px 18px}
div[data-testid="metric-container"] label{color:#64748b!important;font-size:11px!important;text-transform:uppercase;letter-spacing:.08em}
div[data-testid="metric-container"] div[data-testid="stMetricValue"]{color:#f1f5f9!important;font-size:1.5rem!important;font-weight:800!important}
.input-hero{background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #334155;border-radius:16px;padding:28px 32px;margin-bottom:24px}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:#7c3aed20;border:1px solid #7c3aed40;border-radius:20px;padding:6px 14px;font-size:12px;color:#a78bfa;font-weight:600;letter-spacing:.05em;margin-bottom:16px}
.how-it-works{background:#0d1117;border:1px solid #1e293b;border-radius:12px;padding:20px 24px;margin-top:16px}
.step{display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #1e293b}
.step:last-child{border-bottom:none}
.step-num{background:#7c3aed;color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;flex-shrink:0}
</style>
""", unsafe_allow_html=True)

# ── Sidebar: config only ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.divider()

    st.markdown("**🦙 Ollama Settings**")
    ollama_host  = st.text_input(
        "Ollama Host",
        value=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        help="Where Ollama is running. Default is localhost."
    )
    ollama_model = st.selectbox(
        "Model",
        ["llama3.2", "llama3.1:8b", "mistral:7b", "phi3:mini", "llama3:latest"],
        index=0,
        help="llama3.2 is fast (3B). llama3.1:8b is higher quality."
    )

    st.divider()
    st.markdown("**⚖️ Scoring Weights**")
    st.caption("How much each dimension counts toward the final score")
    w_team    = st.slider("👥 Team",         0.0, 1.0, 0.25, 0.05)
    w_market  = st.slider("📊 Market",       0.0, 1.0, 0.20, 0.05)
    w_product = st.slider("🚀 Product",      0.0, 1.0, 0.20, 0.05)
    w_fin     = st.slider("💰 Financials",   0.0, 1.0, 0.15, 0.05)
    w_comp    = st.slider("🔍 Competitive",  0.0, 1.0, 0.10, 0.05)
    w_risk    = st.slider("⚠️ Risk",         0.0, 1.0, 0.10, 0.05)
    total_w = w_team + w_market + w_product + w_fin + w_comp + w_risk
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"Weights sum to {total_w:.2f} (ideally 1.0)")

    st.divider()
    st.markdown("**📋 Setup**")
    st.code("ollama pull llama3.2\nollama serve", language="bash")
    st.caption("Run these commands to start Ollama before using this app.")

# ── Main: Hero input section ──────────────────────────────────────────────────
st.markdown("# 🏦 AI VC Due Diligence")
st.markdown("**Enter any startup below — our AI agent team will analyse it and predict if it's worth investing in.**")

st.markdown("""
<div class="input-hero">
  <div class="hero-badge">🤖 Multi-Agent AI Analysis · Powered by Ollama · 100% Local</div>
  <p style="color:#94a3b8;margin:0;font-size:14px">
    Type the name of any startup — real or fictional, early stage or growth.
    The AI agents will research it, score it across 6 dimensions, and give you a clear
    <strong style="color:#4ade80">INVEST</strong> /
    <strong style="color:#fbbf24">HOLD</strong> /
    <strong style="color:#f87171">PASS</strong> verdict.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Input form ────────────────────────────────────────────────────────────────
with st.form(key="startup_form", clear_on_submit=False):
    st.markdown("### 🔍 Enter Startup Details")

    startup_name = st.text_input(
        "Startup Name *",
        placeholder="e.g.  Stripe   or   My AI Health App   or   GreenRoute",
        help="Enter any startup name — it doesn't have to be a real company."
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        description = st.text_area(
            "What does this startup do? (recommended)",
            placeholder=(
                "e.g. B2B SaaS platform that automates HR onboarding using AI.\n"
                "Founded 2023. $500K ARR. Team of 5. Targeting US SMBs."
            ),
            height=110,
            help="The more context you give, the better the analysis. "
                 "Include: what it does, stage, ARR, team background, target market."
        )
    with col2:
        startup_url = st.text_input(
            "Website URL (optional)",
            placeholder="https://mystartup.com",
            help="If provided, agents will scrape the site for extra context."
        )
        mode = st.selectbox(
            "Analysis Mode",
            ["full", "quick", "market-only", "team-only"],
            index=0,
            help=(
                "full = all 7 agents (~5 min)\n"
                "quick = 3 agents, faster (~2 min)\n"
                "market-only = just market analysis\n"
                "team-only = just team analysis"
            )
        )

    deck_file = st.file_uploader(
        "📄 Upload Pitch Deck PDF (optional)",
        type=["pdf"],
        help="Agents will extract text from the deck for deeper analysis."
    )

    st.markdown("")
    submitted = st.form_submit_button(
        "🚀 Analyse This Startup",
        type="primary",
        use_container_width=True
    )

# ── How it works (shown before run) ──────────────────────────────────────────
if not submitted:
    st.markdown("---")
    st.markdown("""
    <div class="how-it-works">
      <h4 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px">How It Works</h4>
      <div class="step"><div class="step-num">1</div><div style="color:#cbd5e1;font-size:13px">You type any startup name + optional description above</div></div>
      <div class="step"><div class="step-num">2</div><div style="color:#cbd5e1;font-size:13px">6 AI agents analyse Market · Team · Product · Financials · Competition · Risk <strong style="color:#7c3aed">in parallel</strong></div></div>
      <div class="step"><div class="step-num">3</div><div style="color:#cbd5e1;font-size:13px">Investment Committee agent combines scores into a weighted verdict</div></div>
      <div class="step"><div class="step-num">4</div><div style="color:#cbd5e1;font-size:13px">You get a full dashboard: scores, insights, bull/bear case, diligence questions</div></div>
      <div class="step"><div class="step-num">5</div><div style="color:#cbd5e1;font-size:13px">Download the HTML report, Markdown memo, or raw JSON</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.info("**Try:** Stripe")
    col2.info("**Try:** My AI fitness app for seniors")
    col3.info("**Try:** B2B SaaS for restaurant inventory")
    st.stop()  # Stop here until form is submitted

# ── Validation ────────────────────────────────────────────────────────────────
if not startup_name or not startup_name.strip():
    st.error("⚠️ Please enter a startup name above and click 'Analyse This Startup'.")
    st.stop()

startup_name = startup_name.strip()

# ── Setup ─────────────────────────────────────────────────────────────────────
deck_path = None
if deck_file:
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(deck_file.read())
        deck_path = tmp.name

settings = Settings()
settings.ollama_host  = ollama_host
settings.ollama_model = ollama_model
settings.scoring_weights = {
    "team": w_team, "market": w_market, "product": w_product,
    "financials": w_fin, "competitive": w_comp, "risk": w_risk
}

try:
    settings.validate()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

# ── Analysis running ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"## 🔍 Analysing: **{startup_name}**")
if description:
    st.caption(f"Context: {description[:120]}{'…' if len(description)>120 else ''}")

# Live agent status pills
st.markdown("### ⚡ Live Agent Pipeline")
AGENTS = ["market", "team", "product", "financials", "competitive", "risk", "committee"]
ICONS  = {
    "market": "📊", "team": "👥", "product": "🚀",
    "financials": "💰", "competitive": "🔍", "risk": "⚠️", "committee": "🏦"
}
LABELS = {
    "market":"Market","team":"Team","product":"Product",
    "financials":"Finance","competitive":"Compete","risk":"Risk","committee":"Committee"
}

pill_cols   = st.columns(len(AGENTS))
agent_slots = {}
for a, col in zip(AGENTS, pill_cols):
    with col:
        agent_slots[a] = st.empty()

def draw_pill(agent, state):
    icon  = ICONS.get(agent, "🤖")
    label = LABELS.get(agent, agent)
    styles = {
        "pending": ("#334155", "pending",   "#1e293b"),
        "running": ("#f59e0b", "running…",  "#451a0320"),
        "done":    ("#4ade80", "✅ done",    "#14532d20"),
        "error":   ("#f87171", "⚠️ error",   "#1f050520"),
    }
    color, status_label, bg = styles.get(state, styles["pending"])
    agent_slots[agent].markdown(
        f'<div style="background:{bg};border:1px solid {color};border-radius:10px;'
        f'padding:10px 6px;text-align:center">'
        f'<div style="font-size:20px">{icon}</div>'
        f'<div style="color:{color};font-size:10px;font-weight:700;text-transform:uppercase;margin-top:4px">{label}</div>'
        f'<div style="color:{color};font-size:9px;margin-top:2px">{status_label}</div></div>',
        unsafe_allow_html=True
    )

for a in AGENTS:
    draw_pill(a, "pending")

phase_slot = st.empty()
log_slot   = st.empty()
progress   = st.progress(0, text="Starting pipeline…")
phase_pct  = {1: 0.05, 2: 0.30, 3: 0.70, 4: 0.85, 5: 1.0}
log_lines  = []
ev_queue   = queue.Queue()
report_holder, error_holder = [None], [None]

def on_event(ev):
    ev_queue.put(ev)

def run_pipeline():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        pl = DueDiligencePipeline(settings, on_event=on_event)
        report_holder[0] = loop.run_until_complete(
            pl.run(
                startup_name=startup_name,
                description=description or "",
                url=startup_url or None,
                deck_path=deck_path,
                mode=mode,
            )
        )
    except Exception as ex:
        error_holder[0] = str(ex)
    finally:
        ev_queue.put({"event": "__done__", "data": {}, "ts": ""})

threading.Thread(target=run_pipeline, daemon=True).start()

# Consume events
while True:
    try:
        ev = ev_queue.get(timeout=0.3)
    except queue.Empty:
        continue
    if ev["event"] == "__done__":
        break

    e, d = ev["event"], ev["data"]
    if e == "phase":
        pct = phase_pct.get(d["phase"], 0)
        progress.progress(pct, text=f"Phase {d['phase']}/5: {d['label']}")
        phase_slot.markdown(f"**⏳ {d['label']}…**")
    elif e == "agent_start":
        draw_pill(d["agent"], "running")
    elif e == "agent_done":
        draw_pill(d["agent"], "done")
    elif e == "agent_error":
        draw_pill(d["agent"], "error")
        log_lines.append(f"⚠️ {d['agent']}: {d['error'][:60]}")
    elif e == "log":
        log_lines.append(f"ℹ️ {d['msg']}")

    if log_lines:
        log_slot.markdown(" · ".join(f"`{l}`" for l in log_lines[-3:]))

progress.progress(1.0, text="✅ Analysis complete!")
phase_slot.markdown("**✅ All agents finished!**")

if error_holder[0]:
    st.error(f"Pipeline error: {error_holder[0]}")
    st.stop()

report = report_holder[0]
if not report:
    st.error("No report was generated. Check Ollama is running.")
    st.stop()

# ── Results ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"## 📊 Results for **{startup_name}**")

score     = report.get("overall_score", 0)
verdict   = report.get("verdict", "N/A")
worth     = report.get("worth_investing", False)
committee = report.get("committee", {}) or {}
agents    = report.get("agent_results", {}) or {}

# ── Verdict banner ────────────────────────────────────────────────────────────
vc_colors = {
    "STRONG INVEST": ("#00ff87","#00ff8715"),
    "INVEST":        ("#4ade80","#4ade8015"),
    "CONDITIONAL INVEST": ("#fbbf24","#fbbf2415"),
    "HOLD":          ("#fb923c","#fb923c15"),
    "PASS":          ("#f87171","#f8717115"),
}
vc_col, vc_bg = vc_colors.get(str(verdict).upper().strip(), ("#94a3b8","#94a3b815"))
score_col = "#4ade80" if float(score or 0)>=7 else "#fbbf24" if float(score or 0)>=5 else "#f87171"

st.markdown(f"""
<div style="background:{vc_bg};border:2px solid {vc_col};border-radius:16px;
     padding:28px;text-align:center;margin:20px 0">
  <div style="font-size:13px;letter-spacing:.2em;color:{vc_col};opacity:.8;margin-bottom:8px;text-transform:uppercase">
    Investment Verdict for {startup_name}
  </div>
  <div style="font-size:3rem;font-weight:900;color:{vc_col};letter-spacing:-.02em">{verdict}</div>
  <div style="margin-top:16px;font-size:1.2rem;color:{'#4ade80' if worth else '#f87171'};font-weight:700">
    {'✅ WORTH INVESTING' if worth else '❌ NOT WORTH INVESTING'} &nbsp;·&nbsp;
    <span style="color:{score_col}">Score: {score}/10</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Key metrics ───────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Overall Score",   f"{score}/10")
m2.metric("Conviction",      str(committee.get("conviction","N/A") or "N/A").title())
m3.metric("Round Stage",     str(committee.get("round_stage","N/A") or "N/A"))
m4.metric("Recommended Check", str(committee.get("check_size_recommended","N/A") or "N/A"))

# ── Tabbed results ────────────────────────────────────────────────────────────
def sc(v):
    try: v = float(v or 0)
    except: v = 0
    return "🟢" if v >= 7 else "🟡" if v >= 5 else "🔴"

tabs = st.tabs([
    "📋 Overview", "📊 Market", "👥 Team", "🚀 Product",
    "💰 Financials", "🔍 Competition", "⚠️ Risk", "📄 Full Report"
])

# Overview
with tabs[0]:
    st.markdown(f"### 📋 {startup_name} — Overview")
    bd = committee.get("score_breakdown", {}) or {}
    if bd:
        st.markdown("**Score Breakdown:**")
        for k, v in bd.items():
            c1, c2 = st.columns([4, 1])
            c1.progress(min(float(v or 0)/10, 1.0), text=f"{sc(v)} {k.title()} — {v}/10")
    st.markdown("---")
    st.markdown("**📝 Executive Summary**")
    st.info(str(committee.get("summary", "No summary available.") or "No summary."))
    c1, c2 = st.columns(2)
    c1.success(f"🐂 **Bull Case:**\n\n{committee.get('bull_case','')}")
    c2.error(f"🐻 **Bear Case:**\n\n{committee.get('bear_case','')}")
    if committee.get("investment_thesis"):
        st.markdown(f"**💡 Investment Thesis:** {committee['investment_thesis']}")
    if committee.get("key_questions"):
        st.markdown("**❓ Key Diligence Questions:**")
        for q in committee["key_questions"]: st.markdown(f"- {q}")
    if committee.get("next_steps"):
        st.markdown("**🔜 Next Steps:**")
        for s in committee["next_steps"]: st.markdown(f"- → {s}")

# Market
with tabs[1]:
    m = agents.get("market", {}) or {}
    if m and not m.get("error"):
        st.markdown(f"### 📊 Market Analysis — Score: {sc(m.get('overall_market_score'))} {m.get('overall_market_score','?')}/10")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("TAM", f"${m.get('tam_usd_billions','?')}B")
        c2.metric("SAM", f"${m.get('sam_usd_billions','?')}B")
        c3.metric("CAGR", f"{m.get('cagr_pct','?')}%")
        c4.metric("Market Score", f"{m.get('overall_market_score','?')}/10")
        if m.get("ai_insight"):
            st.info(f"🧠 **AI Insight:** {m['ai_insight']}")
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**🔥 Key Trends:**")
            for t in (m.get("key_trends") or []): st.markdown(f"- {t}")
        with cb:
            st.markdown("**⚠️ Market Risks:**")
            for r in (m.get("market_risks") or []): st.markdown(f"- {r}")
        if m.get("summary"): st.caption(m["summary"])
    else:
        st.warning("Market analysis not available for this startup.")

# Team
with tabs[2]:
    t = agents.get("team", {}) or {}
    if t and not t.get("error"):
        st.markdown(f"### 👥 Team Analysis — Score: {sc(t.get('overall_team_score'))} {t.get('overall_team_score','?')}/10")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Team Score",    f"{t.get('overall_team_score','?')}/10")
        c2.metric("Execution",     f"{t.get('execution_score','?')}/10")
        c3.metric("Domain Exp.",   f"{t.get('domain_expertise_score','?')}/10")
        c4.metric("Risk Level",    str(t.get("risk_level","?") or "?").upper())
        if t.get("ai_insight"):
            st.info(f"🧠 **AI Insight:** {t['ai_insight']}")
        founders = t.get("founders") or []
        if founders:
            st.markdown("**👤 Founders:**")
            for f in founders:
                st.markdown(f"- **{f.get('name','?')}** ({f.get('role','?')}) — {f.get('background','')}"
                            + (f" · 🏆 {f.get('prior_exits',0)} exit(s)" if f.get('prior_exits') else ""))
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**✅ Strengths:**")
            for s in (t.get("key_strengths") or []): st.markdown(f"- {s}")
        with cb:
            st.markdown("**❌ Gaps:**")
            for g in (t.get("key_gaps") or []): st.markdown(f"- {g}")
    else:
        st.warning("Team analysis not available.")

# Product
with tabs[3]:
    p = agents.get("product", {}) or {}
    if p and not p.get("error"):
        pname = str(p.get("product_name") or startup_name)
        tagline = str(p.get("tagline") or "")
        stage = str(p.get("stage") or "?")
        st.markdown(f"### 🚀 {pname}")
        if tagline: st.caption(f"*{tagline}*")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Score",       f"{p.get('overall_product_score','?')}/10")
        c2.metric("PMF",         f"{p.get('pmf_score','?')}/10")
        c3.metric("Innovation",  f"{p.get('innovation_score','?')}/10")
        c4.metric("Stage",       stage.title())
        if p.get("ai_insight"):
            st.info(f"🧠 **AI Insight:** {p['ai_insight']}")
        st.markdown("**⚡ Key Features:**")
        for f in (p.get("key_features") or []): st.markdown(f"- {f}")
        defens = p.get("defensibility") or {}
        if defens:
            ca, cb, cc = st.columns(3)
            ca.metric("IP Protection", str(defens.get("ip","none") or "none").title())
            cb.metric("Network Effects", "Yes ✅" if defens.get("network_effects") else "No ✗")
            cc.metric("Data Moat", "Yes ✅" if defens.get("data_moat") else "No ✗")
    else:
        st.warning("Product analysis not available.")

# Financials
with tabs[4]:
    fin = agents.get("financials", {}) or {}
    if fin and not fin.get("error"):
        def fmt(v):
            try:
                v = float(v)
                return f"${v/1e6:.1f}M" if v>=1e6 else f"${v/1e3:.0f}K" if v>=1e3 else f"${v:.0f}"
            except: return "N/A"
        st.markdown(f"### 💰 Financial Analysis — Score: {sc(fin.get('overall_financial_score'))} {fin.get('overall_financial_score','?')}/10")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("ARR",       fmt(fin.get("arr_usd_estimate")))
        c2.metric("Burn/mo",   fmt(fin.get("burn_rate_monthly_usd")))
        c3.metric("Runway",    f"{fin.get('runway_months','?')} mo")
        c4.metric("Growth",    f"{fin.get('growth_rate_pct','?')}%" if fin.get("growth_rate_pct") else "N/A")
        if fin.get("ai_insight"):
            st.info(f"🧠 **AI Insight:** {fin['ai_insight']}")
        ca, cb = st.columns(2)
        with ca:
            st.metric("LTV:CAC",      f"{fin.get('ltv_cac_ratio','?')}x")
            st.metric("Gross Margin", f"{fin.get('gross_margin_pct','?')}%")
            st.metric("Revenue Model", str(fin.get("revenue_model","?") or "?").title())
        with cb:
            burn = str(fin.get("burn_risk","medium") or "medium")
            bc = "🔴" if burn in ("high","critical") else "🟡" if burn == "medium" else "🟢"
            st.markdown(f"**Burn Risk:** {bc} {burn.upper()}")
            for flag in (fin.get("red_flags") or []):
                st.error(f"🚩 {flag}")
    else:
        st.warning("Financial analysis not available.")

# Competitive
with tabs[5]:
    comp = agents.get("competitive", {}) or {}
    if comp and not comp.get("error"):
        st.markdown(f"### 🔍 Competitive Intelligence — Score: {sc(comp.get('overall_competitive_score'))} {comp.get('overall_competitive_score','?')}/10")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Score",           f"{comp.get('overall_competitive_score','?')}/10")
        c2.metric("Differentiation", f"{comp.get('differentiation_score','?')}/10")
        c3.metric("Moat",            f"{comp.get('moat_score','?')}/10")
        c4.metric("Market Structure", str(comp.get("market_concentration","?") or "?").title())
        if comp.get("ai_insight"):
            st.info(f"🧠 **AI Insight:** {comp['ai_insight']}")
        competitors = comp.get("direct_competitors") or []
        if competitors:
            import pandas as pd
            st.markdown("**Competitor Matrix:**")
            st.dataframe(pd.DataFrame([{
                "Company":  x.get("name","?"),
                "Strength": x.get("strength",""),
                "Weakness": x.get("weakness",""),
                "Stage":    x.get("stage","?"),
                "Threat":   str(x.get("threat","?")).upper()
            } for x in competitors]), use_container_width=True)
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**💡 White Space:**")
            for w in (comp.get("white_space") or []): st.markdown(f"- {w}")
        with cb:
            st.markdown("**⚠️ Risks:**")
            for r in (comp.get("competitive_risks") or []): st.markdown(f"- {r}")
    else:
        st.warning("Competitive analysis not available.")

# Risk
with tabs[6]:
    risk = agents.get("risk", {}) or {}
    if risk and not risk.get("error"):
        st.markdown(f"### ⚠️ Risk Assessment — Score: {sc(risk.get('overall_risk_score'))} {risk.get('overall_risk_score','?')}/10")
        c1, c2 = st.columns(2)
        c1.metric("Risk Score",      f"{risk.get('overall_risk_score','?')}/10")
        c2.metric("Return Potential", str(risk.get("risk_adjusted_return","?") or "?").title())
        if risk.get("ai_insight"):
            st.info(f"🧠 **AI Insight:** {risk['ai_insight']}")
        for cat, label in [
            ("regulatory_risks","🏛️ Regulatory"),
            ("technology_risks","💻 Technology"),
            ("market_risks","📉 Market"),
            ("operational_risks","⚙️ Operational")
        ]:
            items = risk.get(cat) or []
            if items:
                st.markdown(f"**{label} Risks:**")
                for r in items:
                    sev = str(r.get("severity","?") or "?")
                    icon = "🔴" if sev in ("high","critical") else "🟡" if sev=="medium" else "🟢"
                    st.markdown(f"- {icon} **{sev.upper()}:** {r.get('risk','?')}"
                                + (f" · *Mitigation: {r['mitigation']}*" if r.get("mitigation") else ""))
    else:
        st.warning("Risk analysis not available.")

# Full Report
with tabs[7]:
    st.markdown(report.get("markdown_report", ""))
    st.divider()
    ca, cb, cc = st.columns(3)
    ca.download_button(
        "⬇️ HTML Dashboard",
        data=report.get("html_report", ""),
        file_name=f"{startup_name.replace(' ','_')}_report.html",
        mime="text/html",
        use_container_width=True
    )
    cb.download_button(
        "⬇️ Markdown Memo",
        data=report.get("markdown_report", ""),
        file_name=f"{startup_name.replace(' ','_')}_report.md",
        mime="text/markdown",
        use_container_width=True
    )
    cc.download_button(
        "⬇️ JSON Data",
        data=json.dumps(report, indent=2, default=str),
        file_name=f"{startup_name.replace(' ','_')}_report.json",
        mime="application/json",
        use_container_width=True
    )

# Save to disk
out = Path("data/outputs")
out.mkdir(parents=True, exist_ok=True)
safe = startup_name.replace(" ", "_")
(out / f"{safe}_report.html").write_text(report.get("html_report",""), encoding="utf-8")
(out / f"{safe}_report.json").write_text(json.dumps(report, indent=2, default=str))
st.success(f"✅ Reports saved to **data/outputs/{safe}_report.html**")
