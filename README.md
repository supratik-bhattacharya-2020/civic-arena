```
   ___  _       _        _
  / __\(_)_   _(_) ___  / \   _ __ ___ _ __   __ _
 / /   | \ \ / / |/ __// _ \ | '__/ _ \ '_ \ / _` |
/ /___ | |\ V /| | (__/ ___ \| | |  __/ | | | (_| |
\____/ |_| \_/ |_|\___\_/ \_/_|  \___|_| |_|\__,_|
```

# CivicArena

**Drop a policy question, pick a city, and watch AI citizens go at it.**

CivicArena generates a panel of diverse citizen-agents — each with their own background, values, and research — and runs them through a structured 4-round deliberation. They argue, challenge each other, find common ground, and vote. A judge scores the whole thing on discourse quality using the [Discourse Quality Index](https://en.wikipedia.org/wiki/Discourse_quality_index).

It's messy, opinionated, and surprisingly insightful. Like a town hall meeting, minus the three-hour parking debate.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![License MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Status Alpha](https://img.shields.io/badge/status-alpha-orange)]()
[![Tests 43](https://img.shields.io/badge/tests-43_passing-brightgreen)]()

<p align="center">
  <img src="assets/demo.svg" alt="CivicArena Demo — London plastic bags deliberation" width="100%">
</p>

---

## Try It in 30 Seconds

```sh
pip install civicarena
python -m civicarena --demo --cached
```

> The `--cached` flag runs a pre-recorded debate — **no API key needed**. See a full London plastic bags deliberation with 5 agents, 4 rounds, votes, and DQI scoring, right in your terminal.

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

---

<details>
<summary><strong>Sample Output</strong> — London plastic bags debate (click to expand)</summary>

```
╭────────────────────────────────────────────────────╮
│ CivicArena — Multi-Agent Civic Deliberation        │
╰────────────────────────────────────────────────────╯

Topic: Should we ban plastic bags?
Location: London

            Citizen Agents
┌─────────────────────┬─────┬──────────────────────────────┬─────────────────┬────────────┐
│ Name                │ Age │ Occupation                   │ Stance          │ Style      │
├─────────────────────┼─────┼──────────────────────────────┼─────────────────┼────────────┤
│ Priya Sharma        │  42 │ Corner shop owner            │ AGAINST         │ pragmatic  │
│ James Whitfield     │  29 │ Marine conservation research │ STRONGLY FOR    │ passionate │
│ Dorothy "Dot" Pemb… │  71 │ Retired headteacher          │ FOR             │ measured   │
│ Kai Morgan          │  24 │ Deliveroo rider & student    │ NEUTRAL         │ direct     │
│ Councillor Amara O… │  55 │ Southwark Council member     │ FOR             │ diplomatic │
└─────────────────────┴─────┴──────────────────────────────┴─────────────────┴────────────┘

─────────────── Round 1: Opening Statements ───────────────

  Priya Sharma:
  Look, I care about the environment — I've got grandchildren. But I've
  already switched to charging 10p per bag, and my costs went up 15%.
  Paper bags tear, customers complain, and the big supermarkets can
  absorb costs I can't. The 5p charge already cut usage by 95%. Why ban
  something that's already working?

  James Whitfield:
  I pull plastic bags out of the Thames every week. The charge reduced
  usage in shops, yes — but 1.5 billion single-use bags are still
  produced annually in the UK. My research shows microplastic levels in
  Thames sediment are three times above safe thresholds. We need a full
  ban with a proper transition period.

        ...rounds 2–3 omitted for brevity...

─────────────── Round 4: Final Positions ───────────────

  Priya Sharma:
  I came in against this, and honestly, I'm still nervous. But the
  phased approach with real grants changes things. If I get £3,000
  upfront and 6 months to adjust, I can make it work. My vote: neutral.

  Kai Morgan:
  I walked in thinking this was just another policy that ignores people
  like me. The 18-month delivery window and making platforms pay changed
  my mind. My vote: for.

────────────────── Final Votes ──────────────────

  Priya Sharma:        NEUTRAL
  James Whitfield:     STRONGLY FOR
  Dorothy "Dot" Pemb:  FOR
  Kai Morgan:          FOR
  Councillor Amara O:  FOR

  FOR                  ############ (3)
  STRONGLY FOR         #### (1)
  NEUTRAL              #### (1)

──────────── Deliberation Quality Score ────────────

┌──────────────────────┬───────┬─────┐
│ Metric               │ Score │ Max │
├──────────────────────┼───────┼─────┤
│ Justification        │     3 │   3 │
│ Respect              │     2 │   2 │
│ Constructive Politics│     2 │   2 │
│ Overall Quality      │     9 │  10 │
└──────────────────────┴───────┴─────┘

Summary: Exceptional deliberation. All participants cited evidence,
engaged directly with opposing arguments, and converged on a concrete
compromise. Priya's stance shift from against to neutral demonstrated
genuine persuasion through dialogue.

Highlights:
  + Kai's delivery exemption argument introduced a practical concern
    no one else had considered
  + Dot synthesized everyone's positions into a workable proposal
  + Every participant cited specific data to support their claims
```

</details>

---

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

# Export a shareable transcript
python -m civicarena --demo --cached --export transcript.md
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

The judge evaluates using a subset of the [Discourse Quality Index](https://en.wikipedia.org/wiki/Discourse_quality_index) (DQI), developed by [Steenbergen et al. (2003)](https://doi.org/10.1177/0010414003251054) for measuring the quality of deliberative discourse:

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
  --cached                 Use cached results (no API key needed)
  -e, --export FILE        Export transcript to Markdown
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
├── export.py         # Markdown transcript export
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

## Research Background

CivicArena is grounded in real political science research on deliberative democracy:

- **Discourse Quality Index (DQI)** — [Steenbergen, M. R., et al. (2003). "Measuring Political Deliberation: A Discourse Quality Index."](https://doi.org/10.1177/0010414003251054) *Comparative Political Studies, 36*(1-2), 21-48. The foundational paper for measuring the quality of political deliberation along dimensions of justification, respect, and constructive politics.

- **Deliberative Democracy** — [Fishkin, J. S. (2009). *When the People Speak: Deliberative Democracy and Public Consultation.*](https://global.oup.com/academic/product/when-the-people-speak-9780199604432) Oxford University Press. Foundational work on structured public deliberation.

- **Multi-Agent Debate** — CivicArena extends the emerging field of LLM-based multi-agent debate systems by grounding agents in web research and location-specific demographics, producing debates that reflect real community dynamics rather than generic arguments.

## Built With

[Rich](https://github.com/Textualize/rich) · [Pydantic](https://docs.pydantic.dev/) · [httpx](https://www.python-httpx.org/) · [DuckDuckGo Search](https://github.com/deedy5/duckduckgo_search) · [python-dotenv](https://github.com/theskumar/python-dotenv)

## Roadmap

- **GUI version** — web-based interface is actively in development
- Multi-language deliberations
- Custom persona templates
- Seed control for reproducible runs
- More export formats (JSON, CSV, HTML)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.

## License

MIT
