"""Utility for comparing two draft versions of an essay."""
from __future__ import annotations

import difflib
from typing import Any, Dict, List


def compare_drafts(old_draft: str, new_draft: str, reason: str | None = None) -> Dict[str, Any]:
    """Diff two drafts and summarize the changed sections and rationale."""
    matcher = difflib.SequenceMatcher(None, old_draft.splitlines(), new_draft.splitlines())
    changes: List[Dict[str, Any]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        changes.append(
            {
                "kind": tag,
                "old": "\n".join(old_draft.splitlines()[i1:i2]),
                "new": "\n".join(new_draft.splitlines()[j1:j2]),
            }
        )
    return {
        "changed": bool(changes),
        "changes": changes,
        "reason": reason or "Revision applied",
        "summary": "Changed sections: " + (", ".join(c["kind"] for c in changes) if changes else "none"),
    }
