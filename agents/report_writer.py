import datetime
from langchain_core.prompts import ChatPromptTemplate
from config.models import report_llm

REPORT_PROMPT = ChatPromptTemplate.from_template("""
Write a complete professional research report.

Topic: {original_query}
Research data: {summary}
Quality score: {quality_score}/10
Date: {date}

Format EXACTLY as:
# [Descriptive Title]
**Date:** {date} | **Quality Score:** {quality_score}/10
---
## Executive Summary
## Key Findings
## Detailed Analysis
### [Theme 1]
### [Theme 2]
### [Theme 3]
## Conclusion
## Sources
""")

def report_writer_node(state: dict) -> dict:
    print("[Report Writer] Generating final report...")
    chain = REPORT_PROMPT | report_llm
    result = chain.invoke({
        "original_query": state.get("original_query", ""),
        "summary": state.get("summary", ""),
        "quality_score": round(state.get("quality_score", 0.0), 1),
        "date": datetime.date.today().strftime("%B %d, %Y"),
    })
    print(f"[Report Writer] Done. Length: {len(result.content)} chars")
    return {**state, "final_report": result.content}
