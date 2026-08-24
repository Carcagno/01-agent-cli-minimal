# Agent CLI Minimal

A minimal command-line agent built from scratch on top of Anthropic's raw Messages API — no agent framework, no MCP. It implements the core agent loop (decide → act → observe) and tool use (function calling) by hand, in order to understand the underlying mechanics before relying on higher-level abstractions.

## What this demonstrates

- **Agent loop from scratch** — a hand-written loop driving decision, tool execution, and observation, with a conversation context that grows across turns.
- **Tool use / function calling** — custom tools defined as a JSON schema (what the model sees) cleanly separated from their Python implementation (what actually runs). The model never has access to the implementation or to any credentials it might use.
- **Multi-tool selection and parallel tool calls** — two independent tools (`calculator`, `current_datetime`); the model correctly picks between them, and can request both in a single turn when a query needs it.
- **Failure handling** — unknown tool names and exceptions raised inside a tool implementation are caught and reported back to the model as a normal result, instead of crashing the loop.
- **Secrets management** — the API key is never hardcoded; it's loaded from a local `.env` file (excluded from version control) via `python-dotenv`.
- **Testable design** — the "brain" that decides what to do is swappable: a scripted mock (`fake_brain.py`) lets the entire loop be built and debugged at zero API cost, before wiring in the real model (`real_brain.py`).

## How it's organized

| File | Responsibility |
|---|---|
| `tools.py` | Tool schemas (what the model is told) and their real implementations (what actually runs) |
| `fake_brain.py` | A scripted stand-in for the model, for cost-free testing of the loop's plumbing |
| `real_brain.py` | The real model call (Claude Haiku via the Anthropic API), normalized to the same response shape as the mock |
| `agent.py` | The agent loop itself: turn management, tool dispatch, failure handling, interactive REPL |

`agent.py` picks `real_brain` or `fake_brain` automatically, based on whether an API key is configured — nothing else changes.

## Running it

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash); use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp .env.example .env            # then fill in your ANTHROPIC_API_KEY
python agent.py
```

Without an API key, it still runs against the scripted mock, at zero cost.

## Cost

Each real exchange costs a fraction of a cent on Claude Haiku 4.5 (current Anthropic pricing: roughly $1 / $5 per million input/output tokens). This project was built and iterated on for well under $1 total.

## Context

This is the first project in a self-directed, project-based learning path in agentic AI (agent loop, tool use, MCP, orchestration...), built incrementally through small, functional projects rather than isolated exercises.
