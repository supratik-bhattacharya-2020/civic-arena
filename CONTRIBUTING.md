# Contributing to CivicArena

Thanks for your interest in CivicArena! Here's how to get started.

## Setup

```sh
git clone https://github.com/supratik-bhattacharya-2020/civic-arena.git
cd civic-arena
pip install -e '.[dev]'
pytest -v  # verify everything works
```

## Code Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```sh
ruff check .
ruff format .
```

- Type hints everywhere
- Async-first design
- Keep functions focused — do one thing well

## How to Contribute

### Add a New Demo Topic

1. Create a cached deliberation JSON in `src/civicarena/cache/`
   - Follow the existing format in `plastic_bags_london.json`
   - Include realistic personas, worldviews, 4 rounds of statements, votes, and DQI scores
2. Register it in `src/civicarena/cache/__init__.py` (add to `CACHE_INDEX`)
3. Add it to `DEMO_TOPICS` in `src/civicarena/cli.py`
4. Update the demo topics table in `README.md`

### Add a Search Provider

1. Create a new file in `src/civicarena/search/` (e.g., `brave.py`)
2. Implement the `SearchProvider` protocol from `base.py`
3. Add it to `src/civicarena/search/__init__.py`
4. Add a row to the Search Providers table in `README.md`

### Fix a Bug or Add a Feature

1. Fork and create a branch: `git checkout -b my-feature`
2. Make your changes
3. Add tests if applicable
4. Run `pytest -v` and `ruff check .`
5. Open a pull request with a clear description

## Project Structure

```
src/civicarena/
├── cli.py            # CLI entry point (Rich terminal UI)
├── orchestrator.py   # Main deliberation flow
├── personas.py       # Persona generation
├── worldview.py      # Web research + worldview assembly
├── protocol.py       # 4-round deliberation protocol
├── judge.py          # DQI scoring
├── export.py         # Markdown transcript export
├── llm.py            # LLM client
├── types.py          # Pydantic models
├── cache/            # Cached demo deliberations
└── search/           # Pluggable search providers
```

## Good First Issues

Look for issues labeled [`good first issue`](https://github.com/supratik-bhattacharya-2020/civic-arena/labels/good%20first%20issue) — these are beginner-friendly tasks.

Ideas for new contributors:
- Add a new demo topic/location
- Improve error messages when API key is missing
- Add `--json` export format alongside `--export` markdown
- Add more test coverage for edge cases in stance extraction

## Questions?

Open an issue — we're happy to help.
