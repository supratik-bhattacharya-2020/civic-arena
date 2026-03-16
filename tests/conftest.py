"""Shared test fixtures for CivicArena."""

from __future__ import annotations

import pytest

from civicarena.types import (
    DQIScore,
    LLMConfig,
    Persona,
    RoundResult,
    SearchResult,
    Stance,
    Statement,
    Worldview,
)


@pytest.fixture
def sample_persona() -> Persona:
    return Persona(
        name="Alice Chen",
        age=34,
        occupation="Small business owner",
        background="Runs a grocery store in East London for 8 years.",
        core_values=["economic sustainability", "community"],
        communication_style="pragmatic",
        initial_stance=Stance.AGAINST,
        location_context="Business in Hackney, concerned about packaging costs",
    )


@pytest.fixture
def sample_persona_2() -> Persona:
    return Persona(
        name="James Green",
        age=28,
        occupation="Environmental activist",
        background="Works for a marine conservation charity.",
        core_values=["environmental protection", "sustainability"],
        communication_style="passionate",
        initial_stance=Stance.STRONGLY_FOR,
        location_context="Campaigns across London boroughs",
    )


@pytest.fixture
def sample_search_results() -> list[SearchResult]:
    return [
        SearchResult(
            title="Plastic bag ban impact study",
            url="https://example.com/study",
            snippet="A 2024 study found that plastic bag bans reduce marine litter by 40%.",
        ),
        SearchResult(
            title="Small business costs of bag alternatives",
            url="https://example.com/costs",
            snippet="Paper and reusable bags cost 3-5x more than single-use plastic.",
        ),
    ]


@pytest.fixture
def sample_worldview(sample_persona, sample_search_results) -> Worldview:
    return Worldview(
        persona=sample_persona,
        key_facts=[
            "Plastic bag bans reduce marine litter by 40%",
            "Alternative bags cost 3-5x more",
        ],
        supporting_evidence=["Small businesses face higher packaging costs"],
        concerns=["Customer pushback on bringing own bags", "Cost increases"],
        sources=sample_search_results,
        stance_reasoning="As a grocery store owner, the transition costs are significant.",
    )


@pytest.fixture
def sample_statement(sample_persona) -> Statement:
    return Statement(
        persona_name=sample_persona.name,
        round_number=1,
        round_name="Opening Statements",
        content="I understand the environmental concerns, but as a small business owner...",
        stance=Stance.AGAINST,
    )


@pytest.fixture
def sample_round_result(sample_statement) -> RoundResult:
    return RoundResult(
        round_number=1,
        round_name="Opening Statements",
        statements=[sample_statement],
    )


@pytest.fixture
def llm_config() -> LLMConfig:
    return LLMConfig(
        base_url="http://test:4141/v1",
        api_key="test-key",
        model="test-model",
    )
