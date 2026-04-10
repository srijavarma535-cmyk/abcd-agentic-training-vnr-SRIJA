import json
from langchain_core.prompts import ChatPromptTemplate
from config.models import summarizer_llm

SUMMARIZER_PROMPT = ChatPromptTemplate.from_template("""
You are a world-class research synthesizer.
Research topic: {original_query}
All facts collected: {raw_results}

1. Remove duplicates
2. Group facts by theme with clear headings (##)
3. Keep all source URLs inline as (Source: url)
4. Write 500-700 words comprehensive synthesis
""")

def summarizer_node(state: dict) -> dict:
    raw = state.get("raw_results", [])
    if not raw:
        return {**state, "summary": "No research results were collected."}
    print(f"[Summarizer] Synthesising {len(raw)} facts...")
    chain = SUMMARIZER_PROMPT | summarizer_llm
    result = chain.invoke({
        "original_query": state.get("original_query", ""),
        "raw_results": json.dumps(raw, indent=2),
    })
    print(f"[Summarizer] Done. Length: {len(result.content)} chars")
    return {**state, "summary": result.content}
