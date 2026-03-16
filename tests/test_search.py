"""Tests for the search providers."""

from __future__ import annotations

import pytest

from civicarena.search.base import SearchProvider
from civicarena.search.ddg import DuckDuckGoProvider
from civicarena.search.google import GoogleCSEProvider
from civicarena.search.searxng import SearXNGProvider
from civicarena.types import SearchResult


class TestSearchProviderProtocol:
    def test_ddg_implements_protocol(self):
        provider = DuckDuckGoProvider()
        assert isinstance(provider, SearchProvider)

    def test_searxng_implements_protocol(self):
        provider = SearXNGProvider()
        assert isinstance(provider, SearchProvider)

    def test_google_implements_protocol(self):
        provider = GoogleCSEProvider()
        assert isinstance(provider, SearchProvider)


class TestDuckDuckGoProvider:
    def test_name(self):
        provider = DuckDuckGoProvider()
        assert provider.name == "DuckDuckGo"


class TestSearXNGProvider:
    def test_name(self):
        provider = SearXNGProvider()
        assert provider.name == "SearXNG"

    def test_custom_url(self):
        provider = SearXNGProvider(base_url="http://custom:9090")
        assert provider._base_url == "http://custom:9090"


class TestGoogleCSEProvider:
    def test_name(self):
        provider = GoogleCSEProvider()
        assert provider.name == "Google CSE"

    @pytest.mark.asyncio
    async def test_returns_empty_without_credentials(self):
        provider = GoogleCSEProvider(api_key="", cx="")
        results = await provider.search("test query")
        assert results == []
