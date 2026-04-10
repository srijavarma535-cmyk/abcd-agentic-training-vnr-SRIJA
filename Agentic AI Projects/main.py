#!/usr/bin/env python3
"""
AI VC Due Diligence Agent Team
Powered by Google Gemini — 100% FREE (1500 requests/day)
Get your free key: https://aistudio.google.com/app/apikey
"""

import asyncio
import argparse
import json
import os
import webbrowser
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from orchestrator.pipeline import DueDiligencePipeline
from config.settings import Settings
from tools.html_report_generator import HTMLReportGenerator


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI VC Due Diligence Agent Team (FREE - powered by Gemini)"
    )
    parser.add_argument("--startup", type=str, required=True, help="Startup name")
    parser.add_argument("--url",     type=str, default=None,   help="Startup website URL")
    parser.add_argument("--deck",    type=str, default=None,   help="Path to pitch deck PDF")
    parser.add_argument("--output",  type=str, default="data/outputs", help="Output directory")
    parser.add_argument("--mode",    choices=["full","quick","market-only","team-only"],
                        default="full", help="Analysis mode")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't auto-open the HTML report in browser")
    return parser.parse_args()


async def main():
    args = parse_args()
    settings = Settings()

    if not settings.gemini_api_key:
        print("\n❌  GEMINI_API_KEY is not set!")
        print("👉  Get your FREE key (no credit card) at:")
        print("    https://aistudio.google.com/app/apikey\n")
        print("👉  Then set it:")
        print("    Windows CMD:  set GEMINI_API_KEY=AIza...")
        print("    Or add to .env file:  GEMINI_API_KEY=AIza...\n")
        return

    print(f"\n{'='*60}")
    print(f"  🏦 AI VC Due Diligence Agent Team")
    print(f"  ⚡ Powered by Google Gemini (FREE)")
    print(f"  🔍 Analyzing: {args.startup}")
    print(f"  📋 Mode: {args.mode}")
    print(f"{'='*60}\n")

    pipeline   = DueDiligencePipeline(settings)
    html_gen   = HTMLReportGenerator()

    report = await pipeline.run(
        startup_name=args.startup,
        url=args.url,
        deck_path=args.deck,
        mode=args.mode,
    )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_name = report['startup'].replace(' ', '_').replace('/', '_')

    # ── Save JSON ──────────────────────────────────────────────
    json_path = output_dir / f"{safe_name}_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # ── Save Markdown ──────────────────────────────────────────
    md_path = output_dir / f"{safe_name}_report.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report.get("markdown_report", ""))

    # ── Save HTML (beautiful webpage) ─────────────────────────
    html_path = output_dir / f"{safe_name}_report.html"
    html_content = html_gen.generate(report)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n{'='*60}")
    print(f"  ✅  Due Diligence Complete!")
    print(f"{'='*60}")
    print(f"\n  📊  Overall Score : {report.get('overall_score', 'N/A')}/10")
    print(f"  🏷️   Verdict       : {report.get('verdict', 'N/A')}")
    print(f"  💡  Conviction    : {report.get('conviction_level', 'N/A')}")
    print(f"\n  📄  HTML Report  → {html_path}")
    print(f"  📝  MD Report    → {md_path}")
    print(f"  🗂️   JSON Report  → {json_path}")

    # ── Auto-open HTML in browser ──────────────────────────────
    if not args.no_browser:
        print(f"\n  🌐  Opening report in your browser...")
        webbrowser.open(html_path.resolve().as_uri())

    print()


if __name__ == "__main__":
    asyncio.run(main())
