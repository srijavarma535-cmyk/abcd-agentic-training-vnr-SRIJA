"""
HTMLReportGenerator — Bloomberg-dark VC dashboard
Full tabbed interface: Overview · Market · Team · Product · Financials · Competition · Verdict
"""
import json
from datetime import datetime


class HTMLReportGenerator:
    def generate(self, report: dict) -> str:
        # ── safe converters (handle None, "?", missing gracefully) ──────────
        def safe_float(v, default=0.0):
            if v is None or v == "?" or v == "": return default
            try: return float(v)
            except (TypeError, ValueError): return default

        def safe_str(v, default="N/A"):
            if v is None or v == "": return default
            return str(v)

        def safe_int(v, default=0):
            if v is None or v == "?" or v == "": return default
            try: return int(float(v))
            except (TypeError, ValueError): return default

        startup    = report.get("startup","Unknown")
        score      = safe_float(report.get("overall_score", 0))
        verdict    = safe_str(report.get("verdict","N/A")) or "N/A"
        worth      = report.get("worth_investing", False)
        if isinstance(worth, str): worth = safe_str(worth).lower() == "true"
        conviction = safe_str(report.get("conviction","N/A")) or "N/A"
        generated  = str(report.get("generated_at",""))[:10]
        committee  = report.get("committee",{})
        agents     = report.get("agent_results",{})
        market     = agents.get("market",{})
        team       = agents.get("team",{})
        product    = agents.get("product",{})
        fin        = agents.get("financials",{})
        comp       = agents.get("competitive",{})
        risk       = agents.get("risk",{})

        # verdict colour
        vcolors = {
            "STRONG INVEST": ("#00ff87","#003d1f"),
            "INVEST":        ("#4ade80","#052e16"),
            "CONDITIONAL INVEST": ("#fbbf24","#1c1003"),
            "HOLD":          ("#fb923c","#1c0a00"),
            "PASS":          ("#f87171","#1f0505"),
        }
        vc_accent, vc_bg = vcolors.get(str(verdict).upper().strip(), ("#94a3b8","#0f172a"))
        score_color = "#00ff87" if safe_float(score)>=7 else "#fbbf24" if safe_float(score)>=5 else "#f87171"
        score_pct   = min(safe_float(score)*10, 100)

        breakdown = committee.get("score_breakdown",{}) or {}
        report_json_str = json.dumps(report, indent=2, default=str)

        # ── helpers ──────────────────────────────────────────────────────────
        def stars(n, max_n=10):
            filled = round(safe_float(n) / 2)
            return "".join(["★" if i < filled else "☆" for i in range(5)])

        def tag(txt, color="#334155"):
            return f'<span style="background:{color};color:#e2e8f0;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:.05em">{txt}</span>'

        def score_bar(label, val, icon=""):
            pct = min(safe_float(val)*10,100)
            clr = "#00ff87" if pct>=70 else "#fbbf24" if pct>=50 else "#f87171"
            return f"""
            <div style="margin-bottom:14px">
              <div style="display:flex;justify-content:space-between;margin-bottom:5px">
                <span style="color:#94a3b8;font-size:13px">{icon} {label}</span>
                <span style="color:{clr};font-weight:700;font-family:monospace">{val}/10</span>
              </div>
              <div style="background:#1e293b;border-radius:100px;height:6px;overflow:hidden">
                <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#334155,{clr});border-radius:100px;transition:width 1.2s"></div>
              </div>
            </div>"""

        def metric_card(label, value, sub="", icon="", color="#00ff87"):
            return f"""
            <div class="metric-card" style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px 22px;min-width:140px;flex:1">
              <div style="color:#64748b;font-size:11px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px">{icon} {label}</div>
              <div style="color:{color};font-size:1.6rem;font-weight:800;line-height:1">{value}</div>
              {f'<div style="color:#64748b;font-size:12px;margin-top:5px">{sub}</div>' if sub else ''}
            </div>"""

        def insight_box(text, icon="🧠"):
            return f"""
            <div style="background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #7c3aed40;border-left:3px solid #7c3aed;border-radius:8px;padding:16px 18px;margin:16px 0">
              <div style="color:#a78bfa;font-size:11px;font-weight:700;letter-spacing:.1em;margin-bottom:8px">{icon} AI INSIGHT</div>
              <p style="color:#cbd5e1;font-size:14px;line-height:1.65;margin:0">{text}</p>
            </div>"""

        def risk_badge(level):
            c = {"low":"#4ade80","medium":"#fbbf24","high":"#f87171","critical":"#ef4444"}.get(str(level).lower(),"#64748b")
            return f'<span style="color:{c};font-weight:700;font-size:12px;text-transform:uppercase">{level}</span>'

        def list_items(items, icon="▸"):
            if not items: return '<p style="color:#475569;font-style:italic">None identified</p>'
            return "".join(f'<div style="color:#cbd5e1;font-size:13px;padding:6px 0;border-bottom:1px solid #1e293b"><span style="color:#7c3aed">{icon}</span> {item}</div>' for item in (items or []))

        # ── Market tab ───────────────────────────────────────────────────────
        def market_tab():
            tam   = market.get("tam_usd_billions","?")
            sam   = market.get("sam_usd_billions","?")
            som   = market.get("som_usd_billions","?")
            cagr  = market.get("cagr_pct","?")
            geo   = market.get("geography","?")
            stage = market.get("market_stage","?")
            trends= market.get("key_trends",[]) or []
            risks = market.get("market_risks",[]) or []
            reg   = market.get("regulation_risk","?")
            timing= market.get("timing_score",5)
            ms    = market.get("overall_market_score",5)
            insight = market.get("ai_insight","")
            # bar chart data as inline SVG
            vals  = [("TAM",safe_float(tam)),("SAM",safe_float(sam)),("SOM",safe_float(som))]
            max_v = max(v for _,v in vals) or 1
            bars  = ""
            colors= ["#7c3aed","#4ade80","#fbbf24"]
            for i,(lbl,v) in enumerate(vals):
                w = int((v/max_v)*200)
                bars += f"""<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
                  <div style="color:#94a3b8;width:32px;font-size:12px">{lbl}</div>
                  <div style="background:{colors[i]};height:24px;width:{w}px;border-radius:4px;min-width:4px;transition:width 1s"></div>
                  <div style="color:#e2e8f0;font-size:13px;font-weight:700">${v}B</div></div>"""
            return f"""
            <div class="tab-pane" id="tab-market">
              <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px">
                {metric_card("TAM","$"+str(tam)+"B","Total Addressable Market","🌍","#7c3aed")}
                {metric_card("SAM","$"+str(sam)+"B","Serviceable Market","🎯","#4ade80")}
                {metric_card("SOM","$"+str(som)+"B","Obtainable Market","🏹","#fbbf24")}
                {metric_card("CAGR",str(cagr)+"%","Annual Growth Rate","📈","#00ff87")}
                {metric_card("Score",str(ms)+"/10","Market Score","⭐",score_color)}
              </div>
              {insight_box(insight)}
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">TAM / SAM / SOM</h3>
                  {bars}
                </div>
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">MARKET DETAILS</h3>
                  <div style="display:flex;flex-direction:column;gap:10px">
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Stage</span><span style="color:#e2e8f0;text-transform:capitalize">{stage}</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Geography</span><span style="color:#e2e8f0">{geo}</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Timing Score</span><span style="color:#fbbf24">{timing}/10</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Regulation Risk</span>{risk_badge(reg)}</div>
                  </div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
                <div class="glass-card"><h3 style="color:#4ade80;font-size:12px;letter-spacing:.1em;margin-bottom:12px">🔥 KEY TRENDS</h3>{list_items(trends,"🔥")}</div>
                <div class="glass-card"><h3 style="color:#f87171;font-size:12px;letter-spacing:.1em;margin-bottom:12px">⚠️ MARKET RISKS</h3>{list_items(risks,"⚠️")}</div>
              </div>
            </div>"""

        # ── Team tab ─────────────────────────────────────────────────────────
        def team_tab():
            founders= team.get("founders",[]) or []
            exec_s  = team.get("execution_score",5)
            dom_s   = team.get("domain_expertise_score",5)
            fit_s   = team.get("founder_market_fit_score",5)
            comp_s  = team.get("team_completeness_score",5)
            ts      = team.get("overall_team_score",5)
            gaps    = team.get("key_gaps",[]) or []
            strengths=team.get("key_strengths",[]) or []
            risk_lvl= team.get("risk_level","medium")
            insight = team.get("ai_insight","")
            founder_cards = ""
            for f in (founders or []):
                exits = f.get("prior_exits",0) or 0
                founder_cards += f"""
                <div class="glass-card" style="text-align:center;min-width:160px">
                  <div style="width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#7c3aed,#4f46e5);display:flex;align-items:center;justify-content:center;margin:0 auto 12px;font-size:22px">👤</div>
                  <div style="color:#e2e8f0;font-weight:700;font-size:15px">{f.get("name","Unknown")}</div>
                  <div style="color:#7c3aed;font-size:12px;margin:4px 0">{f.get("role","")}</div>
                  <div style="color:#64748b;font-size:12px">{f.get("background","")}</div>
                  {f'<div style="color:#fbbf24;font-size:12px;margin-top:6px">🏆 {exits} exit(s)</div>' if exits else ''}
                </div>"""
            if not founder_cards:
                founder_cards = '<div style="color:#475569;font-style:italic">Founder data not available</div>'
            return f"""
            <div class="tab-pane" id="tab-team">
              <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px">
                {metric_card("Team Score",str(ts)+"/10","Overall","👥",score_color)}
                {metric_card("Execution",str(exec_s)+"/10",stars(exec_s),"⚡","#4ade80")}
                {metric_card("Domain Exp.",str(dom_s)+"/10",stars(dom_s),"🎓","#7c3aed")}
                {metric_card("Founder-Mkt",str(fit_s)+"/10",stars(fit_s),"🎯","#fbbf24")}
                {metric_card("Risk Level",safe_str(risk_lvl).upper(),"","⚠️","#f87171" if risk_lvl=="high" else "#fbbf24")}
              </div>
              {insight_box(insight)}
              <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin:20px 0 14px">FOUNDERS</h3>
              <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:20px">{founder_cards}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">SCORING PANEL</h3>
                  {score_bar("Execution",exec_s,"⚡")}
                  {score_bar("Domain Expertise",dom_s,"🎓")}
                  {score_bar("Founder-Market Fit",fit_s,"🎯")}
                  {score_bar("Team Completeness",comp_s,"👥")}
                </div>
                <div class="glass-card">
                  <h3 style="color:#4ade80;font-size:12px;letter-spacing:.1em;margin-bottom:12px">STRENGTHS</h3>
                  {list_items(strengths,"✅")}
                  <h3 style="color:#f87171;font-size:12px;letter-spacing:.1em;margin:16px 0 12px">GAPS</h3>
                  {list_items(gaps,"❌")}
                </div>
              </div>
            </div>"""

        # ── Product tab ──────────────────────────────────────────────────────
        def product_tab():
            pname   = product.get("product_name", startup)
            tagline = product.get("tagline","")
            stage   = product.get("stage","mvp")
            pmf     = product.get("pmf_score",5)
            innov   = product.get("innovation_score",5)
            moat    = product.get("technical_moat_score",5)
            scale   = product.get("scalability_score",5)
            ux      = product.get("ux_score",5)
            ps      = product.get("overall_product_score",5)
            feats   = product.get("key_features",[]) or []
            tech    = product.get("tech_stack_inferred",[]) or []
            defens  = product.get("defensibility",{}) or {}
            risks   = product.get("product_risks",[]) or []
            insight = product.get("ai_insight","")
            stage_colors = {"idea":"#f87171","prototype":"#fb923c","mvp":"#fbbf24","growth":"#4ade80","scale":"#00ff87"}
            sc = stage_colors.get(stage,"#7c3aed")
            feature_cards = ""
            for i,f in enumerate(feats or []):
                icons = ["⚡","📊","🔌","🤖","📱","🔒"]
                feature_cards += f'<div class="glass-card" style="text-align:center"><div style="font-size:24px;margin-bottom:8px">{icons[i%len(icons)]}</div><div style="color:#e2e8f0;font-size:13px">{f}</div></div>'
            ip = defens.get("ip","none")
            ne = defens.get("network_effects",False)
            dm = defens.get("data_moat",False)
            return f"""
            <div class="tab-pane" id="tab-product">
              <div style="background:linear-gradient(135deg,#1e293b,#0f172a);border:1px solid #334155;border-radius:12px;padding:24px;margin-bottom:20px">
                <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap">
                  <div>
                    <h2 style="color:#e2e8f0;font-size:1.4rem;font-weight:800;margin:0">{pname}</h2>
                    <p style="color:#64748b;margin:4px 0 0;font-size:14px;font-style:italic">{tagline}</p>
                  </div>
                  <span style="margin-left:auto;background:{sc}20;color:{sc};border:1px solid {sc}40;padding:6px 16px;border-radius:20px;font-size:12px;font-weight:700;text-transform:uppercase">{stage}</span>
                </div>
              </div>
              <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px">
                {metric_card("Product Score",str(ps)+"/10","","🚀",score_color)}
                {metric_card("PMF Score",str(pmf)+"/10",stars(pmf),"🎯","#4ade80")}
                {metric_card("Innovation",str(innov)+"/10",stars(innov),"💡","#7c3aed")}
                {metric_card("Tech Moat",str(moat)+"/10",stars(moat),"🛡️","#fbbf24")}
                {metric_card("Scalability",str(scale)+"/10",stars(scale),"📈","#00ff87")}
              </div>
              {insight_box(insight)}
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">SCORING</h3>
                  {score_bar("Product-Market Fit",pmf,"🎯")}
                  {score_bar("Innovation",innov,"💡")}
                  {score_bar("Technical Moat",moat,"🛡️")}
                  {score_bar("Scalability",scale,"📈")}
                  {score_bar("UX Quality",ux,"✨")}
                </div>
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">DEFENSIBILITY</h3>
                  <div style="display:flex;flex-direction:column;gap:10px">
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">IP Protection</span><span style="color:#e2e8f0;text-transform:capitalize">{ip}</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Network Effects</span><span style="color:{'#4ade80' if ne else '#f87171'}">{'Yes ✅' if ne else 'No ✗'}</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Data Moat</span><span style="color:{'#4ade80' if dm else '#f87171'}">{'Yes ✅' if dm else 'No ✗'}</span></div>
                  </div>
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin:16px 0 10px">TECH STACK</h3>
                  <div style="display:flex;flex-wrap:wrap;gap:6px">{''.join(tag(t,"#1e3a5f") for t in (tech or []))}</div>
                </div>
              </div>
              <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin:20px 0 14px">KEY FEATURES</h3>
              <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px">
                {feature_cards if feature_cards else '<div style="color:#475569;font-style:italic">No features data</div>'}
              </div>
            </div>"""

        # ── Financials tab ───────────────────────────────────────────────────
        def financial_tab():
            arr     = fin.get("arr_usd_estimate")
            mrr     = fin.get("mrr_usd_estimate")
            burn    = fin.get("burn_rate_monthly_usd")
            runway  = fin.get("runway_months")
            gm      = fin.get("gross_margin_pct")
            ltv_cac = fin.get("ltv_cac_ratio")
            payback = fin.get("payback_months")
            growth  = fin.get("growth_rate_pct")
            rev_mod = fin.get("revenue_model","?")
            burn_risk= fin.get("burn_risk","medium")
            fs      = fin.get("overall_financial_score",5)
            red_flags=fin.get("red_flags",[]) or []
            insight = fin.get("ai_insight","")
            rounds  = fin.get("funding_rounds",[]) or []
            def fmt_usd(v):
                if v is None: return "N/A"
                v = float(v)
                return f"${v/1e6:.1f}M" if v>=1e6 else f"${v/1e3:.0f}K" if v>=1000 else f"${v:.0f}"
            burn_color = {"low":"#4ade80","medium":"#fbbf24","high":"#f87171","critical":"#ef4444"}.get(str(burn_risk).lower(),"#64748b")
            round_rows = "".join(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #1e293b"><span style="color:#64748b">{r.get("round","?")}</span><span style="color:#e2e8f0">{fmt_usd(r.get("amount_usd"))} · {r.get("year","?")}</span></div>' for r in (rounds or []))
            return f"""
            <div class="tab-pane" id="tab-financials">
              <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px">
                {metric_card("ARR",fmt_usd(arr),"Annual Recurring Rev.","💵","#4ade80")}
                {metric_card("MRR",fmt_usd(mrr),"Monthly Recurring Rev.","📅","#4ade80")}
                {metric_card("Burn Rate",fmt_usd(burn)+"/mo","Monthly Spend","🔥",burn_color)}
                {metric_card("Runway",str(runway)+" mo" if runway else "N/A","Months Left","⏱️","#fbbf24")}
                {metric_card("Growth",str(growth)+"%" if growth else "N/A","YoY Growth","📈","#00ff87")}
              </div>
              {insight_box(insight)}
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">UNIT ECONOMICS</h3>
                  <div style="display:flex;flex-direction:column;gap:12px">
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">LTV:CAC Ratio</span><span style="color:{'#4ade80' if safe_float(ltv_cac)>=3 else '#fbbf24'};font-weight:700">{ltv_cac or 'N/A'}x</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Payback Period</span><span style="color:#e2e8f0">{payback or 'N/A'} months</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Gross Margin</span><span style="color:#4ade80">{gm or 'N/A'}%</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Revenue Model</span><span style="color:#e2e8f0;text-transform:capitalize">{rev_mod}</span></div>
                    <div style="display:flex;justify-content:space-between"><span style="color:#64748b">Financial Score</span><span style="color:{score_color};font-weight:700">{fs}/10</span></div>
                  </div>
                </div>
                <div class="glass-card">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
                    <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin:0">BURN RISK</h3>
                    <span style="color:{burn_color};font-weight:700;font-size:16px;text-transform:uppercase">{burn_risk}</span>
                  </div>
                  <div style="background:#1e293b;border-radius:8px;padding:12px;margin-bottom:16px">
                    <div style="color:#64748b;font-size:12px;margin-bottom:6px">Runway indicator</div>
                    <div style="background:#0f172a;border-radius:100px;height:10px;overflow:hidden">
                      <div style="width:{min(float(runway or 0)/24*100,100):.0f}%;height:100%;background:{burn_color};border-radius:100px"></div>
                    </div>
                    <div style="color:{burn_color};font-size:12px;margin-top:6px">{runway or '?'} months remaining</div>
                  </div>
                  <h3 style="color:#f87171;font-size:12px;letter-spacing:.1em;margin-bottom:12px">🚩 RED FLAGS</h3>
                  {list_items(red_flags,"🔴") if red_flags else '<div style="color:#475569;font-style:italic">No red flags identified</div>'}
                </div>
              </div>
              {f'<div class="glass-card" style="margin-top:20px"><h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">FUNDING HISTORY</h3>{round_rows if round_rows else chr(60)+"div style="+chr(34)+"color:#475569;font-style:italic"+chr(34)+">No funding data</div>"}</div>' if True else ''}
            </div>"""

        # ── Competition tab ──────────────────────────────────────────────────
        def competitive_tab():
            competitors = comp.get("direct_competitors",[]) or []
            indirect    = comp.get("indirect_competitors",[]) or []
            diff_s      = comp.get("differentiation_score",5)
            moat_s      = comp.get("moat_score",5)
            incumb_s    = comp.get("incumbent_threat_score",5)
            cs          = comp.get("overall_competitive_score",5)
            conc        = comp.get("market_concentration","fragmented")
            white       = comp.get("white_space",[]) or []
            risks       = comp.get("competitive_risks",[]) or []
            pos         = comp.get("positioning",{}) or {}
            insight     = comp.get("ai_insight","")
            threat_color= {"low":"#4ade80","medium":"#fbbf24","high":"#f87171"}.get
            comp_table  = "".join(f"""
            <tr style="border-bottom:1px solid #1e293b">
              <td style="padding:10px 12px;color:#e2e8f0;font-weight:600">{c.get("name","?")}</td>
              <td style="padding:10px 12px;color:#4ade80;font-size:13px">{c.get("strength","")}</td>
              <td style="padding:10px 12px;color:#f87171;font-size:13px">{c.get("weakness","")}</td>
              <td style="padding:10px 12px">{tag(c.get("stage","?"),"#1e3a5f")}</td>
              <td style="padding:10px 12px;color:{threat_color(c.get("threat","low"),"#64748b")};font-weight:700;text-transform:uppercase">{c.get("threat","?")}</td>
            </tr>""" for c in (competitors or []))
            return f"""
            <div class="tab-pane" id="tab-competitive">
              <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px">
                {metric_card("Comp Score",str(cs)+"/10","","🔍",score_color)}
                {metric_card("Differentiation",str(diff_s)+"/10",stars(diff_s),"🎯","#4ade80")}
                {metric_card("Moat",str(moat_s)+"/10",stars(moat_s),"🛡️","#7c3aed")}
                {metric_card("Incumbent Threat",str(incumb_s)+"/10",stars(incumb_s),"⚡","#f87171")}
                {metric_card("Market Structure",safe_str(conc).title(),"","🏛️","#fbbf24")}
              </div>
              {insight_box(insight)}
              <div class="glass-card" style="margin:20px 0;overflow-x:auto">
                <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">COMPETITOR MATRIX</h3>
                {'<table style="width:100%;border-collapse:collapse"><thead><tr style="border-bottom:2px solid #334155"><th style="padding:8px 12px;color:#64748b;text-align:left;font-size:12px">Company</th><th style="padding:8px 12px;color:#64748b;text-align:left;font-size:12px">Strength</th><th style="padding:8px 12px;color:#64748b;text-align:left;font-size:12px">Weakness</th><th style="padding:8px 12px;color:#64748b;text-align:left;font-size:12px">Stage</th><th style="padding:8px 12px;color:#64748b;text-align:left;font-size:12px">Threat</th></tr></thead><tbody>'+comp_table+'</tbody></table>' if comp_table else '<div style="color:#475569;font-style:italic">No competitor data available</div>'}
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">SCORING</h3>
                  {score_bar("Differentiation",diff_s,"🎯")}
                  {score_bar("Moat Strength",moat_s,"🛡️")}
                  {score_bar("Incumbent Threat",incumb_s,"⚡")}
                </div>
                <div class="glass-card">
                  <h3 style="color:#4ade80;font-size:12px;letter-spacing:.1em;margin-bottom:12px">WHITE SPACE OPPORTUNITIES</h3>
                  {list_items(white,"💡")}
                  <h3 style="color:#f87171;font-size:12px;letter-spacing:.1em;margin:16px 0 12px">COMPETITIVE RISKS</h3>
                  {list_items(risks,"⚠️")}
                </div>
              </div>
            </div>"""

        # ── Overview tab ─────────────────────────────────────────────────────
        def overview_tab():
            bd = breakdown
            return f"""
            <div class="tab-pane" id="tab-overview">
              <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px">
                {metric_card("Overall Score",str(score)+"/10","Composite Score","🏆",score_color)}
                {metric_card("Verdict",verdict,"Investment Decision","🎯",vc_accent)}
                {metric_card("Conviction",safe_str(conviction).title(),"","💡","#7c3aed")}
                {metric_card("Worth Investing","YES ✅" if worth else "NO ✗","AI Recommendation","🧠","#4ade80" if worth else "#f87171")}
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:20px">SCORE BREAKDOWN</h3>
                  {''.join(score_bar(safe_str(k).title(),v,["📊","👥","🚀","💰","🔍","⚠️"][i]) for i,(k,v) in enumerate(bd.items()))}
                </div>
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">INVESTMENT THESIS</h3>
                  <p style="color:#cbd5e1;font-size:14px;line-height:1.7;margin-bottom:16px">{committee.get("investment_thesis","")}</p>
                  <div style="display:flex;gap:8px;flex-wrap:wrap">
                    {tag("Stage: "+safe_str(committee.get("round_stage","?")),"#1e3a5f")}
                    {tag("Check: "+safe_str(committee.get("check_size_recommended","?")),"#1e3a5f")}
                  </div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px">
                <div class="glass-card" style="border-top:2px solid #4ade80">
                  <h3 style="color:#4ade80;font-size:12px;letter-spacing:.1em;margin-bottom:12px">🐂 BULL CASE</h3>
                  <p style="color:#cbd5e1;font-size:14px;line-height:1.65">{committee.get("bull_case","")}</p>
                </div>
                <div class="glass-card" style="border-top:2px solid #f87171">
                  <h3 style="color:#f87171;font-size:12px;letter-spacing:.1em;margin-bottom:12px">🐻 BEAR CASE</h3>
                  <p style="color:#cbd5e1;font-size:14px;line-height:1.65">{committee.get("bear_case","")}</p>
                </div>
              </div>
            </div>"""

        # ── Verdict tab ──────────────────────────────────────────────────────
        def verdict_tab():
            questions = committee.get("key_questions",[]) or []
            steps     = committee.get("next_steps",[]) or []
            comps     = committee.get("comparable_exits",[]) or []
            ring_dash = 314 - 314*safe_float(score_pct)/100
            q_items   = "".join(f'<div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:8px;color:#cbd5e1;font-size:14px"><span style="color:#7c3aed;font-weight:700">{i+1}.</span> {q}</div>' for i,q in enumerate(questions or []))
            s_items   = "".join(f'<div style="background:#1e293b;border-left:3px solid #4ade80;border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:8px;color:#cbd5e1;font-size:14px"><span style="color:#4ade80;font-weight:700">→</span> {s}</div>' for s in (steps or []))
            return f"""
            <div class="tab-pane" id="tab-verdict">
              <div style="background:{vc_bg};border:2px solid {vc_accent};border-radius:16px;padding:32px;text-align:center;margin-bottom:28px;position:relative;overflow:hidden">
                <div style="font-size:13px;letter-spacing:.2em;color:{vc_accent};opacity:.7;margin-bottom:8px">INVESTMENT VERDICT</div>
                <div style="font-size:3rem;font-weight:900;color:{vc_accent};letter-spacing:-.02em">{verdict}</div>
                <div style="display:flex;justify-content:center;align-items:center;gap:40px;margin-top:24px;flex-wrap:wrap">
                  <div>
                    <svg width="120" height="120" viewBox="0 0 120 120">
                      <circle cx="60" cy="60" r="50" fill="none" stroke="#1e293b" stroke-width="8"/>
                      <circle cx="60" cy="60" r="50" fill="none" stroke="{score_color}" stroke-width="8"
                        stroke-dasharray="314" stroke-dashoffset="{ring_dash:.1f}"
                        stroke-linecap="round" transform="rotate(-90 60 60)"/>
                      <text x="60" y="60" text-anchor="middle" dominant-baseline="central"
                        fill="{score_color}" font-size="22" font-weight="800" font-family="Arial">{score}</text>
                      <text x="60" y="80" text-anchor="middle" fill="#64748b" font-size="11" font-family="Arial">/10</text>
                    </svg>
                  </div>
                  <div style="text-align:left">
                    <div style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:.1em">Conviction Level</div>
                    <div style="color:{vc_accent};font-size:1.3rem;font-weight:700;margin:4px 0">{safe_str(conviction).upper()}</div>
                    <div style="color:#64748b;font-size:12px;margin-top:8px">Recommended Check</div>
                    <div style="color:#e2e8f0;font-size:1rem;font-weight:600">{committee.get("check_size_recommended","N/A")}</div>
                    <div style="color:#64748b;font-size:12px;margin-top:8px">Round Stage</div>
                    <div style="color:#e2e8f0;font-size:1rem;font-weight:600">{committee.get("round_stage","N/A")}</div>
                  </div>
                  <div style="background:{'#00ff8720' if worth else '#f8717120'};border:1px solid {'#00ff87' if worth else '#f87171'};border-radius:12px;padding:16px 24px;text-align:center">
                    <div style="font-size:2.5rem">{'✅' if worth else '❌'}</div>
                    <div style="color:{'#4ade80' if worth else '#f87171'};font-weight:800;font-size:14px;margin-top:8px">{'WORTH INVESTING' if worth else 'DO NOT INVEST'}</div>
                  </div>
                </div>
              </div>
              <div class="glass-card" style="margin-bottom:20px">
                <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">📋 EXECUTIVE SUMMARY</h3>
                <p style="color:#cbd5e1;font-size:15px;line-height:1.75">{committee.get("summary","")}</p>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px">
                <div class="glass-card">
                  <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">❓ KEY DILIGENCE QUESTIONS</h3>
                  {q_items if q_items else '<div style="color:#475569;font-style:italic">No questions generated</div>'}
                </div>
                <div class="glass-card">
                  <h3 style="color:#4ade80;font-size:12px;letter-spacing:.1em;margin-bottom:16px">🔜 NEXT STEPS</h3>
                  {s_items if s_items else '<div style="color:#475569;font-style:italic">No steps generated</div>'}
                  {f'<h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin:16px 0 10px">🏆 COMPARABLE EXITS</h3><div style="display:flex;flex-wrap:wrap;gap:6px">{"".join(tag(c,"#1e3a5f") for c in comps)}</div>' if comps else ''}
                </div>
              </div>
              <div class="glass-card">
                <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:20px">SCORE BREAKDOWN</h3>
                {''.join(score_bar(safe_str(k).title(),v,["📊","👥","🚀","💰","🔍","⚠️"][i]) for i,(k,v) in enumerate(breakdown.items()))}
                <div style="border-top:2px solid #334155;margin-top:16px;padding-top:16px;display:flex;justify-content:space-between;align-items:center">
                  <span style="color:#94a3b8;font-weight:700;font-size:14px">FINAL SCORE</span>
                  <span style="color:{score_color};font-size:2rem;font-weight:900">{score}<span style="font-size:1rem;color:#64748b">/10</span></span>
                </div>
              </div>
            </div>"""

        # ── Architecture diagram section ─────────────────────────────────────
        arch_svg = '''<svg width="100%" viewBox="0 0 680 320" style="margin:0">
<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="#7c3aed" stroke-width="1.5"/></marker></defs>
<rect x="0" y="0" width="680" height="320" fill="#0f172a" rx="12"/>
<!-- Input -->
<rect x="20" y="20" width="120" height="36" rx="6" fill="#1e293b" stroke="#334155" stroke-width="0.5"/>
<text x="80" y="38" fill="#94a3b8" font-size="11" text-anchor="middle" font-family="Arial">Startup Input</text>
<!-- Orchestrator -->
<rect x="200" y="20" width="280" height="36" rx="6" fill="#4f46e520" stroke="#7c3aed" stroke-width="1"/>
<text x="340" y="38" fill="#a78bfa" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">DueDiligencePipeline (Orchestrator)</text>
<!-- Phase 2 agents -->
<rect x="20" y="100" width="110" height="30" rx="5" fill="#1e3a5f" stroke="#3b82f6" stroke-width="0.5"/>
<text x="75" y="119" fill="#93c5fd" font-size="10" text-anchor="middle" font-family="Arial">📊 Market</text>
<rect x="142" y="100" width="110" height="30" rx="5" fill="#1e3a5f" stroke="#3b82f6" stroke-width="0.5"/>
<text x="197" y="119" fill="#93c5fd" font-size="10" text-anchor="middle" font-family="Arial">👥 Team</text>
<rect x="264" y="100" width="110" height="30" rx="5" fill="#1e3a5f" stroke="#3b82f6" stroke-width="0.5"/>
<text x="319" y="119" fill="#93c5fd" font-size="10" text-anchor="middle" font-family="Arial">🚀 Product</text>
<rect x="386" y="100" width="110" height="30" rx="5" fill="#1e3a5f" stroke="#3b82f6" stroke-width="0.5"/>
<text x="441" y="119" fill="#93c5fd" font-size="10" text-anchor="middle" font-family="Arial">💰 Financial</text>
<rect x="508" y="100" width="130" height="30" rx="5" fill="#1e3a5f" stroke="#3b82f6" stroke-width="0.5"/>
<text x="573" y="119" fill="#93c5fd" font-size="10" text-anchor="middle" font-family="Arial">🔍 Competitive</text>
<!-- Risk -->
<rect x="230" y="180" width="220" height="30" rx="5" fill="#451a0320" stroke="#f59e0b" stroke-width="0.8"/>
<text x="340" y="199" fill="#fcd34d" font-size="10" text-anchor="middle" font-family="Arial">⚠️ Risk Assessment Agent</text>
<!-- Committee -->
<rect x="160" y="240" width="360" height="30" rx="5" fill="#4c1d9520" stroke="#8b5cf6" stroke-width="0.8"/>
<text x="340" y="259" fill="#c4b5fd" font-size="10" text-anchor="middle" font-family="Arial">🏦 Investment Committee Agent → Verdict + Score</text>
<!-- Outputs -->
<rect x="100" y="295" width="100" height="20" rx="4" fill="#14532d" stroke="#16a34a" stroke-width="0.5"/>
<text x="150" y="308" fill="#86efac" font-size="9" text-anchor="middle" font-family="Arial">HTML Dashboard</text>
<rect x="215" y="295" width="90" height="20" rx="4" fill="#14532d" stroke="#16a34a" stroke-width="0.5"/>
<text x="260" y="308" fill="#86efac" font-size="9" text-anchor="middle" font-family="Arial">Markdown</text>
<rect x="320" y="295" width="90" height="20" rx="4" fill="#14532d" stroke="#16a34a" stroke-width="0.5"/>
<text x="365" y="308" fill="#86efac" font-size="9" text-anchor="middle" font-family="Arial">JSON Report</text>
<!-- Arrows -->
<line x1="140" y1="38" x2="198" y2="38" stroke="#7c3aed" stroke-width="0.8" marker-end="url(#ar)"/>
<line x1="340" y1="56" x2="340" y2="98" stroke="#7c3aed" stroke-width="0.8" marker-end="url(#ar)"/>
<line x1="75" y1="130" x2="310" y2="178" stroke="#7c3aed" stroke-width="0.5" marker-end="url(#ar)"/>
<line x1="340" y1="130" x2="340" y2="178" stroke="#7c3aed" stroke-width="0.5" marker-end="url(#ar)"/>
<line x1="573" y1="130" x2="370" y2="178" stroke="#7c3aed" stroke-width="0.5" marker-end="url(#ar)"/>
<line x1="340" y1="210" x2="340" y2="238" stroke="#7c3aed" stroke-width="0.8" marker-end="url(#ar)"/>
<line x1="270" y1="270" x2="200" y2="293" stroke="#16a34a" stroke-width="0.5" marker-end="url(#ar)"/>
<line x1="340" y1="270" x2="340" y2="293" stroke="#16a34a" stroke-width="0.5" marker-end="url(#ar)"/>
<line x1="400" y1="270" x2="415" y2="293" stroke="#16a34a" stroke-width="0.5" marker-end="url(#ar)"/>
<!-- Labels -->
<text x="340" y="80" fill="#475569" font-size="9" text-anchor="middle" font-family="Arial">Phase 2 — Parallel (Ollama llama3.2)</text>
<text x="340" y="168" fill="#475569" font-size="9" text-anchor="middle" font-family="Arial">Phase 3 — Sequential</text>
<text x="340" y="228" fill="#475569" font-size="9" text-anchor="middle" font-family="Arial">Phase 4 — Synthesis</text>
</svg>'''

        scoring_svg = '''<svg width="100%" viewBox="0 0 680 200" style="margin:0">
<rect x="0" y="0" width="680" height="200" fill="#0f172a" rx="12"/>
<text x="340" y="24" fill="#475569" font-size="11" text-anchor="middle" font-family="Arial">Scoring Model — weighted composite</text>
<rect x="20" y="35" width="88" height="50" rx="6" fill="#1e293b" stroke="#7c3aed" stroke-width="0.8"/>
<text x="64" y="58" fill="#a78bfa" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">Team</text>
<text x="64" y="74" fill="#7c3aed" font-size="10" text-anchor="middle" font-family="Arial">25%</text>
<rect x="120" y="35" width="88" height="50" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="0.8"/>
<text x="164" y="58" fill="#93c5fd" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">Market</text>
<text x="164" y="74" fill="#3b82f6" font-size="10" text-anchor="middle" font-family="Arial">20%</text>
<rect x="220" y="35" width="88" height="50" rx="6" fill="#1e293b" stroke="#3b82f6" stroke-width="0.8"/>
<text x="264" y="58" fill="#93c5fd" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">Product</text>
<text x="264" y="74" fill="#3b82f6" font-size="10" text-anchor="middle" font-family="Arial">20%</text>
<rect x="320" y="35" width="88" height="50" rx="6" fill="#1e293b" stroke="#10b981" stroke-width="0.8"/>
<text x="364" y="58" fill="#6ee7b7" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">Finance</text>
<text x="364" y="74" fill="#10b981" font-size="10" text-anchor="middle" font-family="Arial">15%</text>
<rect x="420" y="35" width="88" height="50" rx="6" fill="#1e293b" stroke="#f59e0b" stroke-width="0.8"/>
<text x="464" y="58" fill="#fcd34d" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">Comp</text>
<text x="464" y="74" fill="#f59e0b" font-size="10" text-anchor="middle" font-family="Arial">10%</text>
<rect x="520" y="35" width="88" height="50" rx="6" fill="#1e293b" stroke="#ef4444" stroke-width="0.8"/>
<text x="564" y="58" fill="#fca5a5" font-size="11" text-anchor="middle" font-family="Arial" font-weight="bold">Risk</text>
<text x="564" y="74" fill="#ef4444" font-size="10" text-anchor="middle" font-family="Arial">10%</text>
<path d="M64 85 L340 140" stroke="#7c3aed" stroke-width="0.5" fill="none"/>
<path d="M164 85 L340 140" stroke="#3b82f6" stroke-width="0.5" fill="none"/>
<path d="M264 85 L340 140" stroke="#3b82f6" stroke-width="0.5" fill="none"/>
<path d="M364 85 L340 140" stroke="#10b981" stroke-width="0.5" fill="none"/>
<path d="M464 85 L340 140" stroke="#f59e0b" stroke-width="0.5" fill="none"/>
<path d="M564 85 L340 140" stroke="#ef4444" stroke-width="0.5" fill="none"/>
<rect x="220" y="140" width="240" height="50" rx="8" fill="#1a1a2e" stroke="#8b5cf6" stroke-width="1.5"/>
<text x="340" y="162" fill="#c4b5fd" font-size="13" text-anchor="middle" font-family="Arial" font-weight="bold">Composite Score /10</text>
<text x="340" y="180" fill="#7c3aed" font-size="10" text-anchor="middle" font-family="Arial">→ Verdict: INVEST / HOLD / PASS</text>
</svg>'''

        # ── Final HTML ───────────────────────────────────────────────────────
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>AI Due Diligence — {startup}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#080c10;--surface:#0d1117;--card:#111827;
  --border:#1e293b;--muted:#334155;--text:#cbd5e1;--bright:#f1f5f9;
  --accent:#7c3aed;--green:#4ade80;--amber:#fbbf24;--red:#f87171;
}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;font-size:14px;line-height:1.6;min-height:100vh}}
body::before{{content:'';position:fixed;inset:0;z-index:0;background-image:radial-gradient(ellipse at 20% 50%,#7c3aed08 0%,transparent 50%),radial-gradient(ellipse at 80% 20%,#06b6d408 0%,transparent 50%);pointer-events:none}}
.wrap{{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 20px 80px}}

/* ── HEADER ── */
.site-header{{background:rgba(13,17,23,.95);border-bottom:1px solid #1e293b;padding:0 20px;position:sticky;top:0;z-index:100;backdrop-filter:blur(12px)}}
.header-inner{{max-width:1200px;margin:0 auto;display:flex;align-items:center;gap:16px;height:64px;flex-wrap:wrap}}
.startup-badge{{display:flex;align-items:center;gap:10px}}
.startup-logo{{width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#7c3aed,#4f46e5);display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#fff}}
.startup-name{{font-size:1.2rem;font-weight:800;color:var(--bright)}}
.status-badge{{display:flex;align-items:center;gap:6px;background:#00ff8710;border:1px solid #00ff8740;border-radius:20px;padding:4px 12px;font-size:12px;color:#4ade80;font-weight:600}}
.status-dot{{width:7px;height:7px;border-radius:50%;background:#4ade80;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
.header-actions{{margin-left:auto;display:flex;gap:8px}}
.btn{{padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;border:none;transition:all .2s;text-decoration:none;display:inline-flex;align-items:center;gap:6px}}
.btn-primary{{background:var(--accent);color:#fff}}
.btn-primary:hover{{background:#6d28d9;transform:translateY(-1px)}}
.btn-outline{{background:transparent;color:var(--text);border:1px solid var(--border)}}
.btn-outline:hover{{border-color:var(--accent);color:var(--bright)}}

/* ── TABS ── */
.tabs-nav{{display:flex;gap:4px;border-bottom:1px solid var(--border);margin:24px 0 0;overflow-x:auto;padding-bottom:0}}
.tab-btn{{padding:10px 18px;border:none;background:transparent;color:#64748b;font-size:13px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;transition:all .2s;white-space:nowrap;display:flex;align-items:center;gap:6px}}
.tab-btn:hover{{color:var(--bright)}}
.tab-btn.active{{color:var(--accent);border-bottom-color:var(--accent)}}
.tab-pane{{display:none;padding-top:24px;animation:fadeUp .3s ease}}
.tab-pane.active{{display:block}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}

/* ── CARDS ── */
.glass-card{{background:#111827;border:1px solid #1e293b;border-radius:12px;padding:20px 22px;margin-bottom:4px}}
.glass-card:hover{{border-color:#334155;transition:border-color .2s}}
.metric-card{{transition:transform .2s,border-color .2s}}
.metric-card:hover{{transform:translateY(-2px);border-color:#334155!important}}

/* ── AGENT STATUS ── */
.agent-status-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;margin:20px 0}}
.agent-pill{{background:#111827;border:1px solid #1e293b;border-radius:8px;padding:10px 14px;display:flex;align-items:center;gap:8px;font-size:13px}}
.agent-pill.running{{border-color:#f59e0b;animation:borderPulse 1.5s infinite}}
.agent-pill.done{{border-color:#4ade80}}
.agent-pill.pending{{opacity:.5}}
@keyframes borderPulse{{0%,100%{{border-color:#f59e0b}}50%{{border-color:#f59e0b80}}}}
.agent-spinner{{width:14px;height:14px;border-radius:50%;border:2px solid #f59e0b;border-top-color:transparent;animation:spin .8s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.agent-check{{color:#4ade80;font-size:14px}}

/* ── DIAGRAMS ── */
.diagram-section{{margin:32px 0}}
.diagram-title{{color:#64748b;font-size:11px;letter-spacing:.15em;text-transform:uppercase;margin-bottom:12px}}

/* ── MISC ── */
.section-label{{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:#64748b;margin-bottom:16px}}
pre{{font-family:'JetBrains Mono',monospace;font-size:11px;color:#64748b;white-space:pre-wrap;word-break:break-all}}
@media print{{
  .site-header,.tabs-nav,.header-actions{{display:none!important}}
  .tab-pane{{display:block!important;page-break-inside:avoid}}
  body{{background:#fff;color:#000}}
}}
@media(max-width:640px){{
  .header-inner{{height:auto;padding:12px 0}}
  .header-actions{{margin-left:0;width:100%}}
  .tab-btn{{padding:8px 12px;font-size:12px}}
}}
</style>
</head>
<body>

<!-- ── HEADER ── -->
<header class="site-header">
  <div class="header-inner">
    <div class="startup-badge">
      <div class="startup-logo">{startup[0].upper()}</div>
      <div>
        <div class="startup-name">{startup}</div>
        <div style="font-size:11px;color:#475569">Due Diligence Report · {generated}</div>
      </div>
    </div>
    <div class="status-badge"><span class="status-dot"></span>Analysis Complete</div>
    <div class="header-actions">
      <button class="btn btn-outline" onclick="window.print()">🖨️ Print / PDF</button>
      <button class="btn btn-outline" onclick="exportJSON()">📥 Export JSON</button>
      <button class="btn btn-primary" onclick="scrollToVerdict()">🎯 Final Verdict</button>
    </div>
  </div>
</header>

<div class="wrap">

  <!-- ── TABS NAV ── -->
  <nav class="tabs-nav">
    <button class="tab-btn active" onclick="showTab('overview','overview')">🏠 Overview</button>
    <button class="tab-btn" onclick="showTab('market','market')">📊 Market</button>
    <button class="tab-btn" onclick="showTab('team','team')">👥 Team</button>
    <button class="tab-btn" onclick="showTab('product','product')">🚀 Product</button>
    <button class="tab-btn" onclick="showTab('financials','financials')">💰 Financials</button>
    <button class="tab-btn" onclick="showTab('competitive','competitive')">🔍 Competition</button>
    <button class="tab-btn" onclick="showTab('verdict','verdict')" id="verdict-tab-btn">🎯 Final Verdict</button>
    <button class="tab-btn" onclick="showTab('diagrams','diagrams')">📐 Diagrams</button>
  </nav>

  <!-- ── TAB PANES ── -->
  {overview_tab()}
  {market_tab()}
  {team_tab()}
  {product_tab()}
  {financial_tab()}
  {competitive_tab()}
  {verdict_tab()}

  <!-- ── DIAGRAMS TAB ── -->
  <div class="tab-pane" id="tab-diagrams">
    <div class="diagram-section">
      <div class="diagram-title">System Architecture</div>
      {arch_svg}
    </div>
    <div class="diagram-section" style="margin-top:24px">
      <div class="diagram-title">Scoring Model</div>
      {scoring_svg}
    </div>
    <div class="glass-card" style="margin-top:24px">
      <h3 style="color:#94a3b8;font-size:12px;letter-spacing:.1em;margin-bottom:16px">📋 EXECUTION FLOW</h3>
      <div style="display:flex;flex-direction:column;gap:8px">
        '<div style="display:flex;gap:12px;align-items:center;background:#1e293b;border-radius:8px;padding:12px;margin-bottom:8px"><div style="background:#334155;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:12px;flex-shrink:0">1</div><div><div style="color:#e2e8f0;font-weight:600">Data Collection</div><div style="color:#64748b;font-size:12px">Scrape website URL + parse PDF pitch deck</div></div></div><div style="display:flex;gap:12px;align-items:center;background:#1e293b;border-radius:8px;padding:12px;margin-bottom:8px"><div style="background:#4f46e5;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:12px;flex-shrink:0">2</div><div><div style="color:#e2e8f0;font-weight:600">Parallel Agent Analysis</div><div style="color:#64748b;font-size:12px">Market, Team, Product, Financial, Competitive — run concurrently via Ollama</div></div></div><div style="display:flex;gap:12px;align-items:center;background:#1e293b;border-radius:8px;padding:12px;margin-bottom:8px"><div style="background:#d97706;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:12px;flex-shrink:0">3</div><div><div style="color:#e2e8f0;font-weight:600">Risk Assessment</div><div style="color:#64748b;font-size:12px">Risk agent reads all prior summaries and identifies compounded risks</div></div></div><div style="display:flex;gap:12px;align-items:center;background:#1e293b;border-radius:8px;padding:12px;margin-bottom:8px"><div style="background:#7c3aed;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:12px;flex-shrink:0">4</div><div><div style="color:#e2e8f0;font-weight:600">Investment Committee</div><div style="color:#64748b;font-size:12px">Weighted scoring, final verdict + investment memo</div></div></div><div style="display:flex;gap:12px;align-items:center;background:#1e293b;border-radius:8px;padding:12px"><div style="background:#16a34a;width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:12px;flex-shrink:0">5</div><div><div style="color:#e2e8f0;font-weight:600">Report Generation</div><div style="color:#64748b;font-size:12px">HTML dashboard + Markdown memo + JSON report saved and opened in browser</div></div></div>'
      </div>
    </div>
    <details style="margin-top:20px">
      <summary style="cursor:pointer;color:var(--accent);font-size:13px;padding:12px;background:#111827;border-radius:8px">🗂️ Full JSON Report Data</summary>
      <div class="glass-card" style="margin-top:8px;overflow-x:auto;max-height:500px;overflow-y:auto">
        <pre>{report_json_str[:8000]}</pre>
      </div>
    </details>
  </div>

</div><!-- /wrap -->

<script>
function showTab(id, name) {{
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const pane = document.getElementById('tab-' + id);
  if (pane) pane.classList.add('active');
  event.target.classList.add('active');
}}
function scrollToVerdict() {{
  document.getElementById('verdict-tab-btn').click();
  window.scrollTo({{top:0,behavior:'smooth'}});
}}
function exportJSON() {{
  const data = {json.dumps(json.dumps(report, default=str))};
  const blob = new Blob([data], {{type:'application/json'}});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '{startup.replace(" ","_")}_diligence.json';
  a.click();
}}
// Animate score bars on load
window.addEventListener('load', () => {{
  setTimeout(() => {{
    document.querySelectorAll('[data-animate-width]').forEach(el => {{
      el.style.width = el.dataset.animateWidth;
    }});
  }}, 200);
}});
</script>
</body>
</html>"""
