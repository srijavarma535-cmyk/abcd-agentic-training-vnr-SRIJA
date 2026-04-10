1.  Business Problem

Venture Capital (VC) due diligence is the backbone of sound investment decisions — yet it is one of the most expensive, slow, and resource-intensive workflows in finance.

The core problem

•	A single due diligence report takes 2–4 weeks involving analysts, associates, and partners.
•	Each report costs firms $10,000–$50,000+ in analyst hours.
•	Early-stage investors and angel investors have no affordable way to get structured analysis.
•	Manual research is inconsistent — two analysts can reach different conclusions on the same startup.
•	Startups themselves struggle to self-assess objectively before approaching investors.


Who is affected

Stakeholder	               Pain Point
VC Analysts	            Weeks of manual research per deal
Angel Investors	         No affordable structured analysis tool
Startup Founders	    Cannot simulate how a VC views them
Accelerators	         Too many applicants to review manually
Corporate VCs      	Slow pipeline velocity due to research backlog

Bottom line: professional-grade investment research is too slow, too expensive, and too inconsistent for the pace of modern startup ecosystems.


2.  Possible Solution

Several approaches exist to automate parts of due diligence:

Approach	                Limitation
Hire more analysts	      Scales cost linearly, not efficiency
Single LLM prompt	Shallow, unstructured, hallucination-prone
Off-the-shelf BI tools	No qualitative reasoning, no scoring
Paid AI research tools	Expensive SaaS ($500–$5000/mo), black box
Multi-Agent AI System	Structured, parallel, consistent — our choice

Why multi-agent?
•	Each agent is a specialist — focused prompts outperform generalist mega-prompts.
•	Parallel execution reduces total time from weeks to under 60 seconds.
•	Structured JSON output makes scoring deterministic and auditable.
•	Modular design means any agent can be improved or replaced independently.

The ideal solution is an AI team that mirrors a VC firm: specialist analysts working in parallel, overseen by a committee that synthesises findings into a final verdict.


3.  Implemented Solution

The AI VC Due Diligence Agent Team is a free, open-source Python application that simulates a full VC due diligence workflow using 7 specialist AI agents powered by Google Gemini (free tier, 1500 requests/day).

How it works — 4 phases
1.	Data Collection — scrapes the startup website (optional) and parses the pitch deck PDF (optional).
2.	Parallel Agent Analysis — 5 specialist agents analyse different dimensions simultaneously.
3.	Risk Assessment — a dedicated risk agent reads all 5 prior summaries and identifies compounded risks.
4.	Investment Committee — a final agent computes a weighted score, verdict, and full investment memo.

The 7 agents:
Agent	                                What it produces
Market Analysis	                     TAM/SAM/SOM, growth rate, timing score
Team Analysis	                     Founder scoring, gaps, track record
Product Analysis	             PMF score, moat, scalability
Financial Analysis	             ARR estimate, burn, unit economics
Competitive Intelligence	     Competitor map, differentiation score
Risk Assessment	                     Regulatory, tech, macro risks
Investment Committee	             Weighted score /10, verdict, investment memo

Key features

•	100% free — uses Google Gemini free tier, no credit card needed.
•	Auto model fallback — if quota is hit, system tries the next available Gemini model.
•	Rate limit protection — batched execution with smart retry and delay.
•	3 output formats — beautiful HTML webpage, Markdown memo, and raw JSON.
•	Auto browser launch — HTML report opens automatically after each run.
•	Streamlit web UI — browser-based interface for non-technical users.
•	CLI interface — scriptable for batch processing multiple startups.
•	Unit tested — mocked tests require no API key.

Sample output verdict scale

Score Range	Verdict
8.5 – 10.0	Strong Pass
7.0 – 8.4	Pass
5.5 – 6.9	Conditional Pass
4.5 – 5.4	Soft Pass
Below 4.5	No Go


4.  Tech Stack Used

Component	Technology / Library
AI Engine	Google Gemini 1.5 Flash Latest (Free tier)
Language	Python 3.10+
API Client	Python stdlib urllib (no extra package needed)
Web Scraping	httpx + BeautifulSoup4
PDF Parsing	pdfplumber
Web UI	Streamlit
Env Management	python-dotenv
Testing	pytest + unittest.mock
Report — HTML	Custom HTML/CSS generator (zero deps)
Report — Markdown	Custom generator (zero deps)
Async Orchestration	Python asyncio
Output Formats	JSON, Markdown, HTML

Why these choices

•	Google Gemini — only major LLM provider with a permanent generous free tier.
•	stdlib urllib — zero extra dependencies for the core API calls.
•	asyncio — enables parallel agent execution, cutting runtime by ~5x.
•	Streamlit — fastest path to a usable web UI in pure Python.
•	pdfplumber — best open-source PDF text extraction accuracy.


5.  Architecture Diagram

The system is composed of 4 layers: Input, Orchestration, Agent Execution, and Output.

INPUT LAYER
Startup name  |  Website URL  |  Pitch deck PDF  |  Mode flags

↓

TOOLS LAYER
WebScraper (httpx + BS4)   |   PDFParser (pdfplumber)   |   Settings (config)

↓

ORCHESTRATOR — DueDiligencePipeline
Phase 1: Data Collection  →  Phase 2: Parallel agents  →  Phase 3: Risk  →  Phase 4: Committee

↓  (parallel, batched, with auto-retry)

Agent (Phase 2 — parallel)	Scores
Market Analysis Agent	overall_market_score /10
Team Analysis Agent	overall_team_score /10
Product Analysis Agent	overall_product_score /10
Financial Analysis Agent	overall_financial_score /10
Competitive Intelligence Agent	overall_competitive_score /10

↓  (sequential — uses all prior summaries)

Risk Assessment Agent  →  overall_risk_score /10

↓  (synthesis)

Investment Committee Agent  →  Weighted score + Verdict + Investment Memo

↓  OUTPUT

Output File	Description
startup_report.html	Beautiful scored webpage — opens in browser automatically
startup_report.md	Markdown investment memo
startup_report.json	Full structured JSON with all agent data

Fallback model chain

If any Gemini model hits a quota limit, the system automatically tries the next:
gemini-1.5-flash-latest  →  gemini-1.5-flash-8b  →  gemini-1.5-pro-latest  →  gemini-2.0-flash-lite


6.  How to Run Locally

Step 1 — Get a free Gemini API key (30 seconds)
5.	Go to:  https://aistudio.google.com/app/apikey
6.	Sign in with your Google account.
7.	Click 'Create API Key'.
8.	Copy the key — it starts with  AIza...

Step 2 — Download the project
Download the zip file from the project link
Unzip it and open a terminal in the folder:
   cd ai_vc_due_diligence

Step 3 — Install dependencies
pip install -r requirements.txt
This installs: python-dotenv, httpx, beautifulsoup4, pdfplumber, streamlit, pytest

Step 4 — Set your API key
Option A — Create a .env file in the project folder (recommended):
GEMINI_API_KEY=AIza...your_key_here...

Option B — Set in terminal (Windows CMD):
set GEMINI_API_KEY=AIza...your_key_here...

Option B — Set in terminal (Mac / Linux):
export GEMINI_API_KEY=AIza...your_key_here...

Step 5 — Run
CLI — full analysis:
python main.py --startup "Stripe" --mode full

CLI — quick mode (3 agents, fewer API calls, better for free tier):
python main.py --startup "Stripe" --mode quick

CLI — with website URL:
python main.py --startup "Stripe" --url https://stripe.com --mode full

CLI — with pitch deck PDF:
python main.py --startup "Stripe" --deck pitch.pdf --mode full

Streamlit web UI:
streamlit run ui/app.py
Open browser at:  http://localhost:8501

Run unit tests (no API key needed):
pytest tests/test_agents.py -v

Analysis modes
Mode	Agents run  |  Use case
full	All 7 agents  |  Complete analysis
quick	Market + Team + Product  |  Fast check, fewer API calls
market-only	Market agent only  |  TAM/SOM research
team-only	Team agent only  |  Founder assessment

Output location
All reports are saved to:
data/outputs/
   Stripe_report.html   ← opens in browser automatically
   Stripe_report.md
   Stripe_report.json


7.  References and Resources

APIs and services
Resource	URL / Notes
Google Gemini Free API Key	https://aistudio.google.com/app/apikey
Gemini API Documentation	https://ai.google.dev/gemini-api/docs
Gemini Rate Limits	https://ai.google.dev/gemini-api/docs/rate-limits
Serper Web Search (optional)	https://serper.dev — 2500 free searches/month

Python libraries
Library	Purpose  |  Install
python-dotenv	Load .env file  |  pip install python-dotenv
httpx	Async HTTP for web scraping  |  pip install httpx
beautifulsoup4	HTML parsing  |  pip install beautifulsoup4
pdfplumber	PDF text extraction  |  pip install pdfplumber
streamlit	Web UI  |  pip install streamlit
pytest	Unit testing  |  pip install pytest

VC due diligence frameworks referenced
•	Y Combinator's Request for Startups — market sizing methodology
•	Sequoia Capital's company narrative framework — team and product evaluation
•	a16z's market sizing framework — TAM/SAM/SOM breakdown
•	First Round Capital's due diligence checklist — risk assessment dimensions

Tools and technologies
•	Python asyncio documentation — https://docs.python.org/3/library/asyncio.html
•	Streamlit documentation — https://docs.streamlit.io
•	Google Gemini Python SDK — https://pypi.org/project/google-generativeai


8.  Recording

Demo Video
A screen recording demonstrating the full pipeline from startup name input to HTML report output.
 
Recording link: [Add your recording link here — Loom / YouTube / Google Drive]
Duration: ~3–5 minutes recommended

What the recording should cover
9.	Show the .env file setup with the Gemini API key.
10.	Run:  python main.py --startup "Stripe" --mode quick
11.	Show the terminal output — all 4 phases, agent logs, rate limit handling.
12.	Show the HTML report opening in the browser — score ring, verdict banner, agent cards.
13.	Optional: show the Streamlit UI running at localhost:8501.

Recommended recording tools
•	Loom — https://loom.com (free, shareable link)
•	OBS Studio — https://obsproject.com (free, local recording)
•	Windows built-in — Win + G  (Xbox Game Bar)
•	Mac built-in — Cmd + Shift + 5


9.  Screenshots
Add your actual screenshots by replacing the placeholder boxes below. Take screenshots of each section described.

Screenshot 1 — Terminal output
[Add screenshot here: terminal showing all 4 phases running with agent logs]
What to capture: The 4 phase headers, agent emoji logs, score outputs, and final report path.

Screenshot 2 — HTML report: hero section
[Add screenshot here: the HTML report header with score ring, verdict banner, and score bars]
What to capture: Score ring animation, colored verdict banner, animated score breakdown bars.

Screenshot 3 — HTML report: agent analysis cards
[Add screenshot here: the 6 agent analysis cards section of the HTML report]
What to capture: Each agent card with its score, summary text, and key metrics.

Screenshot 4 — HTML report: investment thesis
[Add screenshot here: bull case / bear case / investment thesis cards]
What to capture: The three thesis cards with color-coded borders.

Screenshot 5 — Streamlit UI (optional)
[Add screenshot here: the Streamlit web interface at localhost:8501]
What to capture: The sidebar with API key field, input form, and analysis mode selector.

How to take screenshots
•	Windows: Press  Win + Shift + S  to capture a region, then paste into the document.
•	Mac: Press  Cmd + Shift + 4  to capture a region.
•	Replace each placeholder box above with your actual image in the Word document.


10.  Problems Faced and Solutions

Problem	Solution Applied
API key not being read	Added python-dotenv to auto-load .env file; added clear error message pointing to setup steps
Anthropic API required paid credits	Replaced entire Anthropic integration with Google Gemini free tier; rewrote base_agent.py to use stdlib urllib — no extra package needed
Gemini model 'gemini-1.5-flash' returned 404	Fixed API version from v1beta to v1; updated model name to gemini-1.5-flash-latest
Gemini model 'gemini-2.0-flash' returned limit: 0	Added a fallback chain: flash-latest → flash-8b → pro-latest → flash-lite; system tries each automatically
429 Too Many Requests error	Changed parallel execution to batched (2 agents at a time); added 5-second pause between batches; added smart retry that reads the retryDelay from the error response
All agents failing silently	Added per-agent try/except in the pipeline; failed agents return a structured error dict so the pipeline continues instead of crashing
HTML report not rendering correctly	Rewrote the HTMLReportGenerator to produce a fully self-contained HTML file with embedded CSS and no external dependencies
JSON parsing failures from LLM output	Added markdown fence stripping logic in _call_llm_json; Gemini sometimes wraps JSON in ```json blocks
Streamlit asyncio conflict on Windows	Wrapped asyncio.run() correctly; noted Python 3.12 asyncio runner differences for Windows users
pytest failing due to Anthropic import	Replaced all Anthropic imports with Gemini client; updated all unit tests to mock _call_llm_json instead of the Anthropic client

Lessons learned
•	Always build a fallback model chain when relying on free-tier APIs — quotas are model-specific.
•	Use stdlib where possible to reduce dependencies — urllib works perfectly for simple REST calls.
•	Rate limit errors contain retry timing — parse and use it instead of hardcoding delays.
•	Test with mocks from day one — makes switching the underlying LLM provider trivial.

