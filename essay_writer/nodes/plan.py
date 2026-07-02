"""Essay planner node definitions."""
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from ..config import EssayWriterConfig
from ..state import AgentState

PLAN_PROMPT = (
    "You are an expert writer tasked with writing a high level outline of an essay. "
    "Write such an outline for the user provided topic. Give an outline of the essay along with any relevant notes "
    "or instructions for the sections."
)


def make_plan_node(model: Any, config: EssayWriterConfig | None = None):
    """Return a planner node function bound to the provided model."""
    config = config or EssayWriterConfig()

    def plan_node(state: AgentState) -> dict[str, str]:
        prompt = (
            f"{PLAN_PROMPT}\n\nTarget word count: {config.target_word_count}\n"
            f"Style: {config.style}"
        )
        messages = [SystemMessage(content=prompt), HumanMessage(content=state["task"])]
        response = model.invoke(messages)
        return {"plan": response.content}

    return plan_node
