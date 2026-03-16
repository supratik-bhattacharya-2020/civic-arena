"""Deliberation protocol — 4-round structured debate with civility rules."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import AsyncIterator

from civicarena.llm import chat_completion, chat_completion_stream
from civicarena.types import LLMConfig, LLMMessage, Stance, Statement, Worldview


@dataclass
class Round:
    """Definition of a deliberation round."""

    number: int
    name: str
    instruction: str
    system_context: str


ROUNDS = [
    Round(
        number=1,
        name="Opening Statements",
        instruction="Present your initial position on the topic with supporting evidence. Cite specific sources.",
        system_context="This is Round 1: Opening Statements. Each participant presents their position clearly.",
    ),
    Round(
        number=2,
        name="Cross-Examination",
        instruction=(
            "Respond to the other participants' statements. Challenge claims you disagree with "
            "using evidence. Ask probing questions. You must reference at least one other participant by name."
        ),
        system_context="This is Round 2: Cross-Examination. Participants engage with each other's arguments.",
    ),
    Round(
        number=3,
        name="Common Ground",
        instruction=(
            "Identify areas where you agree with other participants. Propose a compromise or "
            "middle-ground solution. Acknowledge at least one valid point from someone you disagree with."
        ),
        system_context="This is Round 3: Common Ground. Participants seek areas of agreement.",
    ),
    Round(
        number=4,
        name="Final Positions",
        instruction=(
            "Present your final position. Has your view changed at all? Summarize your key argument "
            "in 2-3 sentences. State your final vote: strongly_for, for, neutral, against, or strongly_against."
        ),
        system_context="This is Round 4: Final Positions. Participants give closing statements and vote.",
    ),
]

CIVILITY_RULES_SHORT = """\
CIVILITY RULES (you MUST follow these):
1. Cite sources for factual claims
2. Acknowledge valid points from opponents
3. No personal attacks — critique arguments, not people
4. Be concise — keep responses under 75 words. Make every sentence count.\
"""

CIVILITY_RULES_LONG = """\
CIVILITY RULES (you MUST follow these):
1. Cite sources for factual claims — reference specific data, studies, or articles
2. Acknowledge valid points from those you disagree with
3. No personal attacks — critique arguments, not people
4. Use respectful language — no insults, sarcasm, or condescension
5. Show willingness to update your views when presented with compelling evidence
6. Keep responses focused and under 200 words\
"""

AGENT_SYSTEM_PROMPT = """\
You are {name}, a {age}-year-old {occupation} from {location}.
Background: {background}
Core values: {values}
Communication style: {communication_style}

Your researched position on "{topic}":
{stance_reasoning}

Key facts you know:
{key_facts}

Your concerns:
{concerns}

{civility_rules}

{round_context}

Stay in character. Speak as {name} would — use your communication style consistently.
Do not break character or refer to yourself as an AI.\
"""


def _build_agent_system_prompt(
    worldview: Worldview,
    topic: str,
    location: str,
    round_def: Round,
    verbose: bool = False,
) -> str:
    """Build the system prompt for an agent in a specific round."""
    civility_rules = CIVILITY_RULES_LONG if verbose else CIVILITY_RULES_SHORT
    return AGENT_SYSTEM_PROMPT.format(
        name=worldview.persona.name,
        age=worldview.persona.age,
        occupation=worldview.persona.occupation,
        location=location,
        background=worldview.persona.background,
        values=", ".join(worldview.persona.core_values),
        communication_style=worldview.persona.communication_style,
        topic=topic,
        stance_reasoning=worldview.stance_reasoning,
        key_facts="\n".join(f"- {f}" for f in worldview.key_facts),
        concerns="\n".join(f"- {c}" for c in worldview.concerns),
        civility_rules=civility_rules,
        round_context=round_def.system_context,
    )


def _build_conversation_context(
    prior_statements: list[Statement],
    current_round: Round,
) -> str:
    """Build the conversation history for an agent."""
    if not prior_statements:
        return current_round.instruction

    context_parts = []
    # Group prior statements by round
    rounds_seen: dict[int, list[Statement]] = {}
    for stmt in prior_statements:
        rounds_seen.setdefault(stmt.round_number, []).append(stmt)

    for round_num in sorted(rounds_seen):
        stmts = rounds_seen[round_num]
        context_parts.append(f"--- Round {round_num}: {stmts[0].round_name} ---")
        for stmt in stmts:
            context_parts.append(f"\n{stmt.persona_name}:\n{stmt.content}")

    context_parts.append(f"\n--- Now it's your turn in Round {current_round.number}: {current_round.name} ---")
    context_parts.append(current_round.instruction)

    return "\n".join(context_parts)


async def generate_statement(
    worldview: Worldview,
    topic: str,
    location: str,
    round_def: Round,
    prior_statements: list[Statement],
    config: LLMConfig | None = None,
    verbose: bool = False,
) -> Statement:
    """Generate a single agent's statement for a round (non-streaming)."""
    system = _build_agent_system_prompt(worldview, topic, location, round_def, verbose=verbose)
    conversation = _build_conversation_context(prior_statements, round_def)

    content = await chat_completion(
        messages=[LLMMessage(role="user", content=conversation)],
        system=system,
        config=config,
        temperature=0.8,
    )

    # For final round, try to extract stance from the response
    stance = worldview.persona.initial_stance
    if round_def.number == 4:
        stance = _extract_final_stance(content, worldview.persona.initial_stance)

    return Statement(
        persona_name=worldview.persona.name,
        round_number=round_def.number,
        round_name=round_def.name,
        content=content.strip(),
        stance=stance,
    )


async def generate_statement_stream(
    worldview: Worldview,
    topic: str,
    location: str,
    round_def: Round,
    prior_statements: list[Statement],
    config: LLMConfig | None = None,
    verbose: bool = False,
) -> AsyncIterator[str]:
    """Generate a single agent's statement with streaming output."""
    system = _build_agent_system_prompt(worldview, topic, location, round_def, verbose=verbose)
    conversation = _build_conversation_context(prior_statements, round_def)

    async for chunk in chat_completion_stream(
        messages=[LLMMessage(role="user", content=conversation)],
        system=system,
        config=config,
        temperature=0.8,
    ):
        yield chunk


def _extract_final_stance(content: str, default: Stance) -> Stance:
    """Try to extract the final stance/vote from a response."""
    content_lower = content.lower()
    # Check longer patterns first to avoid partial matches (e.g., "strongly against" before "against")
    ordered_stances = sorted(Stance, key=lambda s: len(s.value), reverse=True)
    for stance in ordered_stances:
        if stance.value in content_lower or stance.value.replace("_", " ") in content_lower:
            return stance
    return default
