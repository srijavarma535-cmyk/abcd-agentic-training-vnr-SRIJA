"""
AI Research Analyst Agent — Entry Point
────────────────────────────────────────
Run modes:
  1. API server (default):  uvicorn main:app --host 0.0.0.0 --port 8080
  2. CLI:                   python main.py "your research topic here"
  3. Docker:                docker-compose up --build

LangSmith tracing activates automatically via .env:
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=...
  LANGCHAIN_PROJECT=ai-research-analyst
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()  # Load .env before any LangChain imports

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from graph.research_graph import build_graph, make_initial_state

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Research Analyst Agent",
    description="Multi-agent research pipeline: Planner → Search (parallel) → Summarizer → Critic → Optimizer → Report Writer → Pushover",
    version="1.0.0",
)

# Build graph once at startup
graph = build_graph()


class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    query:         str
    quality_score: float
    retries:       int
    output_file:   str
    report:        str


@app.get("/", response_class=PlainTextResponse)
async def root():
    return (
        "AI Research Analyst Agent is running.\n\n"
        "POST /research   { \"query\": \"your topic\" }\n"
        "GET  /health     health check\n"
    )


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "AI Research Analyst"}


@app.post("/research", response_model=ResearchResponse)
async def run_research(req: ResearchRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    print(f"\n{'='*60}")
    print(f"[API] New research request: {req.query}")
    print(f"{'='*60}\n")

    try:
        state  = make_initial_state(req.query.strip())
        result = graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    return ResearchResponse(
        query         = req.query,
        quality_score = round(result.get("quality_score", 0.0), 1),
        retries       = result.get("retry_count", 0),
        output_file   = result.get("output_file", ""),
        report        = result.get("final_report", ""),
    )


# ── CLI mode ──────────────────────────────────────────────────────────────────

def run_cli(query: str):
    print(f"\n{'='*60}")
    print(f" AI Research Analyst Agent")
    print(f"{'='*60}")
    print(f" Query: {query}")
    print(f"{'='*60}\n")

    state  = make_initial_state(query)
    result = graph.invoke(state)

    print(f"\n{'='*60}")
    print(result.get("final_report", "No report generated."))
    print(f"\n{'='*60}")
    print(f" Quality Score : {round(result.get('quality_score', 0), 1)} / 10")
    print(f" Retries       : {result.get('retry_count', 0)}")
    print(f" Saved to      : {result.get('output_file', 'N/A')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your research topic\"")
        print("Example: python main.py \"impact of AI on healthcare in 2025\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    run_cli(query)
