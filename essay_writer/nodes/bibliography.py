"""Final bibliography node for the essay writer graph."""
from typing import Any

from ..citations import build_bibliography
from ..state import AgentState


def make_bibliography_node(style: str = "APA"):
    """Return a bibliography node that appends formatted references to the final draft."""

    def bibliography_node(state: AgentState) -> dict[str, str]:
        final_draft = state.get("draft", "")
        research_sources = list(state.get("research_sources") or [])
        bibliography = build_bibliography(final_draft, research_sources, style=style)
        return {
            "bibliography": bibliography,
            "draft": f"{final_draft}\n\n{bibliography}",
        }

    return bibliography_node
