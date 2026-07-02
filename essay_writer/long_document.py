"""Simple long-document mode helpers for chapter-level assembly."""
from __future__ import annotations

from typing import Any, Dict, List


def build_long_document_sections(topic: str, sections: List[str], draft_text: str) -> Dict[str, Any]:
    """Create a chapter-style outline from the supplied sections and draft text."""
    chapters = []
    for index, section in enumerate(sections, start=1):
        chapters.append({"title": section, "content": f"{draft_text}\n\nSection {index}: {section}"})
    assembled = "\n\n".join(f"# {chapter['title']}\n\n{chapter['content']}" for chapter in chapters)
    return {"topic": topic, "sections": chapters, "assembled": assembled}
