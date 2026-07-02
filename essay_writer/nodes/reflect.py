"""Reflection node definition for essay critique generation."""
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..citations import validate_citations
from ..config import EssayWriterConfig
from ..state import AgentState

REFLECTION_PROMPT = (
    "You are a teacher grading an essay submission. "
    "Generate critique and recommendations for the user's submission. "
    "Provide detailed recommendations, including requests for length, depth, style, etc."
)


def make_reflection_node(model: Any, config: EssayWriterConfig | None = None):
    """Return a reflection node function bound to the provided model."""
    config = config or EssayWriterConfig()

    def reflection_node(state: AgentState) -> dict[str, str]:
        messages = [
            SystemMessage(content=f"{REFLECTION_PROMPT}\n\nTarget style: {config.style}"),
            HumanMessage(content=state["draft"]),
        ]
        response = model.invoke(messages)
        research_sources = list(state.get("research_sources") or [])
        validation = validate_citations(state.get("draft", ""), research_sources)
        return {"critique": response.content, "citation_validation": validation}

    return reflection_node
