# Agent Design Decisions

## Why Multi-Agent?

Each dimension of VC due diligence requires distinct expertise and prompting strategy.
Splitting into specialist agents gives:
- **Better accuracy** — focused prompts outperform bloated mega-prompts
- **Parallelism** — 5 agents run concurrently, cutting total time by ~5x
- **Modularity** — swap or extend any agent without touching others
- **Debuggability** — each agent's output is independently inspectable

## Agent Sequencing

```
Phase 1 (parallel):  Market, Team, Product, Financial, Competitive
Phase 2 (sequential): Risk  ← uses Phase 1 summaries as input
Phase 3 (sequential): Committee ← uses all agent results
```

The Risk agent needs prior analysis to identify compounded risks.
The Committee agent needs all scores to compute the weighted verdict.

## Scoring Philosophy

All scores are 1–10 and weighted into a composite.
Team is weighted highest (25%) because execution beats idea at early stages.
Risk is scored inversely — a high risk score means HIGH risk (bad), so the
Committee agent treats it as a penalty, not a bonus.

## JSON-first Outputs

All agents return structured JSON.
This enables:
- Programmatic score aggregation in the Committee agent
- UI rendering without parsing freeform text
- Downstream integrations (CRM, Notion, Airtable)

## Extensibility

To add a new agent:
1. Create `agents/my_agent.py` subclassing `BaseAgent`
2. Implement `async def analyze(self, context) -> dict`
3. Register in `agents/__init__.py`
4. Add to `orchestrator/pipeline.py`
5. Add weight in `config/settings.py`
