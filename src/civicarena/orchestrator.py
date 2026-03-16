"""Orchestrator — manages agent turns and full deliberation flow."""

from __future__ import annotations

from typing import AsyncIterator, Protocol

from rich.console import Console

from civicarena.judge import judge_deliberation
from civicarena.personas import generate_personas
from civicarena.protocol import ROUNDS, generate_statement, generate_statement_stream
from civicarena.search.base import SearchProvider
from civicarena.search.ddg import DuckDuckGoProvider
from civicarena.types import (
    DeliberationResult,
    LLMConfig,
    Persona,
    RoundResult,
    Stance,
    Statement,
    Worldview,
)
from civicarena.worldview import build_worldview


class DeliberationCallback(Protocol):
    """Callback protocol for deliberation events."""

    async def on_personas_generated(self, personas: list[Persona]) -> None: ...
    async def on_worldview_built(self, worldview: Worldview) -> None: ...
    async def on_round_start(self, round_number: int, round_name: str) -> None: ...
    async def on_statement_start(self, persona_name: str) -> None: ...
    async def on_statement_chunk(self, chunk: str) -> None: ...
    async def on_statement_end(self, statement: Statement) -> None: ...
    async def on_round_end(self, round_result: RoundResult) -> None: ...


class NoopCallback:
    """Default callback that does nothing."""

    async def on_personas_generated(self, personas: list[Persona]) -> None:
        pass

    async def on_worldview_built(self, worldview: Worldview) -> None:
        pass

    async def on_round_start(self, round_number: int, round_name: str) -> None:
        pass

    async def on_statement_start(self, persona_name: str) -> None:
        pass

    async def on_statement_chunk(self, chunk: str) -> None:
        pass

    async def on_statement_end(self, statement: Statement) -> None:
        pass

    async def on_round_end(self, round_result: RoundResult) -> None:
        pass


async def run_deliberation(
    topic: str,
    location: str,
    persona_count: int = 5,
    search_provider: SearchProvider | None = None,
    config: LLMConfig | None = None,
    callback: DeliberationCallback | None = None,
    stream: bool = True,
    verbose: bool = False,
) -> DeliberationResult:
    """Run a complete deliberation session."""
    cb = callback or NoopCallback()
    search = search_provider or DuckDuckGoProvider()

    # Phase 1: Generate personas
    personas = await generate_personas(topic, location, count=persona_count, config=config)
    await cb.on_personas_generated(personas)

    # Phase 2: Build worldviews
    worldviews: list[Worldview] = []
    for persona in personas:
        worldview = await build_worldview(persona, topic, location, search, config=config)
        worldviews.append(worldview)
        await cb.on_worldview_built(worldview)

    # Phase 3: Run deliberation rounds
    all_statements: list[Statement] = []
    rounds: list[RoundResult] = []

    for round_def in ROUNDS:
        await cb.on_round_start(round_def.number, round_def.name)

        round_statements: list[Statement] = []
        for worldview in worldviews:
            await cb.on_statement_start(worldview.persona.name)

            if stream:
                # Stream the statement and collect the full text
                chunks: list[str] = []
                async for chunk in generate_statement_stream(
                    worldview=worldview,
                    topic=topic,
                    location=location,
                    round_def=round_def,
                    prior_statements=all_statements,
                    config=config,
                    verbose=verbose,
                ):
                    chunks.append(chunk)
                    await cb.on_statement_chunk(chunk)

                full_text = "".join(chunks)
                # Determine stance
                stance = worldview.persona.initial_stance
                if round_def.number == 4:
                    from civicarena.protocol import _extract_final_stance
                    stance = _extract_final_stance(full_text, worldview.persona.initial_stance)

                statement = Statement(
                    persona_name=worldview.persona.name,
                    round_number=round_def.number,
                    round_name=round_def.name,
                    content=full_text.strip(),
                    stance=stance,
                )
            else:
                statement = await generate_statement(
                    worldview=worldview,
                    topic=topic,
                    location=location,
                    round_def=round_def,
                    prior_statements=all_statements,
                    config=config,
                    verbose=verbose,
                )

            round_statements.append(statement)
            all_statements.append(statement)
            await cb.on_statement_end(statement)

        round_result = RoundResult(
            round_number=round_def.number,
            round_name=round_def.name,
            statements=round_statements,
        )
        rounds.append(round_result)
        await cb.on_round_end(round_result)

    # Phase 4: Extract final votes
    final_votes: dict[str, Stance] = {}
    if rounds:
        for stmt in rounds[-1].statements:
            final_votes[stmt.persona_name] = stmt.stance

    # Phase 5: Judge the deliberation
    dqi_score = await judge_deliberation(topic, location, rounds, config=config)

    return DeliberationResult(
        topic=topic,
        location=location,
        personas=personas,
        worldviews=worldviews,
        rounds=rounds,
        final_votes=final_votes,
        dqi_score=dqi_score,
    )
