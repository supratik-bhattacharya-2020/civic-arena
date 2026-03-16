# CivicArena

**Drop a policy question, pick a city, and watch AI citizens go at it.**

CivicArena generates a panel of diverse citizen-agents — each with their own background, values, and research — and runs them through a structured 4-round deliberation. They argue, challenge each other, find common ground, and vote. A judge scores the whole thing on discourse quality.

It's messy, opinionated, and surprisingly insightful. Like a town hall meeting, minus the three-hour parking debate.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue) ![License MIT](https://img.shields.io/badge/license-MIT-green) ![Status Alpha](https://img.shields.io/badge/status-alpha-orange)

---

## What It Does

```
$ python -m civicarena "Should we ban plastic bags?" --location London
```

1. **Generates 5 citizens** tied to your chosen location — a shop owner, an activist, a council member, a student, a retiree — each with distinct values and communication styles
2. **Researches the topic** via DuckDuckGo from each citizen's perspective, building individual worldviews with real sources
3. **Runs 4 structured rounds** of deliberation:
   - Opening Statements — stake your position
   - Cross-Examination — challenge and question
   - Common Ground — find where you agree
   - Final Positions — updated stance + vote
4. **Scores the debate** using Discourse Quality Index metrics (justification, respect, constructive proposals)
5. **Shows the vote tally** — did anyone change their mind?

All output streams to your terminal in real-time with color-coded stances.

## Quick Start

```sh
git clone https://github.com/supratik-bhattacharya-2020/civic-arena.git
cd civic-arena
pip install -e .
```

On first run, you'll be prompted for an OpenAI-compatible API key. It gets saved to `.env` (gitignored) — one-time setup.

```sh
# Interactive topic picker with 5 pre-built demos
python -m civicarena --demo

# Custom topic
python -m civicarena "Should public transit be free?" --location "New York City"

# More agents, longer responses
python -m civicarena "Should AI art be copyrightable?" -l "San Francisco" -n 6 --verbose
```

## Demo Topics

These work out of the box — just pick one:

| # | Topic | Location |
|---|-------|----------|
| 1 | Should we ban plastic bags? | London |
| 2 | Should public transit be free? | New York City |
| 3 | Should AI-generated art be copyrightable? | San Francisco |
| 4 | Should universities have speech codes? | Oxford |
| 5 | Should remote work be a legal right? | Berlin |

## How Scoring Works

The judge evaluates using a subset of the [Discourse Quality Index](https://en.wikipedia.org/wiki/Discourse_quality_index):

| Metric | Scale | What it measures |
|--------|-------|------------------|
| Justification | 0–3 | Are claims backed by evidence and reasoning? |
| Respect | 0–2 | Do participants treat each other with dignity? |
| Constructive Politics | 0–2 | Are concrete, actionable proposals offered? |
| Overall Quality | 0–10 | Holistic assessment of the deliberation |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | Your API key (prompted on first run) |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | Any OpenAI-compatible endpoint |
| `CIVICARENA_MODEL` | `gpt-4o-mini` | Model to use |
| `CIVICARENA_TEMPERATURE` | `0.7` | Response temperature |
| `CIVICARENA_MAX_TOKENS` | `2048` | Max tokens per response |

All of these can also go in a `.env` file in the project root.

### CLI Flags

```
python -m civicarena [TOPIC] [OPTIONS]

Arguments:
  TOPIC                    The policy question to debate

Options:
  -l, --location TEXT      City/region for the deliberation
  -n, --agents INT         Number of citizen-agents (default: 5)
  -m, --model TEXT         Override the LLM model
  --base-url TEXT          Override the API base URL
  --api-key TEXT           Override the API key
  -v, --verbose            Longer, more detailed responses
  --no-stream              Disable streaming output
  -d, --demo               Interactive demo topic picker
```

## Search Providers

Pluggable search backends — DuckDuckGo is the default (free, zero setup):

| Provider | Setup | Use case |
|----------|-------|----------|
| **DuckDuckGo** | None | Default, works everywhere |
| **SearXNG** | Self-hosted instance | Privacy-focused setups |
| **Google CSE** | API key + CX ID | Research requiring precision |

## Architecture

```
src/civicarena/
├── cli.py            # Terminal UI with Rich
├── personas.py       # Location-aware agent generation
├── worldview.py      # Per-agent web research + synthesis
├── protocol.py       # 4-round deliberation engine
├── judge.py          # DQI scoring
├── orchestrator.py   # Ties it all together
├── llm.py            # OpenAI-compatible client + .env setup
├── types.py          # Pydantic models
└── search/
    ├── base.py       # SearchProvider protocol
    ├── ddg.py        # DuckDuckGo
    ├── searxng.py    # SearXNG
    └── google.py     # Google CSE
```

## Running Tests

```sh
pip install -e '.[dev]'
pytest -v
```

43 tests covering types, protocol logic, search providers, config, and scoring.

## Roadmap

- **GUI version** — web-based interface is actively in development. Stay tuned.
- Cached demo results for fully offline runs
- Session export (JSON/CSV transcripts)
- Custom persona templates
- Multi-language deliberations

## License

MIT
