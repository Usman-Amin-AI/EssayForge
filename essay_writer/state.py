"""Shared state schema for the essay writer graph."""
from __future__ import annotations
from typing import List, TypedDict

from pydantic import BaseModel, Field


class AgentState(TypedDict, total=False):
    """Typed dictionary for the essay writer state machine."""

    task: str
    plan: str
    draft: str
    critique: str
    content: List[str]
    research_sources: List[dict]
    draft_with_citations: str
    bibliography: str
    citation_validation: str
    revision_number: int
    max_revisions: int
    config: dict


class AgentStateModel(BaseModel):
    """Pydantic model for the essay writer state."""

    task: str
    plan: str = ""
    draft: str = ""
    critique: str = ""
    content: List[str] = Field(default_factory=list)
    research_sources: List[dict] = Field(default_factory=list)
    draft_with_citations: str = ""
    bibliography: str = ""
    citation_validation: str = ""
    revision_number: int = 1
    max_revisions: int = 2
    config: dict = Field(default_factory=dict)
