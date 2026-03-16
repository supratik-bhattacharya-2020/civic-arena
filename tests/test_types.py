"""Tests for Pydantic types and data models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from civicarena.types import (
    DQIScore,
    DeliberationResult,
    LLMConfig,
    LLMMessage,
    Persona,
    RoundResult,
    SearchResult,
    Stance,
    Statement,
    Worldview,
)


class TestStance:
    def test_stance_values(self):
        assert Stance.STRONGLY_FOR.value == "strongly_for"
        assert Stance.AGAINST.value == "against"

    def test_stance_from_string(self):
        assert Stance("strongly_for") == Stance.STRONGLY_FOR
        assert Stance("neutral") == Stance.NEUTRAL


class TestPersona:
    def test_create_persona(self, sample_persona):
        assert sample_persona.name == "Alice Chen"
        assert sample_persona.age == 34
        assert sample_persona.initial_stance == Stance.AGAINST

    def test_persona_summary(self, sample_persona):
        assert sample_persona.summary == "Alice Chen, 34, Small business owner"

    def test_persona_validation(self):
        with pytest.raises(ValidationError):
            Persona(
                name="Test",
                age="not a number",  # type: ignore
                occupation="test",
                background="test",
                core_values=[],
                communication_style="test",
                initial_stance="invalid_stance",  # type: ignore
            )


class TestSearchResult:
    def test_create_search_result(self):
        result = SearchResult(
            title="Test",
            url="https://example.com",
            snippet="A test result",
        )
        assert result.title == "Test"
        assert result.url == "https://example.com"


class TestWorldview:
    def test_create_worldview(self, sample_worldview):
        assert sample_worldview.persona.name == "Alice Chen"
        assert len(sample_worldview.key_facts) == 2
        assert len(sample_worldview.sources) == 2


class TestStatement:
    def test_create_statement(self, sample_statement):
        assert sample_statement.persona_name == "Alice Chen"
        assert sample_statement.round_number == 1
        assert sample_statement.stance == Stance.AGAINST

    def test_statement_default_sources(self):
        stmt = Statement(
            persona_name="Test",
            round_number=1,
            round_name="Test",
            content="Hello",
            stance=Stance.NEUTRAL,
        )
        assert stmt.sources_cited == []


class TestDQIScore:
    def test_valid_score(self):
        score = DQIScore(
            justification_level=3,
            respect=2,
            constructive_politics=2,
            overall_quality=8,
            summary="Good deliberation",
        )
        assert score.justification_level == 3

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            DQIScore(
                justification_level=5,  # max is 3
                respect=2,
                constructive_politics=2,
                overall_quality=8,
                summary="test",
            )

    def test_overall_quality_bounds(self):
        with pytest.raises(ValidationError):
            DQIScore(
                justification_level=2,
                respect=2,
                constructive_politics=2,
                overall_quality=15,  # max is 10
                summary="test",
            )


class TestLLMConfig:
    def test_defaults(self):
        config = LLMConfig()
        assert config.base_url == "https://api.openai.com/v1"
        assert config.api_key == ""
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048


class TestDeliberationResult:
    def test_create_result(self, sample_persona, sample_worldview, sample_round_result):
        result = DeliberationResult(
            topic="Test topic",
            location="London",
            personas=[sample_persona],
            worldviews=[sample_worldview],
            rounds=[sample_round_result],
            final_votes={"Alice Chen": Stance.AGAINST},
        )
        assert result.topic == "Test topic"
        assert result.dqi_score is None
