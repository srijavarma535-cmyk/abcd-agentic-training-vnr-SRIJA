import os
import datetime
from tools.pushover_tool import send_pushover_alert

def notifier_node(state: dict) -> dict:
    topic = state.get("original_query", "Research")
    score = round(state.get("quality_score", 0.0), 1)
    retries = state.get("retry_count", 0)
    report = state.get("final_report", "")
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in topic)[:50]
    filename = f"outputs/report_{safe}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[Notifier] Report saved to: {filename}")
    preview = report[:200].replace("\n", " ").strip()
    send_pushover_alert.invoke({
        "title": f"Research done: {topic[:45]}",
        "message": f"Quality {score}/10 | {retries} retries\n{preview}...",
    })
    return {**state, "output_file": filename}
