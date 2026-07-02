"""Utility for validating that research-derived claims are cited."""
from typing import Sequence

from .citations import build_bibliography, validate_citations


def validate_draft_with_sources(draft: str, research_sources: Sequence[dict], style: str = "APA") -> dict:
    """Return a validation report for a draft and its cited sources."""
    return {
        "validation": validate_citations(draft, research_sources),
        "bibliography": build_bibliography(draft, research_sources, style=style),
    }
