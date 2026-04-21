# Agent Design — AI VC Due Diligence v5

## Why Ollama?
- 100% local — no API keys, no billing, no rate limits
- Fast inference on llama3.2 (~5-15s per agent)
- Privacy — startup data never leaves your machine

## Parallel Execution
All 5 batch-1 agents run via asyncio.gather() — concurrent, not sequential.

## Streaming
Pipeline fires on_event() callbacks → thread-safe queue → Streamlit live updates.
