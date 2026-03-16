"""Worldview assembly — researches topic from each agent's perspective."""

from __future__ import annotations

import json

from civicarena.llm import chat_completion
from civicarena.search.base import SearchProvider
from civicarena.types import LLMConfig, LLMMessage, Persona, SearchResult, Worldview

WORLDVIEW_SYSTEM_PROMPT = """\
You are assembling a worldview for a citizen participating in a civic deliberation.

Given a persona and search results about the topic, synthesize their perspective:
- Filter facts through their values and background
- Identify evidence that supports or challenges their stance
- Note their specific concerns
- Explain why they hold their position

Respond with a JSON object with these fields:
- "key_facts": array of 3-5 strings (facts most relevant to this persona)
- "supporting_evidence": array of 2-4 strings (evidence supporting their stance)
- "concerns": array of 2-3 strings (their worries or objections)
- "stance_reasoning": string (2-3 sentences explaining why they hold their position)

Respond with ONLY the JSON object, no other text.\
"""


def _build_search_queries(persona: Persona, topic: str, location: str) -> list[str]:
    """Build search queries tailored to a persona's perspective."""
    base_query = f"{topic} {location}"
    queries = [base_query]

    # Add occupation-specific query
    queries.append(f"{topic} impact on {persona.occupation} {location}")

    # Add values-based query
    if persona.core_values:
        values_str = " ".join(persona.core_values[:2])
        queries.append(f"{topic} {values_str} {location}")

    return queries


async def build_worldview(
    persona: Persona,
    topic: str,
    location: str,
    search_provider: SearchProvider,
    config: LLMConfig | None = None,
) -> Worldview:
    """Research the topic from a persona's perspective and build their worldview."""
    queries = _build_search_queries(persona, topic, location)

    # Gather search results from all queries
    all_results: list[SearchResult] = []
    seen_urls: set[str] = set()
    for query in queries:
        results = await search_provider.search(query, max_results=3)
        for r in results:
            if r.url not in seen_urls:
                all_results.append(r)
                seen_urls.add(r.url)

    # Format search results for the LLM
    search_context = "\n\n".join(
        f"Source: {r.title}\nURL: {r.url}\n{r.snippet}" for r in all_results
    )

    prompt = (
        f"Topic: {topic}\n"
        f"Location: {location}\n\n"
        f"Persona: {persona.name}, {persona.age}, {persona.occupation}\n"
        f"Background: {persona.background}\n"
        f"Core values: {', '.join(persona.core_values)}\n"
        f"Initial stance: {persona.initial_stance.value}\n\n"
        f"Search results:\n{search_context}\n\n"
        f"Build this persona's worldview on the topic."
    )

    response = await chat_completion(
        messages=[LLMMessage(role="user", content=prompt)],
        system=WORLDVIEW_SYSTEM_PROMPT,
        config=config,
        temperature=0.5,
    )

    # Parse JSON response
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    raw = json.loads(text)

    return Worldview(
        persona=persona,
        key_facts=raw["key_facts"],
        supporting_evidence=raw["supporting_evidence"],
        concerns=raw["concerns"],
        sources=all_results[:5],
        stance_reasoning=raw["stance_reasoning"],
    )
