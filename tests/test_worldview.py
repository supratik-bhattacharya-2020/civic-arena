"""Tests for the worldview module."""

from __future__ import annotations

from civicarena.worldview import _build_search_queries
from civicarena.types import Persona, Stance


class TestBuildSearchQueries:
    def test_generates_multiple_queries(self, sample_persona):
        queries = _build_search_queries(sample_persona, "Ban plastic bags?", "London")
        assert len(queries) >= 2

    def test_includes_base_query(self, sample_persona):
        queries = _build_search_queries(sample_persona, "Ban plastic bags?", "London")
        assert "Ban plastic bags? London" in queries

    def test_includes_occupation(self, sample_persona):
        queries = _build_search_queries(sample_persona, "Ban plastic bags?", "London")
        occupation_queries = [q for q in queries if "Small business owner" in q]
        assert len(occupation_queries) >= 1

    def test_includes_values(self, sample_persona):
        queries = _build_search_queries(sample_persona, "Ban plastic bags?", "London")
        # Should include at least one query with a core value
        values_queries = [q for q in queries if any(v in q for v in sample_persona.core_values)]
        assert len(values_queries) >= 1
