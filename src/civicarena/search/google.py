"""Google Custom Search Engine provider — paid, for researchers."""

from __future__ import annotations

import os

import httpx

from civicarena.types import SearchResult


class GoogleCSEProvider:
    """Search provider using Google Custom Search Engine API."""

    def __init__(self, api_key: str | None = None, cx: str | None = None):
        self._api_key = api_key or os.environ.get("GOOGLE_CSE_API_KEY", "")
        self._cx = cx or os.environ.get("GOOGLE_CSE_CX", "")

    @property
    def name(self) -> str:
        return "Google CSE"

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Execute a Google CSE search."""
        if not self._api_key or not self._cx:
            return []

        params = {
            "key": self._api_key,
            "cx": self._cx,
            "q": query,
            "num": min(max_results, 10),
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://www.googleapis.com/customsearch/v1",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()
        except Exception:
            return []

        results = []
        for item in data.get("items", [])[:max_results]:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                )
            )
        return results
