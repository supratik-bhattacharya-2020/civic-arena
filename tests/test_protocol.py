"""Tests for the protocol module."""

from __future__ import annotations

import pytest

from civicarena.protocol import (
    ROUNDS,
    _build_agent_system_prompt,
    _build_conversation_context,
    _extract_final_stance,
)
from civicarena.types import Stance, Statement


class TestRounds:
    def test_four_rounds_defined(self):
        assert len(ROUNDS) == 4

    def test_round_numbers_sequential(self):
        for i, r in enumerate(ROUNDS, 1):
            assert r.number == i

    def test_round_names(self):
        names = [r.name for r in ROUNDS]
        assert names == [
            "Opening Statements",
            "Cross-Examination",
            "Common Ground",
            "Final Positions",
        ]


class TestExtractFinalStance:
    def test_extracts_strongly_for(self):
        text = "My final vote is strongly_for this policy."
        assert _extract_final_stance(text, Stance.NEUTRAL) == Stance.STRONGLY_FOR

    def test_extracts_with_spaces(self):
        text = "I vote strongly against this measure."
        assert _extract_final_stance(text, Stance.NEUTRAL) == Stance.STRONGLY_AGAINST

    def test_returns_default_when_no_match(self):
        text = "I have complex feelings about this."
        assert _extract_final_stance(text, Stance.NEUTRAL) == Stance.NEUTRAL

    def test_case_insensitive(self):
        text = "My vote: STRONGLY_FOR"
        assert _extract_final_stance(text, Stance.NEUTRAL) == Stance.STRONGLY_FOR


class TestBuildConversationContext:
    def test_first_round_no_prior(self):
        context = _build_conversation_context([], ROUNDS[0])
        assert "Present your initial position" in context

    def test_includes_prior_statements(self):
        prior = [
            Statement(
                persona_name="Alice",
                round_number=1,
                round_name="Opening Statements",
                content="I support this policy.",
                stance=Stance.FOR,
            )
        ]
        context = _build_conversation_context(prior, ROUNDS[1])
        assert "Alice" in context
        assert "I support this policy." in context
        assert "Round 2" in context


class TestBuildAgentSystemPrompt:
    def test_includes_persona_details(self, sample_worldview):
        prompt = _build_agent_system_prompt(
            sample_worldview, "Ban plastic bags?", "London", ROUNDS[0]
        )
        assert "Alice Chen" in prompt
        assert "34" in prompt
        assert "Small business owner" in prompt
        assert "London" in prompt

    def test_includes_civility_rules(self, sample_worldview):
        prompt = _build_agent_system_prompt(
            sample_worldview, "Ban plastic bags?", "London", ROUNDS[0]
        )
        assert "CIVILITY RULES" in prompt
        assert "Cite sources" in prompt

    def test_includes_worldview(self, sample_worldview):
        prompt = _build_agent_system_prompt(
            sample_worldview, "Ban plastic bags?", "London", ROUNDS[0]
        )
        assert "grocery store owner" in prompt
