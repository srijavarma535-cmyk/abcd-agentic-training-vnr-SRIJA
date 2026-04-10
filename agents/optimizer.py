from langchain_core.prompts import ChatPromptTemplate
from config.models import optimizer_llm

OPTIMIZER_PROMPT = ChatPromptTemplate.from_template("""
The critic rated this research {quality_score}/10 with feedback:
{quality_feedback}

Original query: {original_query}

Generate a refined, more specific research query that addresses the gaps.
Return ONLY the refined query string, nothing else.
""")

def optimizer_node(state: dict) -> dict:
    retry = state.get("retry_count", 0) + 1
    print(f"[Optimizer] Retry #{retry} - refining query...")
    chain = OPTIMIZER_PROMPT | optimizer_llm
    result = chain.invoke({
        "quality_score": state.get("quality_score", 0),
        "quality_feedback": state.get("quality_feedback", ""),
        "original_query": state.get("original_query", ""),
    })
    refined = result.content.strip().strip('"').strip("'")
    print(f"[Optimizer] Refined query: {refined}")
    return {**state, "refined_query": refined, "retry_count": retry, "raw_results": [], "summary": ""}
