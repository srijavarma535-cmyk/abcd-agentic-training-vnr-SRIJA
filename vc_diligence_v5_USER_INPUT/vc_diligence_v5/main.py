#!/usr/bin/env python3
"""
AI VC Due Diligence Agent Team v5
Usage:
  python main.py --startup "Stripe"
  python main.py --startup "Notion" --description "All-in-one workspace tool" --mode quick
  python main.py --startup "HealthPilot" --url https://healthpilot.ai --mode full
"""
import asyncio, argparse, json, os, webbrowser
from pathlib import Path

try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

from orchestrator.pipeline import DueDiligencePipeline
from config.settings import Settings


def parse_args():
    p = argparse.ArgumentParser(
        description="AI VC Due Diligence — Enter ANY startup name and get a full investment analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --startup "Stripe"
  python main.py --startup "My Startup" --description "B2B SaaS for HR teams" --mode quick
  python main.py --startup "HealthPilot" --url https://healthpilot.ai --mode full
  python main.py --startup "NovaMind AI" --deck pitch_deck.pdf
        """
    )
    p.add_argument("--startup",     required=True,
                   help="Name of the startup to analyse (any name you choose)")
    p.add_argument("--description", default="",
                   help="Optional: brief description of what the startup does")
    p.add_argument("--url",         default=None,
                   help="Optional: startup website URL to scrape for context")
    p.add_argument("--deck",        default=None,
                   help="Optional: path to pitch deck PDF")
    p.add_argument("--output",      default="data/outputs",
                   help="Directory to save reports (default: data/outputs)")
    p.add_argument("--mode",        default="full",
                   choices=["full", "quick", "market-only", "team-only"],
                   help="full=all 7 agents | quick=3 agents | market-only | team-only")
    p.add_argument("--model",       default=None,
                   help="Override Ollama model (default: llama3.2)")
    p.add_argument("--no-browser",  action="store_true",
                   help="Do not auto-open the HTML report in browser")
    return p.parse_args()


def on_event(ev: dict):
    e, d = ev["event"], ev["data"]
    if e == "phase":
        print(f"\n🔄 Phase {d['phase']}/5: {d['label']}")
    elif e == "agent_start":
        print(f"  ▶  {d['agent']} starting…")
    elif e == "agent_done":
        r = d.get("result", {})
        score_key = next((k for k in r if "overall" in k and "score" in k), None)
        score_str = f" → {r[score_key]}/10" if score_key and r.get(score_key) else ""
        print(f"  ✅ {d['agent']} done{score_str}")
    elif e == "agent_error":
        print(f"  ⚠️  {d['agent']}: {d['error'][:80]}")
    elif e == "log":
        print(f"  ℹ️  {d['msg']}")
    elif e == "complete":
        print(f"\n{'='*55}")
        print(f"  ✅  Score: {d['score']}/10  |  Verdict: {d['verdict']}")
        print(f"{'='*55}")


async def main():
    args = parse_args()
    settings = Settings()

    if args.model:
        settings.ollama_model = args.model

    print(f"\n{'='*55}")
    print(f"  🏦  AI VC Due Diligence Agent Team v5")
    print(f"  🦙  Ollama · {settings.ollama_model}")
    print(f"  🔍  Startup : {args.startup}")
    if args.description:
        print(f"  📝  Desc    : {args.description[:60]}")
    if args.url:
        print(f"  🌐  URL     : {args.url}")
    print(f"  📋  Mode    : {args.mode}")
    print(f"{'='*55}")

    # Check Ollama is running
    try:
        settings.validate()
    except RuntimeError as e:
        print(e)
        return

    pipeline = DueDiligencePipeline(settings, on_event=on_event)

    # Pass description into context via startup_name if provided
    startup_label = args.startup
    if args.description:
        # We inject it into context via the description field of context
        pass

    report = await pipeline.run(
        startup_name=startup_label,
        description=args.description,   # ← user-supplied description
        url=args.url,
        deck_path=args.deck,
        mode=args.mode,
    )

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    safe = args.startup.replace(" ", "_").replace("/", "_")

    json_path = out / f"{safe}_report.json"
    md_path   = out / f"{safe}_report.md"
    html_path = out / f"{safe}_report.html"

    json_path.write_text(json.dumps(report, indent=2, default=str))
    md_path.write_text(report.get("markdown_report", ""))
    html_path.write_text(report.get("html_report", ""), encoding="utf-8")

    print(f"\n  📄  HTML  → {html_path}")
    print(f"  📝  MD    → {md_path}")
    print(f"  🗂️   JSON  → {json_path}\n")

    if not args.no_browser:
        print("  🌐  Opening report in browser…\n")
        webbrowser.open(html_path.resolve().as_uri())


if __name__ == "__main__":
    asyncio.run(main())
