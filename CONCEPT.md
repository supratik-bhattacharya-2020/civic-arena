# CivicArena — Concept Document

## Vision

CivicArena is a multi-agent civic deliberation platform where AI citizen-agents debate real policy issues using structured democratic protocols. Each agent is grounded in real web research and represents a distinct demographic perspective specific to a chosen location.

## Two Audiences

### Arena Mode (Viral)
- Fast, opinionated, personality-driven debates
- Rich terminal output with streaming, colors, and drama
- Shareable summaries and vote tallies
- "Who would win?" framing

### Lab Mode (Academic)
- Discourse Quality Index (DQI) scoring
- Structured rounds with formal protocols
- Exportable transcripts for research
- Reproducible with seed control

## How It Works

### 1. Topic & Location Selection
User provides a policy question and location (e.g., "Should we ban plastic bags?" in London). The system researches local context — existing laws, demographics, economic factors.

### 2. Persona Generation
The system generates 4-6 diverse citizen-agents representing the location's demographics:
- A small business owner worried about costs
- An environmental activist pushing for change
- A working parent focused on convenience
- A local council member balancing interests
- A university student with idealistic views
- A retired teacher with historical perspective

Each persona has: name, age, occupation, background, core values, communication style, and initial stance.

### 3. Web Research & Worldview Assembly
Each agent independently researches the topic from their perspective:
- DuckDuckGo searches tailored to their concerns
- Facts filtered through their value system
- Sources cited in their arguments
- Local context prioritized

### 4. Structured Deliberation (4 Rounds)

**Round 1 — Opening Statements**
Each agent presents their initial position with supporting evidence.

**Round 2 — Cross-Examination**
Agents challenge each other's claims with questions and counter-evidence.

**Round 3 — Common Ground**
Agents identify areas of agreement and propose compromises.

**Round 4 — Final Positions**
Each agent presents their (potentially updated) position and votes.

### 5. Civility Rules
All agents must:
- Cite sources for factual claims
- Acknowledge valid points from opponents
- Avoid personal attacks (focus on arguments)
- Use respectful language
- Show willingness to update views when presented with evidence

### 6. Judging (DQI Subset)
A judge agent scores the deliberation on:
- **Justification Level** (0-3): Are claims backed by reasons and evidence?
- **Respect** (0-2): Do participants treat each other with dignity?
- **Constructive Politics** (0-2): Are concrete proposals offered?
- **Overall Quality** (0-10): Holistic assessment

## Demo Topics

1. "Should we ban plastic bags?" — London
2. "Should public transit be free?" — New York City
3. "Should AI-generated art be copyrightable?" — San Francisco
4. "Should universities have speech codes?" — Oxford
5. "Should remote work be a legal right?" — Berlin

## Technical Design

### Search Provider Protocol
Pluggable search backends:
- **DuckDuckGo** (default) — free, zero config
- **SearXNG** — self-hosted, privacy-focused
- **Google CSE** — paid, for researchers needing precision

### LLM Backend
OpenAI-compatible API client that works with:
- copilot-api proxy (default — free via GitHub Copilot)
- Any OpenAI-compatible endpoint
- Configurable via `OPENAI_API_KEY` and `OPENAI_BASE_URL`

### Caching
- Search results cached to disk for offline demo
- LLM responses optionally cached for reproducibility
