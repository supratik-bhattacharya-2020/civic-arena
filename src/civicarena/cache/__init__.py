"""Cache loader for pre-generated demo deliberations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from civicarena.types import (
    DQIScore,
    DeliberationResult,
    Persona,
    RoundResult,
    SearchResult,
    Stance,
    Statement,
    Worldview,
)

CACHE_DIR = Path(__file__).parent

# Map demo topics to cache filenames
CACHE_INDEX: dict[tuple[str, str], str] = {
    ("Should we ban plastic bags?", "London"): "plastic_bags_london.json",
    ("Should public transit be free?", "New York City"): "public_transit_nyc.json",
    ("Should AI-generated art be copyrightable?", "San Francisco"): "ai_art_copyright_sf.json",
    ("Should universities have speech codes?", "Oxford"): "speech_codes_oxford.json",
    ("Should remote work be a legal right?", "Berlin"): "remote_work_berlin.json",
}


def load_cached_result(topic: str, location: str) -> Optional[DeliberationResult]:
    """Load a cached deliberation result if available."""
    filename = CACHE_INDEX.get((topic, location))
    if not filename:
        return None

    cache_file = CACHE_DIR / filename
    if not cache_file.exists():
        return None

    data = json.loads(cache_file.read_text(encoding="utf-8"))
    return _parse_result(data)


def _parse_result(data: dict) -> DeliberationResult:
    """Parse a cached JSON result into a DeliberationResult."""
    personas = [
        Persona(
            name=p["name"],
            age=p["age"],
            occupation=p["occupation"],
            background=p["background"],
            core_values=p["core_values"],
            communication_style=p["communication_style"],
            initial_stance=Stance(p["initial_stance"]),
            location_context=p.get("location_context", ""),
        )
        for p in data["personas"]
    ]

    persona_map = {p.name: p for p in personas}

    worldviews = []
    for w in data["worldviews"]:
        persona_name = w.get("persona_name", w.get("persona", {}).get("name", ""))
        persona = persona_map.get(persona_name, personas[0])
        sources = [
            SearchResult(title=s["title"], url=s["url"], snippet=s["snippet"])
            for s in w.get("sources", [])
        ]
        worldviews.append(
            Worldview(
                persona=persona,
                key_facts=w["key_facts"],
                supporting_evidence=w["supporting_evidence"],
                concerns=w["concerns"],
                sources=sources,
                stance_reasoning=w["stance_reasoning"],
            )
        )

    rounds = []
    for r in data["rounds"]:
        statements = [
            Statement(
                persona_name=s["persona_name"],
                round_number=s["round_number"],
                round_name=s["round_name"],
                content=s["content"],
                sources_cited=s.get("sources_cited", []),
                stance=Stance(s["stance"]),
            )
            for s in r["statements"]
        ]
        rounds.append(
            RoundResult(
                round_number=r["round_number"],
                round_name=r["round_name"],
                statements=statements,
            )
        )

    final_votes = {name: Stance(stance) for name, stance in data["final_votes"].items()}

    dqi_score = None
    if data.get("dqi_score"):
        d = data["dqi_score"]
        dqi_score = DQIScore(
            justification_level=d["justification_level"],
            respect=d["respect"],
            constructive_politics=d["constructive_politics"],
            overall_quality=d["overall_quality"],
            summary=d["summary"],
            highlights=d.get("highlights", []),
            concerns=d.get("concerns", []),
        )

    return DeliberationResult(
        topic=data["topic"],
        location=data["location"],
        personas=personas,
        worldviews=worldviews,
        rounds=rounds,
        final_votes=final_votes,
        dqi_score=dqi_score,
    )
