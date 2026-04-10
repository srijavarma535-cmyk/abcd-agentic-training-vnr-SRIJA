# 🏦 AI VC Due Diligence Agent Team
### ⚡ 100% FREE — Powered by Google Gemini (1500 requests/day, no credit card)

A production-ready **multi-agent system** for venture capital due diligence.
Seven specialist AI agents analyze a startup in parallel, then synthesize a full investment memo.

---

## 🆓 Why It's Free

This project uses **Google Gemini 1.5 Flash** which has a permanent free tier:
- ✅ **1,500 API calls/day** — free forever
- ✅ **No credit card needed**
- ✅ **Get key in 30 seconds** at https://aistudio.google.com/app/apikey

---

## 🚀 Quick Start (3 steps)

### Step 1 — Get Free API Key
Go to **https://aistudio.google.com/app/apikey** → Sign in with Google → Create API Key

### Step 2 — Install
```bash
pip install -r requirements.txt
```

### Step 3 — Run
```cmd
# Windows CMD
set GEMINI_API_KEY=AIza...your_key_here...
python main.py --startup "Stripe" --mode full
```

```bash
# Mac / Linux
export GEMINI_API_KEY=AIza...your_key_here...
python main.py --startup "Stripe" --mode full
```

**Or use a .env file (recommended):**
```
# Create .env in the project folder:
GEMINI_API_KEY=AIza...your_key_here...
```
Then just run `python main.py --startup "Stripe"` — it auto-loads the .env.

---

## 🖥️ Web UI (Streamlit)
```bash
streamlit run ui/app.py
```
Open http://localhost:8501 — paste your Gemini key in the sidebar and go.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              DueDiligencePipeline (Orchestrator)    │
└────────┬────────────────────────────────────────────┘
         │
         │  Phase 1 — Data Collection
         │  ├── WebScraper  (URL)
         │  └── PDFParser   (Pitch Deck)
         │
         │  Phase 2 — Parallel Agent Analysis
         ├──► 📊 MarketAnalysisAgent     TAM/SAM/SOM, timing, trends
         ├──► 👥 TeamAnalysisAgent       Founders, gaps, track record
         ├──► 🚀 ProductAnalysisAgent    PMF, moat, scalability
         ├──► 💰 FinancialAnalysisAgent  ARR, burn, unit economics
         ├──► 🔍 CompetitiveIntelAgent   Competitor landscape
         │
         │  Phase 3 — Sequential (needs prior results)
         ├──► ⚠️  RiskAssessmentAgent    Regulatory, tech, macro risks
         │
         │  Phase 4 — Synthesis
         └──► 🏦 InvestmentCommittee    Final memo + verdict
```

---

## 📁 Folder Structure

```
ai_vc_due_diligence/
├── main.py                    ← CLI entry point
├── requirements.txt
├── Makefile
├── .env.example               ← Copy to .env and add your key
├── README.md
├── config/
│   └── settings.py            ← Gemini key, weights, model config
├── agents/
│   ├── base_agent.py          ← Gemini REST API (uses stdlib only)
│   ├── market_agent.py        ← 📊 TAM/SAM/SOM
│   ├── team_agent.py          ← 👥 Founders
│   ├── product_agent.py       ← 🚀 PMF & moat
│   ├── financial_agent.py     ← 💰 Unit economics
│   ├── competitive_agent.py   ← 🔍 Competitors
│   ├── risk_agent.py          ← ⚠️  Risks
│   └── committee_agent.py     ← 🏦 Final verdict
├── orchestrator/
│   └── pipeline.py            ← 4-phase async orchestrator
├── tools/
│   ├── web_scraper.py         ← URL scraping
│   ├── pdf_parser.py          ← Pitch deck parsing
│   └── report_generator.py    ← Markdown memo
├── ui/
│   └── app.py                 ← Streamlit web dashboard
├── data/
│   ├── samples/               ← Sample startup JSON
│   └── outputs/               ← Generated reports
├── tests/
│   ├── test_agents.py         ← Unit tests (no API key needed)
│   └── test_integration.py    ← Live test
└── docs/
    └── AGENT_DESIGN.md
```

---

## ⚙️ Analysis Modes

| Mode | Agents | Speed |
|------|--------|-------|
| `full` | All 7 agents | ~30-60s |
| `quick` | Market+Team+Product | ~15-25s |
| `market-only` | Market only | ~5-10s |
| `team-only` | Team only | ~5-10s |

---

## 🧪 Tests
```bash
# Unit tests (no API key needed — all mocked)
pytest tests/test_agents.py -v

# Live integration test (needs GEMINI_API_KEY)
python tests/test_integration.py
```

---

## 🔑 Environment Variables

| Variable | Required | Where to get |
|----------|----------|--------------|
| `GEMINI_API_KEY` | ✅ Yes (FREE) | https://aistudio.google.com/app/apikey |
| `SERPER_API_KEY` | ❌ Optional (FREE tier) | https://serper.dev |

