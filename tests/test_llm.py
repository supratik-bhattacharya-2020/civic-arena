"""Tests for the LLM client configuration."""

from __future__ import annotations

import os

from civicarena.llm import get_default_config
from civicarena.types import LLMConfig


class TestGetDefaultConfig:
    def test_default_values(self, monkeypatch):
        # Clear relevant env vars
        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("CIVICARENA_MODEL", raising=False)
        monkeypatch.delenv("CIVICARENA_TEMPERATURE", raising=False)
        monkeypatch.delenv("CIVICARENA_MAX_TOKENS", raising=False)

        config = get_default_config()
        assert config.base_url == "https://api.openai.com/v1"
        assert config.api_key == "test-key"
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.7
        assert config.max_tokens == 2048

    def test_custom_env_values(self, monkeypatch):
        monkeypatch.setenv("OPENAI_BASE_URL", "http://custom:8080/v1")
        monkeypatch.setenv("OPENAI_API_KEY", "my-key")
        monkeypatch.setenv("CIVICARENA_MODEL", "gpt-4o")
        monkeypatch.setenv("CIVICARENA_TEMPERATURE", "0.5")
        monkeypatch.setenv("CIVICARENA_MAX_TOKENS", "4096")

        config = get_default_config()
        assert config.base_url == "http://custom:8080/v1"
        assert config.api_key == "my-key"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.5
        assert config.max_tokens == 4096
