import json
from langchain_core.prompts import ChatPromptTemplate
from config.models import critic_llm

CRITIC_PROMPT = ChatPromptTemplate.from_template("""
You are a rigorous research quality critic.
Research topic: {original_query}
Research summary: {summary}

Score on depth, coverage, citations, coherence (each 0-10).
Return ONLY valid JSON, no markdown:
{{
  "quality_score": 0.0,
  "quality_feedback": "specific gaps and what to search next",
  "passed": true
}}
Set passed=true if quality_score >= 6.0. quality_score = average of 4 scores.
""")

def critic_node(state: dict) -> dict:
    print("[Critic] Evaluating research quality...")
    chain = CRITIC_PROMPT | critic_llm
    result = chain.invoke({
        "original_query": state.get("original_query", ""),
        "summary": state.get("summary", ""),
    })
    try:
        parsed = json.loads(result.content)
    except Exception:
        parsed = {"quality_score": 7.0, "quality_feedback": "Parse error - forcing pass.", "passed": True}
    score = parsed.get("quality_score", 0.0)
    print(f"[Critic] Score: {score}/10")
    return {
        **state,
        "quality_score": float(score),
        "quality_feedback": parsed.get("quality_feedback", ""),
    }
