<<<<<<< HEAD
# abcd-agentic-training-vnr-SRIJA
=======
# AI Research Analyst Agent

A fully agentic, multi-model research pipeline built on LangGraph, LangChain,
CrewAI patterns, Serper web search, Pushover notifications, Docker, and LangSmith tracing.

---

## What it does

1. **Planner agent** breaks your query into 3 specific sub-topics
2. **3 Search agents** run in parallel using Serper (Google Search API)
3. **Summarizer agent** (Claude) synthesises all findings
4. **Critic agent** scores research quality 0–10
5. **Optimizer agent** refines the query if score < 6 (loops back, max 3 retries)
6. **Report Writer agent** (Claude) writes a full professional Markdown report
7. **Notifier** saves the report to `/outputs/` and sends a Pushover push notification

---

## Course concepts covered

| Concept | Where |
|---|---|
| Docker | Dockerfile, docker-compose.yml |
| LLMs / Transformers | Every agent (GPT-4o + Claude) |
| Tokenization | All LLM inputs |
| MCP pattern (tools) | serper_tool.py, pushover_tool.py |
| Credentials | .env file |
| LangChain | Prompts, chains, tool wrappers |
| LangGraph | graph/research_graph.py — full state machine |
| LangSmith | Auto-tracing via env vars |
| Multi-model (Lab 3) | 3 models: GPT-4o, GPT-4o-mini, Claude Sonnet |
| Parallelization | search_A / search_B / search_C run concurrently |
| Orchestrator-worker | Planner orchestrates 3 search workers |
| Evaluator-optimizer | Critic scores → Optimizer refines → loop (max 3) |
| Prompt chaining | Query → sub-topics → search → summary → report |
| Routing | route_after_critic() conditional edge |
| Tracing | LangSmith dashboard — every LLM call logged |
| Pushover | notifier.py sends completion alert |
| Serper | searcher.py — live web search per sub-topic |

---

## Setup

### 1. Prerequisites
- Docker + Docker Compose  (for Docker mode)
- Python 3.11+             (for local mode)
- API keys (see step 2)

### 2. Get API keys

| Service | URL | Free tier |
|---|---|---|
| OpenAI | https://platform.openai.com | Pay per use |
| Anthropic | https://console.anthropic.com | Pay per use |
| Serper | https://serper.dev | 2,500 free searches |
| Pushover | https://pushover.net | 7-day free trial |
| LangSmith | https://smith.langchain.com | Free tier available |

### 3. Configure environment

```bash
copy env.example .env
# Edit .env and fill in all your API keys
```

---

## Run with Docker (recommended)

```bash
# Build and start
docker-compose up --build

# Test via API
curl -X POST http://localhost:8080/research \
  -H "Content-Type: application/json" \
  -d '{"query": "impact of AI on software engineering in 2025"}'

# Health check
curl http://localhost:8080/health
```

---

## Run locally (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run CLI
python main.py "future of quantum computing"

# Run API server
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

---

## API Reference

### POST /research
```json
// Request
{ "query": "your research topic" }

// Response
{
  "query": "your research topic",
  "quality_score": 7.8,
  "retries": 1,
  "output_file": "outputs/report_your_topic_20250409_143022.md",
  "report": "# Full Markdown Report..."
}
```

### GET /health
```json
{ "status": "ok", "agent": "AI Research Analyst" }
```

---

## Output

Every completed report is saved to the `outputs/` folder as a `.md` file:
```
outputs/
  report_impact_of_AI_on_healthcare_20250409_143022.md
  report_future_of_quantum_computing_20250409_151844.md
```

---

## LangSmith Tracing

Once `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` are set in `.env`,
every run is automatically traced at:

https://smith.langchain.com → Project: **ai-research-analyst**

You can see every LLM call, token count, latency, agent input/output, and the
full evaluator-optimizer retry loop visually.

---

## Project Structure

```
ai_research_analyst/
├── Dockerfile
├── docker-compose.yml
├── env.example             ← copy to .env and fill keys
├── requirements.txt
├── main.py                  ← FastAPI app + CLI entry point
├── graph/
│   └── research_graph.py    ← LangGraph state machine
├── agents/
│   ├── planner.py           ← breaks query into 3 sub-topics
│   ├── searcher.py          ← 3 parallel Serper search agents
│   ├── summarizer.py        ← Claude synthesis agent
│   ├── critic.py            ← quality scorer (evaluator)
│   ├── optimizer.py         ← query refiner (optimizer)
│   ├── report_writer.py     ← Claude report writer
│   └── notifier.py          ← saves file + Pushover alert
├── tools/
│   ├── serper_tool.py       ← web_search tool (MCP pattern)
│   └── pushover_tool.py     ← send_pushover_alert tool
├── config/
│   └── models.py            ← multi-model assignments
└── outputs/                 ← generated reports saved here
```

---

## Troubleshooting

**`SERPER_API_KEY not set`** — copy `env.example` to `.env` and add your Serper key.

**`AuthenticationError: OpenAI`** — check your `OPENAI_API_KEY` in `.env`.

**`No module named langchain_anthropic`** — run `pip install -r requirements.txt` again.

**LangSmith not tracing** — ensure both `LANGCHAIN_TRACING_V2=true` and `LANGCHAIN_API_KEY` are set.

**Pushover not sending** — both `PUSHOVER_USER_KEY` and `PUSHOVER_APP_TOKEN` must be set. The pipeline continues even if Pushover fails.
>>>>>>> 29fb880 (Initial commit:ai_research_analysis)
