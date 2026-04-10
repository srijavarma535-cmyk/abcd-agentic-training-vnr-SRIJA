import json
from langchain_core.prompts import ChatPromptTemplate
from config.models import planner_llm

PLANNER_PROMPT = ChatPromptTemplate.from_template("""
You are an expert research planning agent.
Break this research topic into exactly 3 specific, distinct, searchable sub-topic queries.

Original query       : {original_query}
Refined focus        : {refined_query}
Critic feedback      : {quality_feedback}

Return ONLY valid JSON, no markdown, no explanation:
{{"sub_topics": ["query_string_1", "query_string_2", "query_string_3"]}}
""")

def planner_node(state: dict) -> dict:
    chain = PLANNER_PROMPT | planner_llm
    result = chain.invoke({
        "original_query":   state.get("original_query", ""),
        "refined_query":    state.get("refined_query", "none"),
        "quality_feedback": state.get("quality_feedback", "none - first attempt"),
    })
    try:
        parsed = json.loads(result.content)
        sub_topics = parsed.get("sub_topics", [])
    except Exception:
        q = state.get("original_query", "research topic")
        sub_topics = [q, f"{q} latest developments", f"{q} analysis and impact"]
    print(f"[Planner] Sub-topics: {sub_topics}")
    return {**state, "sub_topics": sub_topics, "raw_results": []}
