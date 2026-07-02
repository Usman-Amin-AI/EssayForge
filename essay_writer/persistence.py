"""Helpers for saving graph state snapshots and resume data."""
from __future__ import annotations

from typing import Any, Callable

from .store import EssayRunStore


def make_persisting_node(label: str, store: EssayRunStore, run_id: str | None = None):
    """Wrap a node so its output is published into the JSON-backed store."""

    def persisted_node(state: dict[str, Any]) -> dict[str, Any]:
        run_key = run_id or state.get("run_id")
        if run_key:
            store.save_checkpoint(run_key, state, label=label)
            store.save_event(run_key, "node", {"node": label, "state": state})
        return state

    return persisted_node
