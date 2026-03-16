"""DQI-based judge — scores deliberation quality."""

from __future__ import annotations

import json

from civicarena.llm import chat_completion
from civicarena.types import DQIScore, LLMConfig, LLMMessage, RoundResult

JUDGE_SYSTEM_PROMPT = """\
You are an impartial deliberation quality judge using a subset of the Discourse Quality Index (DQI).

Score the deliberation on these dimensions:

1. **Justification Level** (0-3):
   0 = No justification — bare assertions with no reasoning
   1 = Inferior justification — reasons given but incomplete or illogical
   2 = Qualified justification — reasons with some supporting evidence
   3 = Sophisticated justification — well-reasoned with strong evidence and source citations

2. **Respect** (0-2):
   0 = Disrespectful — personal attacks, dismissive language
   1 = Neutral — no disrespect but no explicit respect either
   2 = Respectful — actively acknowledges others' perspectives, uses courteous language

3. **Constructive Politics** (0-2):
   0 = No proposals — only criticism, no alternatives
   1 = Vague proposals — general ideas without specifics
   2 = Concrete proposals — specific, actionable suggestions

4. **Overall Quality** (0-10):
   Holistic assessment of the entire deliberation.

Also provide:
- "summary": 2-3 sentence summary of the deliberation quality
- "highlights": array of 2-3 strings noting what went well
- "concerns": array of 1-2 strings noting areas for improvement

Respond with ONLY a JSON object with these fields:
"justification_level", "respect", "constructive_politics", "overall_quality", "summary", "highlights", "concerns"
No other text.\
"""


def _format_transcript(rounds: list[RoundResult]) -> str:
    """Format the full deliberation transcript for judging."""
    parts = []
    for rnd in rounds:
        parts.append(f"=== Round {rnd.round_number}: {rnd.round_name} ===\n")
        for stmt in rnd.statements:
            parts.append(f"[{stmt.persona_name}]:\n{stmt.content}\n")
        parts.append("")
    return "\n".join(parts)


async def judge_deliberation(
    topic: str,
    location: str,
    rounds: list[RoundResult],
    config: LLMConfig | None = None,
) -> DQIScore:
    """Score a completed deliberation using DQI criteria."""
    transcript = _format_transcript(rounds)

    prompt = (
        f"Topic: {topic}\n"
        f"Location: {location}\n\n"
        f"Full deliberation transcript:\n\n{transcript}\n\n"
        f"Please score this deliberation."
    )

    response = await chat_completion(
        messages=[LLMMessage(role="user", content=prompt)],
        system=JUDGE_SYSTEM_PROMPT,
        config=config,
        temperature=0.3,
    )

    # Parse JSON response
    text = response.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    raw = json.loads(text)

    return DQIScore(
        justification_level=raw["justification_level"],
        respect=raw["respect"],
        constructive_politics=raw["constructive_politics"],
        overall_quality=raw["overall_quality"],
        summary=raw["summary"],
        highlights=raw.get("highlights", []),
        concerns=raw.get("concerns", []),
    )
