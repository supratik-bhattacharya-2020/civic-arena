"""Persona generation — creates diverse, location-aware citizen-agents."""

from __future__ import annotations

import json

from civicarena.llm import chat_completion
from civicarena.types import LLMConfig, LLMMessage, Persona, Stance

PERSONA_SYSTEM_PROMPT = """\
You are a demographic researcher creating diverse citizen personas for a civic deliberation.
Given a policy topic and location, generate {count} distinct personas representing the local population.

Each persona must:
- Be demographically diverse (age, occupation, background, values)
- Have a plausible connection to the location
- Have a clear but varied stance on the topic (from strongly_for to strongly_against)
- Have a distinct communication style (formal, passionate, pragmatic, analytical, etc.)

Respond with a JSON array of persona objects. Each object must have exactly these fields:
- "name": string (realistic full name appropriate for the location)
- "age": integer (18-85)
- "occupation": string
- "background": string (2-3 sentences)
- "core_values": array of 2-4 strings
- "communication_style": string (one word or short phrase)
- "initial_stance": one of "strongly_for", "for", "neutral", "against", "strongly_against"
- "location_context": string (how they connect to the location)

Ensure a balanced mix of stances — not all should agree. Include at least one person on each side.
Respond with ONLY the JSON array, no other text.\
"""


async def generate_personas(
    topic: str,
    location: str,
    count: int = 5,
    config: LLMConfig | None = None,
) -> list[Persona]:
    """Generate diverse citizen-agent personas for a deliberation."""
    prompt = (
        f"Topic: {topic}\n"
        f"Location: {location}\n"
        f"Generate {count} diverse citizen personas for this civic deliberation."
    )

    response = await chat_completion(
        messages=[LLMMessage(role="user", content=prompt)],
        system=PERSONA_SYSTEM_PROMPT.format(count=count),
        config=config,
        temperature=0.9,
    )

    # Parse JSON response — handle markdown code fences
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json) and last line (```)
        text = "\n".join(lines[1:-1])

    raw_personas = json.loads(text)

    personas = []
    for raw in raw_personas:
        # Normalize stance value
        stance_str = raw["initial_stance"].lower().replace(" ", "_")
        personas.append(
            Persona(
                name=raw["name"],
                age=raw["age"],
                occupation=raw["occupation"],
                background=raw["background"],
                core_values=raw["core_values"],
                communication_style=raw["communication_style"],
                initial_stance=Stance(stance_str),
                location_context=raw.get("location_context", ""),
            )
        )

    return personas
