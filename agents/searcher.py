import json
from langchain_core.prompts import ChatPromptTemplate
from config.models import searcher_llm
from tools.serper_tool import web_search

EXTRACT_PROMPT = ChatPromptTemplate.from_template("""
You searched the web for: "{query}"
Raw search results: {results}

Extract the 4 most useful factual findings. Each must include the source URL.
Return ONLY valid JSON, no markdown:
{{"facts": [{{"fact": "specific finding", "source": "https://..."}}]}}
""")

def _make_search_node(topic_index: int):
    def search_node(state: dict) -> dict:
        sub_topics = state.get("sub_topics", [])
        if topic_index >= len(sub_topics):
            return state
        query = sub_topics[topic_index]
        print(f"[Search {chr(65+topic_index)}] Searching: {query}")
        raw = web_search.invoke({"query": query})
        chain = EXTRACT_PROMPT | searcher_llm
        result = chain.invoke({"query": query, "results": json.dumps(raw, indent=2)})
        try:
            parsed = json.loads(result.content)
            facts = parsed.get("facts", [])
        except Exception:
            facts = [{"fact": f"Search results for: {query}", "source": ""}]
        print(f"[Search {chr(65+topic_index)}] Found {len(facts)} facts.")
        existing = state.get("raw_results", [])
        return {**state, "raw_results": existing + facts}
    search_node.__name__ = f"search_{chr(65+topic_index)}_node"
    return search_node

search_A_node = _make_search_node(0)
search_B_node = _make_search_node(1)
search_C_node = _make_search_node(2)
