"""
LangGraph Research Pipeline
────────────────────────────
State machine that connects all agents into a full agentic workflow:

  planner
    ├─ search_A (parallel)
    ├─ search_B (parallel)
    └─ search_C (parallel)
         └─ summarizer
              └─ critic
                   ├─ [score < 6]  optimizer ──► planner  (loop, max 3 retries)
                   └─ [score >= 6] report_writer
                                        └─ notify ──► END
"""
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

from agents.planner       import planner_node
from agents.searcher      import search_A_node, search_B_node, search_C_node
from agents.summarizer    import summarizer_node
from agents.critic        import critic_node
from agents.optimizer     import optimizer_node
from agents.report_writer import report_writer_node
from agents.notifier      import notifier_node


# ── Shared state definition ──────────────────────────────────────────────────

class ResearchState(TypedDict):
    # Input
    original_query:   str
    # Planner outputs
    sub_topics:       List[str]
    refined_query:    str
    # Search outputs  (accumulated by all 3 search agents)
    raw_results:      List[dict]
    # Summarizer output
    summary:          str
    # Critic outputs
    quality_score:    float
    quality_feedback: str
    # Control flow
    retry_count:      int
    # Final outputs
    final_report:     str
    output_file:      Optional[str]


# ── Routing function (evaluator-optimizer pattern) ───────────────────────────

def route_after_critic(state: ResearchState) -> str:
    """
    Route based on quality score.
    - score >= 6  → write the report
    - score <  6  → optimize query and retry (max 3 times)
    - retries >= 3 → force write report regardless
    """
    retries = state.get("retry_count", 0)
    score   = state.get("quality_score", 0.0)

    if retries >= 3:
        print(f"[Router] Max retries ({retries}) reached — forcing report generation.")
        return "write_report"

    if score >= 6.0:
        print(f"[Router] Score {score}/10 — quality passed, writing report.")
        return "write_report"

    print(f"[Router] Score {score}/10 — quality insufficient, optimizing (retry {retries+1}/3).")
    return "optimize"


# ── Graph construction ────────────────────────────────────────────────────────

def build_graph():
    g = StateGraph(ResearchState)

    # Register all nodes
    g.add_node("planner",       planner_node)
    g.add_node("search_A",      search_A_node)
    g.add_node("search_B",      search_B_node)
    g.add_node("search_C",      search_C_node)
    g.add_node("summarizer",    summarizer_node)
    g.add_node("critic",        critic_node)
    g.add_node("optimizer",     optimizer_node)
    g.add_node("report_writer", report_writer_node)
    g.add_node("notify",        notifier_node)

    # Entry point
    g.set_entry_point("planner")

    # Planner → parallel search agents
    g.add_edge("planner", "search_A")
    g.add_edge("planner", "search_B")
    g.add_edge("planner", "search_C")

    # All 3 search agents → summarizer (fan-in)
    g.add_edge("search_A",   "summarizer")
    g.add_edge("search_B",   "summarizer")
    g.add_edge("search_C",   "summarizer")

    # Linear chain through critic
    g.add_edge("summarizer", "critic")

    # Conditional routing from critic (evaluator-optimizer loop)
    g.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "optimize":    "optimizer",
            "write_report": "report_writer",
        },
    )

    # Optimizer loops back to planner with refined query
    g.add_edge("optimizer", "planner")

    # Report writer → notify → end
    g.add_edge("report_writer", "notify")
    g.add_edge("notify",        END)

    return g.compile()


# ── Default initial state helper ─────────────────────────────────────────────

def make_initial_state(query: str) -> ResearchState:
    return {
        "original_query":   query,
        "sub_topics":       [],
        "refined_query":    "",
        "raw_results":      [],
        "summary":          "",
        "quality_score":    0.0,
        "quality_feedback": "",
        "retry_count":      0,
        "final_report":     "",
        "output_file":      None,
    }
