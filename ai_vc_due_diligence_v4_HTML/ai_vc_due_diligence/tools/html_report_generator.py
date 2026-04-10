"""
HTML Report Generator
Converts due diligence JSON output into a stunning standalone HTML webpage.
"""
from datetime import datetime
import json


class HTMLReportGenerator:
    def generate(self, report: dict) -> str:
        startup     = report.get("startup", "Unknown")
        score       = report.get("overall_score", 0)
        verdict     = report.get("verdict", "N/A")
        conviction  = report.get("conviction_level", "N/A")
        generated   = report.get("generated_at", datetime.utcnow().isoformat() + "Z")
        committee   = report.get("committee", {})
        agents      = report.get("agent_results", {})

        # Verdict color
        verdict_colors = {
            "STRONG PASS":        ("#00ff87", "#003d1f"),
            "PASS":               ("#4ade80", "#052e16"),
            "CONDITIONAL PASS":   ("#fbbf24", "#1c1003"),
            "SOFT PASS":          ("#fbbf24", "#1c1003"),
            "PASS WITH CONDITIONS":("#fbbf24","#1c1003"),
            "NO GO":              ("#f87171", "#1f0505"),
        }
        v_accent, v_bg = verdict_colors.get(verdict, ("#94a3b8", "#0f172a"))

        score_pct = min(float(score) * 10, 100)

        breakdown      = committee.get("score_breakdown", {})
        breakdown_html = self._score_bars(breakdown)
        agent_sections = self._agent_sections(agents)
        questions_html = self._list_items(committee.get("key_diligence_questions", []), "❓")
        nextsteps_html = self._list_items(committee.get("next_steps", []), "→")
        comps_html     = self._tags(committee.get("comparable_exits", []))
        report_json    = json.dumps(report, indent=2)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>VC Due Diligence — {startup}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap" rel="stylesheet"/>
<style>
:root {{
  --bg:        #080c10;
  --surface:   #0d1117;
  --border:    #1e2733;
  --muted:     #3d4f63;
  --text:      #cdd9e5;
  --bright:    #e6edf3;
  --accent:    {v_accent};
  --accent-bg: {v_bg};
  --score-color: {"#00ff87" if score >= 7 else "#fbbf24" if score >= 5 else "#f87171"};
  --font-display: 'Syne', sans-serif;
  --font-body:    'DM Sans', sans-serif;
  --font-mono:    'DM Mono', monospace;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 15px;
  line-height: 1.7;
  min-height: 100vh;
}}

/* ── NOISE OVERLAY ── */
body::before {{
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
  pointer-events: none; opacity: .4;
}}

/* ── GRID LINES ── */
body::after {{
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image:
    linear-gradient(var(--border) 1px, transparent 1px),
    linear-gradient(90deg, var(--border) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: .25;
  pointer-events: none;
}}

.wrap {{ position: relative; z-index: 1; max-width: 1100px; margin: 0 auto; padding: 0 24px 80px; }}

/* ── HERO ── */
.hero {{
  padding: 72px 0 56px;
  border-bottom: 1px solid var(--border);
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 40px;
  align-items: end;
  animation: fadeUp .6s ease both;
}}
.hero-label {{
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: .2em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 16px;
}}
.hero-title {{
  font-family: var(--font-display);
  font-size: clamp(2.4rem, 5vw, 4rem);
  font-weight: 800;
  color: var(--bright);
  line-height: 1.05;
  letter-spacing: -.02em;
}}
.hero-title span {{ color: var(--accent); }}
.hero-meta {{
  margin-top: 20px;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--muted);
}}
.hero-meta b {{ color: var(--text); }}

/* score ring */
.score-ring {{
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  flex-shrink: 0;
}}
.ring-svg {{ width: 120px; height: 120px; transform: rotate(-90deg); }}
.ring-bg   {{ fill: none; stroke: var(--border); stroke-width: 8; }}
.ring-fill {{
  fill: none; stroke: var(--score-color); stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 314;
  stroke-dashoffset: calc(314 - 314 * {score_pct} / 100);
  transition: stroke-dashoffset 1.5s cubic-bezier(.4,0,.2,1);
  filter: drop-shadow(0 0 8px var(--score-color));
}}
.ring-label {{
  font-family: var(--font-display);
  font-size: 2rem; font-weight: 800;
  color: var(--bright);
  text-align: center; line-height: 1;
}}
.ring-sub {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .12em; }}

/* ── VERDICT BANNER ── */
.verdict-banner {{
  margin: 32px 0;
  padding: 20px 28px;
  background: var(--accent-bg);
  border: 1px solid var(--accent);
  border-left: 4px solid var(--accent);
  border-radius: 4px;
  display: flex; align-items: center; gap: 20px;
  animation: fadeUp .6s .1s ease both;
}}
.verdict-label {{ font-family: var(--font-mono); font-size: 10px; letter-spacing: .2em; text-transform: uppercase; color: var(--muted); }}
.verdict-value {{ font-family: var(--font-display); font-size: 1.5rem; font-weight: 800; color: var(--accent); }}
.conviction-pill {{
  margin-left: auto;
  font-family: var(--font-mono); font-size: 11px; letter-spacing: .1em;
  padding: 6px 14px; border: 1px solid var(--border); border-radius: 100px;
  color: var(--text); text-transform: uppercase;
}}

/* ── SECTION ── */
.section {{
  margin-top: 56px;
  animation: fadeUp .5s ease both;
}}
.section-header {{
  display: flex; align-items: center; gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 28px;
}}
.section-icon {{ font-size: 1.2rem; }}
.section-title {{
  font-family: var(--font-display);
  font-size: 1.25rem; font-weight: 700;
  color: var(--bright); letter-spacing: -.01em;
}}
.section-score {{
  margin-left: auto;
  font-family: var(--font-mono); font-size: 13px;
  color: var(--score-color);
}}

/* ── CARDS GRID ── */
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 22px 24px;
  transition: border-color .2s, transform .2s;
}}
.card:hover {{ border-color: var(--muted); transform: translateY(-2px); }}
.card-label {{ font-family: var(--font-mono); font-size: 10px; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }}
.card-value {{ font-family: var(--font-display); font-size: 1.6rem; font-weight: 700; color: var(--bright); }}
.card-sub {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}

/* ── SCORE BARS ── */
.score-bars {{ display: flex; flex-direction: column; gap: 14px; }}
.bar-row {{ display: flex; flex-direction: column; gap: 6px; }}
.bar-meta {{ display: flex; justify-content: space-between; font-size: 13px; }}
.bar-name {{ color: var(--text); font-weight: 500; }}
.bar-val  {{ font-family: var(--font-mono); color: var(--accent); }}
.bar-track {{
  height: 6px; background: var(--border); border-radius: 100px; overflow: hidden;
}}
.bar-fill {{
  height: 100%; border-radius: 100px;
  background: linear-gradient(90deg, var(--muted), var(--accent));
  transition: width 1.2s cubic-bezier(.4,0,.2,1);
}}

/* ── TEXT BLOCKS ── */
.text-block {{ color: var(--text); line-height: 1.75; font-size: 15px; }}
.label-text {{ font-family: var(--font-mono); font-size: 10px; letter-spacing: .18em; text-transform: uppercase; color: var(--muted); margin-bottom: 10px; margin-top: 24px; }}

/* ── THESIS GRID ── */
.thesis-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 4px; }}
@media (max-width: 640px) {{ .thesis-grid {{ grid-template-columns: 1fr; }} }}
.thesis-card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 20px;
}}
.thesis-card.bull {{ border-top: 2px solid #4ade80; }}
.thesis-card.bear {{ border-top: 2px solid #f87171; }}
.thesis-card.main {{ border-top: 2px solid var(--accent); grid-column: 1 / -1; }}
.thesis-head {{ font-family: var(--font-mono); font-size: 10px; letter-spacing: .15em; text-transform: uppercase; margin-bottom: 10px; }}
.thesis-card.bull .thesis-head {{ color: #4ade80; }}
.thesis-card.bear .thesis-head {{ color: #f87171; }}
.thesis-card.main .thesis-head {{ color: var(--accent); }}

/* ── LISTS ── */
.fancy-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
.fancy-list li {{
  display: flex; gap: 12px; align-items: flex-start;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 6px; padding: 12px 16px; font-size: 14px; color: var(--text);
}}
.fancy-list li .li-icon {{ color: var(--accent); font-style: normal; flex-shrink: 0; margin-top: 1px; font-family: var(--font-mono); }}

/* ── TAGS ── */
.tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }}
.tag {{
  font-family: var(--font-mono); font-size: 11px; letter-spacing: .05em;
  padding: 5px 12px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 100px; color: var(--text);
}}

/* ── AGENT GRID ── */
.agent-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; }}
.agent-card {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; transition: border-color .2s;
}}
.agent-card:hover {{ border-color: var(--muted); }}
.agent-header {{
  padding: 16px 20px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}}
.agent-emoji {{ font-size: 1.3rem; }}
.agent-name  {{ font-family: var(--font-display); font-size: .95rem; font-weight: 700; color: var(--bright); }}
.agent-score-pill {{
  margin-left: auto; font-family: var(--font-mono); font-size: 12px;
  padding: 3px 10px; border-radius: 100px;
  background: var(--bg); border: 1px solid var(--border); color: var(--score-color);
}}
.agent-body {{ padding: 18px 20px; font-size: 13.5px; color: var(--text); line-height: 1.65; }}
.agent-detail {{ margin-top: 14px; display: flex; flex-direction: column; gap: 8px; }}
.agent-kv {{ display: flex; gap: 8px; font-size: 12px; }}
.agent-kv .k {{ color: var(--muted); font-family: var(--font-mono); flex-shrink: 0; }}
.agent-kv .v {{ color: var(--text); }}

/* ── JSON VIEWER ── */
.json-block {{
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: 20px 24px; overflow-x: auto;
  font-family: var(--font-mono); font-size: 12px; color: var(--muted);
  max-height: 400px; overflow-y: auto;
}}
details summary {{ cursor: pointer; color: var(--accent); font-family: var(--font-mono); font-size: 12px; letter-spacing: .1em; margin-bottom: 12px; }}

/* ── FOOTER ── */
footer {{
  margin-top: 80px; padding-top: 24px; border-top: 1px solid var(--border);
  text-align: center; font-size: 12px; color: var(--muted); font-family: var(--font-mono);
}}

/* ── ANIMATIONS ── */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(20px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
.section:nth-child(2) {{ animation-delay: .05s; }}
.section:nth-child(3) {{ animation-delay: .10s; }}
.section:nth-child(4) {{ animation-delay: .15s; }}
.section:nth-child(5) {{ animation-delay: .20s; }}
.section:nth-child(6) {{ animation-delay: .25s; }}
</style>
</head>
<body>
<div class="wrap">

  <!-- HERO -->
  <header class="hero">
    <div>
      <div class="hero-label">VC Due Diligence Report</div>
      <h1 class="hero-title">
        <span>{startup}</span><br/>Investment Analysis
      </h1>
      <div class="hero-meta">
        Generated <b>{generated[:10]}</b> &nbsp;·&nbsp;
        AI VC Due Diligence Agent Team &nbsp;·&nbsp;
        7 Specialist Agents
      </div>
    </div>
    <div class="score-ring">
      <svg class="ring-svg" viewBox="0 0 120 120">
        <circle class="ring-bg"   cx="60" cy="60" r="50"/>
        <circle class="ring-fill" cx="60" cy="60" r="50"/>
      </svg>
      <div class="ring-label">{score}<span style="font-size:1rem;color:var(--muted)">/10</span></div>
      <div class="ring-sub">Overall Score</div>
    </div>
  </header>

  <!-- VERDICT -->
  <div class="verdict-banner">
    <div>
      <div class="verdict-label">Investment Verdict</div>
      <div class="verdict-value">{verdict}</div>
    </div>
    <div class="conviction-pill">Conviction: {conviction}</div>
  </div>

  <!-- SCORE BREAKDOWN -->
  <div class="section">
    <div class="section-header">
      <span class="section-icon">📊</span>
      <span class="section-title">Score Breakdown</span>
    </div>
    <div class="score-bars">
      {breakdown_html}
    </div>
  </div>

  <!-- EXECUTIVE SUMMARY -->
  <div class="section">
    <div class="section-header">
      <span class="section-icon">📋</span>
      <span class="section-title">Executive Summary</span>
    </div>
    <p class="text-block">{committee.get("summary", "")}</p>

    <div class="label-text">Investment Thesis</div>
    <div class="thesis-grid">
      <div class="thesis-card bull">
        <div class="thesis-head">🐂 Bull Case</div>
        <p class="text-block" style="font-size:14px">{committee.get("bull_case","")}</p>
      </div>
      <div class="thesis-card bear">
        <div class="thesis-head">🐻 Bear Case</div>
        <p class="text-block" style="font-size:14px">{committee.get("bear_case","")}</p>
      </div>
      <div class="thesis-card main">
        <div class="thesis-head">💡 Investment Thesis</div>
        <p class="text-block" style="font-size:14px">{committee.get("investment_thesis","")}</p>
      </div>
    </div>
  </div>

  <!-- AGENT SECTIONS -->
  <div class="section">
    <div class="section-header">
      <span class="section-icon">🤖</span>
      <span class="section-title">Agent Analysis</span>
    </div>
    <div class="agent-grid">
      {agent_sections}
    </div>
  </div>

  <!-- DILIGENCE QUESTIONS -->
  <div class="section">
    <div class="section-header">
      <span class="section-icon">❓</span>
      <span class="section-title">Key Diligence Questions</span>
    </div>
    <ul class="fancy-list">
      {questions_html}
    </ul>
  </div>

  <!-- NEXT STEPS -->
  <div class="section">
    <div class="section-header">
      <span class="section-icon">🔜</span>
      <span class="section-title">Recommended Next Steps</span>
    </div>
    <ul class="fancy-list">
      {nextsteps_html}
    </ul>
  </div>

  <!-- COMPARABLE EXITS -->
  {"" if not committee.get("comparable_exits") else f'''
  <div class="section">
    <div class="section-header">
      <span class="section-icon">🏆</span>
      <span class="section-title">Comparable Exits</span>
    </div>
    <div class="tags">{comps_html}</div>
  </div>
  '''}

  <!-- RAW JSON -->
  <div class="section">
    <div class="section-header">
      <span class="section-icon">🗂️</span>
      <span class="section-title">Full Data</span>
    </div>
    <details>
      <summary>▶ Show raw JSON report</summary>
      <div class="json-block"><pre>{report_json}</pre></div>
    </details>
  </div>

  <footer>
    AI VC Due Diligence Agent Team &nbsp;·&nbsp; Powered by Google Gemini &nbsp;·&nbsp;
    Always validate findings with primary research.
  </footer>

</div>
</body>
</html>"""

    def _score_bars(self, breakdown: dict) -> str:
        html = []
        labels = {
            "market": "📈 Market", "team": "👥 Team", "product": "🚀 Product",
            "financials": "💰 Financials", "competition": "🔍 Competitive", "risk": "⚠️ Risk",
        }
        for k, v in breakdown.items():
            label = labels.get(k, k.title())
            pct   = min(float(v) * 10, 100)
            html.append(f"""
        <div class="bar-row">
          <div class="bar-meta">
            <span class="bar-name">{label}</span>
            <span class="bar-val">{v}/10</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width:{pct}%"></div>
          </div>
        </div>""")
        return "\n".join(html)

    def _agent_sections(self, agents: dict) -> str:
        config = {
            "market":      ("📈", "Market Analysis",          "overall_market_score",      [("market_growth_rate_pct","Growth Rate %"),("market_timing","Timing")]),
            "team":        ("👥", "Team Analysis",            "overall_team_score",        [("team_completeness_score","Completeness"),("founder_market_fit_score","Founder-Market Fit")]),
            "product":     ("🚀", "Product Analysis",         "overall_product_score",     [("product_stage","Stage"),("pmf_score","PMF Score"),("technical_moat_score","Tech Moat")]),
            "financials":  ("💰", "Financial Analysis",       "overall_financial_score",   [("revenue_model","Revenue Model"),("burn_rate_assessment","Burn Rate"),("runway_months_estimate","Runway (mo)")]),
            "competitive": ("🔍", "Competitive Intelligence", "overall_competitive_score", [("market_concentration","Market Structure"),("differentiation_score","Differentiation")]),
            "risk":        ("⚠️", "Risk Assessment",          "overall_risk_score",        [("risk_adjusted_return_potential","Risk-Adj Return"),("deal_breakers","Deal Breakers")]),
        }
        html = []
        for key, (emoji, title, score_key, kvs) in config.items():
            r = agents.get(key, {})
            if not r or r.get("error"):
                continue
            score = r.get(score_key, "—")
            summary = r.get("summary", "")
            kvhtml  = ""
            for field, label in kvs:
                val = r.get(field)
                if val and val not in ([], {}, None, ""):
                    if isinstance(val, list):
                        val = ", ".join(str(x) for x in val[:3])
                    elif isinstance(val, dict):
                        val = str(list(val.values())[0]) if val else ""
                    kvhtml += f'<div class="agent-kv"><span class="k">{label}</span><span class="v">{val}</span></div>'

            html.append(f"""
      <div class="agent-card">
        <div class="agent-header">
          <span class="agent-emoji">{emoji}</span>
          <span class="agent-name">{title}</span>
          <span class="agent-score-pill">{score}/10</span>
        </div>
        <div class="agent-body">
          <p>{summary}</p>
          {f'<div class="agent-detail">{kvhtml}</div>' if kvhtml else ''}
        </div>
      </div>""")
        return "\n".join(html)

    def _list_items(self, items: list, icon: str = "→") -> str:
        if not items:
            return '<li><span class="li-icon">—</span>No items.</li>'
        return "\n".join(
            f'<li><span class="li-icon">{icon}</span>{item}</li>'
            for item in items
        )

    def _tags(self, items: list) -> str:
        return "".join(f'<span class="tag">{item}</span>' for item in items)
