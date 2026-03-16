"""OpenAI-compatible LLM client for CivicArena."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import AsyncIterator

import httpx
from dotenv import load_dotenv

from civicarena.types import LLMConfig, LLMMessage

# Load .env from project root (where pyproject.toml lives)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"
load_dotenv(_ENV_FILE)


def _ensure_api_key() -> str:
    """Return the API key from env, or prompt the user and save to .env."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key

    import sys
    if not sys.stdin.isatty():
        raise SystemExit(
            "Error: No API key found. Set OPENAI_API_KEY in your environment or .env file."
        )

    from rich.console import Console
    c = Console()
    c.print("\n[yellow]No API key found.[/yellow]")
    c.print("[dim]You need an OpenAI-compatible API key to run CivicArena.[/dim]")
    c.print("[dim]This will be saved to .env (git-ignored) so you only do this once.[/dim]\n")

    key = c.input("[bold]Enter your API key: [/bold]").strip()
    if not key:
        raise SystemExit("Error: No API key provided.")

    # Optionally ask for base URL and model
    base_url = c.input(
        "[bold]API base URL[/bold] [dim](press Enter for https://api.openai.com/v1):[/dim] "
    ).strip()
    model = c.input(
        "[bold]Model[/bold] [dim](press Enter for gpt-4o-mini):[/dim] "
    ).strip()

    # Write to .env
    lines = [f"OPENAI_API_KEY={key}\n"]
    if base_url:
        lines.append(f"OPENAI_BASE_URL={base_url}\n")
    if model:
        lines.append(f"CIVICARENA_MODEL={model}\n")

    _ENV_FILE.write_text("".join(lines))

    # Load into current process
    os.environ["OPENAI_API_KEY"] = key
    if base_url:
        os.environ["OPENAI_BASE_URL"] = base_url
    if model:
        os.environ["CIVICARENA_MODEL"] = model

    c.print(f"\n[green]Saved to {_ENV_FILE}[/green]\n")
    return key


def get_default_config() -> LLMConfig:
    """Build LLM config from environment variables with sensible defaults."""
    api_key = _ensure_api_key()
    return LLMConfig(
        base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        api_key=api_key,
        model=os.environ.get("CIVICARENA_MODEL", "gpt-4o-mini"),
        temperature=float(os.environ.get("CIVICARENA_TEMPERATURE", "0.7")),
        max_tokens=int(os.environ.get("CIVICARENA_MAX_TOKENS", "2048")),
    )


async def chat_completion(
    messages: list[LLMMessage],
    config: LLMConfig | None = None,
    system: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Send a chat completion request and return the full response text."""
    config = config or get_default_config()

    payload_messages = []
    if system:
        payload_messages.append({"role": "system", "content": system})
    payload_messages.extend({"role": m.role, "content": m.content} for m in messages)

    payload = {
        "model": config.model,
        "messages": payload_messages,
        "temperature": temperature if temperature is not None else config.temperature,
        "max_tokens": max_tokens or config.max_tokens,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{config.base_url}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def chat_completion_stream(
    messages: list[LLMMessage],
    config: LLMConfig | None = None,
    system: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> AsyncIterator[str]:
    """Send a streaming chat completion request and yield text chunks."""
    config = config or get_default_config()

    payload_messages = []
    if system:
        payload_messages.append({"role": "system", "content": system})
    payload_messages.extend({"role": m.role, "content": m.content} for m in messages)

    payload = {
        "model": config.model,
        "messages": payload_messages,
        "temperature": temperature if temperature is not None else config.temperature,
        "max_tokens": max_tokens or config.max_tokens,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            "POST",
            f"{config.base_url}/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                try:
                    data = json.loads(data_str)
                    delta = data["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
