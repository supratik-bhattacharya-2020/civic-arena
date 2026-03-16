# CivicArena

## Overview

Multi-agent civic deliberation platform. AI citizen-agents debate policy issues using structured democratic protocols, grounded in real web research, specific to a location.

## Stack

Python 3.11+ · Rich · httpx · Pydantic · duckduckgo-search · pytest

## Commands

```sh
pip install -e '.[dev]'
pytest
python -m civicarena "Should we ban plastic bags?" --location London
```

## Architecture

- `cli.py` — Rich CLI entry, topic + location selection
- `personas.py` — generates 4-6 location-aware citizen-agents
- `search/` — pluggable search providers (DuckDuckGo default, SearXNG, Google CSE)
- `worldview.py` — assembles per-agent research into worldviews
- `protocol.py` — 4-round deliberation with civility rules
- `judge.py` — DQI-based scoring (justification + respect)
- `orchestrator.py` — manages agent turns and full deliberation flow
- `llm.py` — OpenAI-compatible LLM client (works with copilot-api proxy)
- `types.py` — shared Pydantic models

## Code Style

- ruff for linting
- Type hints everywhere
- Async-first design
- No semicolons, no trailing commas on single lines
