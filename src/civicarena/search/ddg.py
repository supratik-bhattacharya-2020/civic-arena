"""DuckDuckGo search provider — free, zero config."""

from __future__ import annotations

import asyncio
from functools import partial

from ddgs import DDGS

from civicarena.types import SearchResult


class DuckDuckGoProvider:
    """Search provider using DuckDuckGo (free, no API key required)."""

    @property
    def name(self) -> str:
        return "DuckDuckGo"

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Execute a DuckDuckGo search asynchronously."""
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, partial(self._search_sync, query, max_results))
        return results

    def _search_sync(self, query: str, max_results: int) -> list[SearchResult]:
        """Synchronous search implementation."""
        try:
            raw_results = DDGS().text(query, max_results=max_results, backend="duckduckgo")
        except Exception:
            return []

        return [
            SearchResult(
                title=r.get("title", ""),
                url=r.get("href", r.get("link", "")),
                snippet=r.get("body", r.get("snippet", "")),
            )
            for r in raw_results
            if r.get("href") or r.get("link")
        ]
