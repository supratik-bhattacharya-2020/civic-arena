"""Shared Pydantic models for CivicArena."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Stance(str, Enum):
    STRONGLY_FOR = "strongly_for"
    FOR = "for"
    NEUTRAL = "neutral"
    AGAINST = "against"
    STRONGLY_AGAINST = "strongly_against"


class Persona(BaseModel):
    """A citizen-agent persona participating in deliberation."""

    name: str
    age: int
    occupation: str
    background: str
    core_values: list[str]
    communication_style: str
    initial_stance: Stance
    location_context: str = ""

    @property
    def summary(self) -> str:
        return f"{self.name}, {self.age}, {self.occupation}"


class SearchResult(BaseModel):
    """A single web search result."""

    title: str
    url: str
    snippet: str


class Worldview(BaseModel):
    """An agent's researched perspective on the topic."""

    persona: Persona
    key_facts: list[str]
    supporting_evidence: list[str]
    concerns: list[str]
    sources: list[SearchResult]
    stance_reasoning: str


class Statement(BaseModel):
    """A single statement made by an agent during deliberation."""

    persona_name: str
    round_number: int
    round_name: str
    content: str
    sources_cited: list[str] = Field(default_factory=list)
    stance: Stance


class RoundResult(BaseModel):
    """Result of a single deliberation round."""

    round_number: int
    round_name: str
    statements: list[Statement]


class DQIScore(BaseModel):
    """Discourse Quality Index scores for a deliberation."""

    justification_level: int = Field(ge=0, le=3, description="0=none, 1=inferior, 2=qualified, 3=sophisticated")
    respect: int = Field(ge=0, le=2, description="0=disrespectful, 1=neutral, 2=respectful")
    constructive_politics: int = Field(ge=0, le=2, description="0=none, 1=vague, 2=concrete proposals")
    overall_quality: int = Field(ge=0, le=10)
    summary: str
    highlights: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)


class DeliberationResult(BaseModel):
    """Complete result of a deliberation session."""

    topic: str
    location: str
    personas: list[Persona]
    worldviews: list[Worldview]
    rounds: list[RoundResult]
    final_votes: dict[str, Stance]
    dqi_score: Optional[DQIScore] = None


class LLMMessage(BaseModel):
    """A message in the LLM conversation."""

    role: str
    content: str


class LLMConfig(BaseModel):
    """Configuration for the LLM client."""

    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 2048
