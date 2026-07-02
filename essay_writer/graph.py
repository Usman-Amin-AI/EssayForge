"""Graph builder for the essay writer workflow."""
from __future__ import annotations
from typing import Any

from langgraph.graph import END, StateGraph

from .config import EssayWriterConfig
from .nodes.bibliography import make_bibliography_node
from .nodes.critique import make_research_critique_node
from .nodes.generate import make_generation_node
from .nodes.pause import make_human_pause_node
from .nodes.plan import make_plan_node
from .nodes.reflect import make_reflection_node
from .nodes.research import make_research_plan_node
from .persistence import make_persisting_node
from .research_tools import ResearchPipeline
from .state import AgentState
from .store import EssayRunStore


class AgentGraphBuilder(StateGraph[AgentState]):
    """Typed StateGraph builder for the essay writer."""


def make_should_continue(config: EssayWriterConfig):
    """Return an edge function that stops after the configured revision budget."""

    def should_continue(state: AgentState) -> Any:
        if state.get("revision_number", 1) > config.max_reflect_cycles:
            return END
        return "reflect"

    return should_continue


def create_essay_writer_graph(
    model: Any,
    research_pipeline: ResearchPipeline,
    config: EssayWriterConfig | None = None,
    store: EssayRunStore | None = None,
) -> AgentGraphBuilder:
    """Create a configured essay writer StateGraph builder.

    Args:
        model: A chat model instance with invoke() and with_structured_output().
        research_pipeline: A pipeline that selects providers and gathers deduplicated research content.

    Returns:
        AgentGraphBuilder: A graph builder configured with planner, research,
        generation, reflection, and critique nodes.
    """
    config = config or EssayWriterConfig()
    store = store or EssayRunStore()
    graph_builder = AgentGraphBuilder(AgentState)

    graph_builder.add_node("planner", make_plan_node(model, config=config))
    graph_builder.add_node("persist_plan", make_persisting_node("plan", store))
    graph_builder.add_node(
        "pause_plan",
        make_human_pause_node("plan", "plan", config=config),
    )
    graph_builder.add_node("research_plan", make_research_plan_node(model, research_pipeline))
    graph_builder.add_node("generate", make_generation_node(model, config=config))
    graph_builder.add_node("reflect", make_reflection_node(model, config=config))
    graph_builder.add_node("persist_reflect", make_persisting_node("reflect", store))
    graph_builder.add_node(
        "pause_reflect",
        make_human_pause_node("reflect", "critique", config=config),
    )
    graph_builder.add_node(
        "research_critique", make_research_critique_node(model, research_pipeline)
    )
    graph_builder.add_node("bibliography", make_bibliography_node(style="APA"))

    graph_builder.set_entry_point("planner")
    graph_builder.add_conditional_edges(
        "generate",
        make_should_continue(config),
        {END: END, "reflect": "reflect"},
    )
    graph_builder.add_edge("planner", "pause_plan")
    graph_builder.add_edge("pause_plan", "persist_plan")
    graph_builder.add_edge("persist_plan", "research_plan")
    graph_builder.add_edge("research_plan", "generate")
    graph_builder.add_edge("reflect", "pause_reflect")
    graph_builder.add_edge("pause_reflect", "persist_reflect")
    graph_builder.add_edge("persist_reflect", "research_critique")
    graph_builder.add_edge("research_critique", "generate")
    graph_builder.add_edge("generate", "bibliography")
    graph_builder.add_edge("bibliography", END)

    return graph_builder
