"""SearXNG search provider — self-hosted, privacy-focused."""

from __future__ import annotations

import os

import httpx

from civicarena.types import SearchResult


class SearXNGProvider:
    """Search provider using a SearXNG instance."""

    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or os.environ.get("SEARXNG_URL", "http://localhost:8080")

    @property
    def name(self) -> str:
        return "SearXNG"

    async def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Execute a SearXNG search."""
        params = {
            "q": query,
            "format": "json",
            "categories": "general",
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self._base_url}/search", params=params)
                response.raise_for_status()
                data = response.json()
        except Exception:
            return []

        results = []
        for r in data.get("results", [])[:max_results]:
            results.append(
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                )
            )
        return results
