"""Critique research node definition for essay revision."""
from typing import Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from ..research_tools import ResearchPipeline
from ..state import AgentState

RESEARCH_CRITIQUE_PROMPT = (
    "You are a researcher charged with providing information that can "
    "be used when making any requested revisions (as outlined below). "
    "Generate a list of search queries that will gather any relevant information. Only generate 3 queries max."
)


class Queries(BaseModel):
    """Structured output model for generated research queries."""

    queries: List[str]


def make_research_critique_node(model: Any, research_pipeline: ResearchPipeline):
    """Return a research node that gathers content based on essay critique feedback."""

    def research_critique_node(state: AgentState) -> dict[str, List[str]]:
        queries = model.with_structured_output(Queries).invoke(
            [SystemMessage(content=RESEARCH_CRITIQUE_PROMPT), HumanMessage(content=state["critique"])]
        )
        content = list(state.get("content") or [])
        gathered = research_pipeline.gather_texts(
            task=state.get("task", ""),
            queries=queries.queries,
            existing_content=content,
            max_results=2,
        )
        return {
            "content": gathered["content"],
            "research_sources": [
                *list(state.get("research_sources") or []),
                *gathered.get("research_sources", []),
            ],
        }

    return research_critique_node
