"""Human-in-the-loop pause nodes for the essay writer graph."""
from __future__ import annotations

from typing import Any, Callable

from langgraph.types import interrupt

from ..config import EssayWriterConfig
from ..state import AgentState


def make_human_pause_node(
    stage_name: str,
    state_key: str,
    interrupt_fn: Callable[[dict], Any] | None = None,
    config: EssayWriterConfig | None = None,
):
    """Return a pause node that interrupts the graph for human review."""

    config = config or EssayWriterConfig()

    def pause_node(state: AgentState) -> dict[str, Any]:
        if not config.pause_for_human_approval:
            return {state_key: state.get(state_key, "")}

        payload = {
            "stage": stage_name,
            "state_key": state_key,
            "current_value": state.get(state_key, ""),
        }
        if interrupt_fn is not None:
            resumed_value = interrupt_fn(payload)
        else:
            resumed_value = interrupt(payload)

        if isinstance(resumed_value, dict):
            if state_key in resumed_value:
                return {state_key: resumed_value[state_key]}
            if "content" in resumed_value:
                return {state_key: resumed_value["content"]}
        if resumed_value is not None and resumed_value is not payload:
            return {state_key: resumed_value}
        return {state_key: state.get(state_key, "")}

    return pause_node
