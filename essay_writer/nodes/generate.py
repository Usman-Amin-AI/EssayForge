"""Essay generation node definition."""
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..citations import attach_source_markers, validate_citations
from ..config import EssayWriterConfig
from ..state import AgentState

WRITER_PROMPT = (
    "You are an essay assistant tasked with writing excellent essays. "
    "Generate the best essay possible for the user's request and the initial outline. "
    "If the user provides critique, respond with a revised version of your previous attempts. "
    "Write in a {style} tone, aiming for approximately {target_word_count} words. "
    "Utilize all the information below as needed:\n\n------\n\n{content}"
)


def make_generation_node(model: Any, config: EssayWriterConfig | None = None):
    """Return a generation node function bound to the provided model."""
    config = config or EssayWriterConfig()

    def generation_node(state: AgentState) -> dict[str, Any]:
        content = "\n\n".join(state.get("content") or [])
        user_message = HumanMessage(
            content=f"{state['task']}\n\nHere is my plan:\n\n{state['plan']}"
        )
        messages = [
            SystemMessage(
                content=WRITER_PROMPT.format(
                    content=content,
                    style=config.style,
                    target_word_count=config.target_word_count,
                )
            ),
            user_message,
        ]
        response = model.invoke(messages)
        draft = response.content
        research_sources = list(state.get("research_sources") or [])
        tagged_draft = attach_source_markers(draft, research_sources)
        validation = validate_citations(tagged_draft, research_sources)
        return {
            "draft": tagged_draft,
            "draft_with_citations": tagged_draft,
            "citation_validation": validation,
            "revision_number": state.get("revision_number", 1) + 1,
        }

    return generation_node
