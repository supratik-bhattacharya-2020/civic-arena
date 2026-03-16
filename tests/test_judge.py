"""Tests for the judge module."""

from __future__ import annotations

from civicarena.judge import _format_transcript
from civicarena.types import RoundResult, Stance, Statement


class TestFormatTranscript:
    def test_formats_single_round(self, sample_round_result):
        transcript = _format_transcript([sample_round_result])
        assert "Round 1" in transcript
        assert "Opening Statements" in transcript
        assert "Alice Chen" in transcript

    def test_formats_multiple_rounds(self):
        rounds = [
            RoundResult(
                round_number=1,
                round_name="Opening Statements",
                statements=[
                    Statement(
                        persona_name="Alice",
                        round_number=1,
                        round_name="Opening Statements",
                        content="I support this.",
                        stance=Stance.FOR,
                    ),
                ],
            ),
            RoundResult(
                round_number=2,
                round_name="Cross-Examination",
                statements=[
                    Statement(
                        persona_name="Bob",
                        round_number=2,
                        round_name="Cross-Examination",
                        content="But consider this.",
                        stance=Stance.AGAINST,
                    ),
                ],
            ),
        ]
        transcript = _format_transcript(rounds)
        assert "Round 1" in transcript
        assert "Round 2" in transcript
        assert "Alice" in transcript
        assert "Bob" in transcript

    def test_empty_rounds(self):
        transcript = _format_transcript([])
        assert transcript.strip() == ""
