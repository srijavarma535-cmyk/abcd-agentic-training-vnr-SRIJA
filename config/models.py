"""
Multi-model configuration.
Each agent is assigned a model suited to its task.
"""
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Planner — strong structured reasoning, JSON output
planner_llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

# Searcher — lightweight, just parses and formats search results
searcher_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Summarizer — Claude excels at synthesis and long-context condensation
summarizer_llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0.3)

# Critic — rigorous analytical scoring, needs reliability
critic_llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Optimizer — query refinement needs creative variation
optimizer_llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# Report writer — Claude excels at long-form structured professional prose
report_llm = ChatAnthropic(model="claude-sonnet-4-5", temperature=0.4)
