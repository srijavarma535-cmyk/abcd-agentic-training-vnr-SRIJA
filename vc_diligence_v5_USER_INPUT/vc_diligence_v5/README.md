# 🏦 AI VC Due Diligence Agent Team v5
### ⚡ Ollama-powered · 100% Local · Real-time Streaming · Bloomberg-dark Dashboard

---

## 🚀 Quick Start

### Step 1 — Install Ollama
Download from https://ollama.com/download then:
```bash
ollama pull llama3.2
ollama serve
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run
```bash
# CLI
python main.py --startup "Stripe" --mode full

# Web UI
streamlit run ui/app.py
```

---

## 📁 Structure
```
vc_diligence_v5/
├── main.py                    ← CLI entry point (auto-opens HTML report)
├── requirements.txt
├── Makefile
├── agents/
│   ├── base_agent.py          ← Ollama REST caller (stdlib urllib only)
│   ├── market_agent.py
│   ├── team_agent.py
│   ├── product_agent.py
│   ├── financial_agent.py
│   ├── competitive_agent.py
│   ├── risk_agent.py
│   └── committee_agent.py
├── orchestrator/
│   └── pipeline.py            ← Async orchestrator with streaming callbacks
├── tools/
│   ├── html_generator.py      ← Bloomberg-dark dashboard HTML
│   ├── report_generator.py    ← Markdown memo
│   ├── web_scraper.py
│   └── pdf_parser.py
├── ui/
│   └── app.py                 ← Streamlit real-time streaming UI
├── config/
│   └── settings.py
├── data/outputs/              ← Reports saved here
└── tests/
    └── test_agents.py         ← Mocked unit tests (no Ollama needed)
```

---

## ⚙️ Modes
| Mode | Agents | Time (approx) |
|------|--------|--------------|
| full | All 7 | ~2–5 min |
| quick | Market+Team+Product | ~1–2 min |
| market-only | Market | ~15–30s |
| team-only | Team | ~15–30s |

---

## 🏗️ Architecture
```
Input → Orchestrator → [Market|Team|Product|Financial|Competitive] (parallel)
                     → Risk Agent (uses prior summaries)
                     → Committee Agent (weighted score + verdict)
                     → HTML Dashboard + Markdown + JSON
```

---

## 🧪 Testing
```bash
pytest tests/ -v   # no Ollama needed — all mocked
```
