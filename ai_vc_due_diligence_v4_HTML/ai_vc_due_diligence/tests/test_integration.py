"""
Integration test — runs a quick live analysis.
Requires GEMINI_API_KEY to be set (free at aistudio.google.com/app/apikey)
Usage: python tests/test_integration.py
"""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from orchestrator.pipeline import DueDiligencePipeline
from config.settings import Settings

async def run_demo():
    settings = Settings()
    if not settings.gemini_api_key:
        print("❌ GEMINI_API_KEY not set.")
        print("👉 Get FREE key: https://aistudio.google.com/app/apikey")
        return

    pipeline = DueDiligencePipeline(settings)
    print("\n🧪 Integration Test: Analyzing 'NovaMind AI'")
    report = await pipeline.run(startup_name="NovaMind AI", mode="quick")

    print(f"\n  Score  : {report['overall_score']}/10")
    print(f"  Verdict: {report['verdict']}")

    os.makedirs("data/outputs", exist_ok=True)
    with open("data/outputs/novamind_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    with open("data/outputs/novamind_test_report.md", "w") as f:
        f.write(report.get("markdown_report", ""))
    print("\n✅ Done. Output in data/outputs/")

if __name__ == "__main__":
    asyncio.run(run_demo())
