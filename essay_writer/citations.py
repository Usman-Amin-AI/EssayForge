"""Helpers for source tagging, citation validation, and bibliography generation."""
from __future__ import annotations
import re
from typing import Any, Dict, List, Optional, Sequence


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def build_source_map(research_sources: Sequence[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Build a mapping from source id to research source metadata."""
    source_map: Dict[int, Dict[str, Any]] = {}
    for source in research_sources:
        source_id = source.get("id")
        if not isinstance(source_id, int):
            source_id = len(source_map) + 1
        source_map[source_id] = source
    return source_map


def attach_source_markers(draft: str, research_sources: Sequence[Dict[str, Any]]) -> str:
    """Attach inline citation markers to sentences that appear to reflect research content."""
    if not draft or not research_sources:
        return draft

    source_map = build_source_map(research_sources)
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", draft.strip()) if segment.strip()]

    annotated_sentences: List[str] = []
    for sentence in sentences:
        if re.search(r"\[(\d+)\]", sentence):
            annotated_sentences.append(sentence)
            continue

        best_source_id: Optional[int] = None
        best_score = 0
        sentence_tokens = set(_normalize_text(sentence).split())
        for source_id, source in source_map.items():
            content = source.get("content", "")
            source_tokens = set(_normalize_text(content).split())
            if not source_tokens or not sentence_tokens:
                continue
            overlap = len(source_tokens & sentence_tokens)
            if overlap > best_score:
                best_score = overlap
                best_source_id = source_id

        if best_source_id is not None and best_score >= 2:
            annotated_sentences.append(f"{sentence} [{best_source_id}]")
        else:
            annotated_sentences.append(sentence)

    return "\n".join(annotated_sentences)


def validate_citations(draft: str, research_sources: Sequence[Dict[str, Any]]) -> str:
    """Return a validation message describing whether research-derived claims are cited."""
    if not research_sources:
        return "No research sources were provided."

    source_map = build_source_map(research_sources)
    sentences = [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", draft.strip()) if segment.strip()]
    uncited_sentences: List[str] = []

    for sentence in sentences:
        sentence_tokens = set(_normalize_text(sentence).split())
        if not sentence_tokens:
            continue
        has_citation = bool(re.search(r"\[(\d+)\]", sentence))
        if has_citation:
            continue

        best_score = 0
        for source in source_map.values():
            content = source.get("content", "")
            source_tokens = set(_normalize_text(content).split())
            overlap = len(source_tokens & sentence_tokens)
            if overlap > best_score:
                best_score = overlap

        if best_score >= 2:
            uncited_sentences.append(sentence)

    if uncited_sentences:
        return f"Warning: {len(uncited_sentences)} sentence(s) appear to reflect research content without inline citations."
    return "All research-derived claims are cited."


def _format_author(author: Any, style: str) -> str:
    if not author:
        return ""
    if isinstance(author, (list, tuple)):
        author = ", ".join(str(item) for item in author)
    author_str = str(author).strip()
    if style.upper() == "MLA":
        if "," in author_str:
            return author_str
        return author_str
    return author_str


def format_reference(source: Dict[str, Any], style: str = "APA") -> str:
    """Format a research source as APA or MLA reference text."""
    style = style.upper()
    title = source.get("title") or source.get("name") or source.get("source") or "Untitled"
    author = source.get("author") or source.get("authors") or source.get("source_author") or ""
    year = source.get("year") or source.get("published") or "n.d."
    source_name = source.get("source") or source.get("publisher") or source.get("source_name") or "Unknown source"
    url = source.get("url") or source.get("link") or ""

    author_text = _format_author(author, style)
    if style == "MLA":
        base = f'{author_text}. "{title}". {source_name}, {year}.'
        return f"{base} {url}".strip()

    if author_text:
        base = f"{author_text} ({year}). {title}."
    else:
        base = f"{title}. ({year})."
    if source_name:
        base = f"{base} {source_name}."
    if url:
        base = f"{base} {url}"
    return base.strip()


def build_bibliography(
    draft: str,
    research_sources: Sequence[Dict[str, Any]],
    style: str = "APA",
) -> str:
    """Build a bibliography from the sources cited in the draft."""
    if not research_sources:
        return "References\n\nNo sources were cited."

    source_map = build_source_map(research_sources)
    cited_ids = sorted({int(match.group(1)) for match in re.finditer(r"\[(\d+)\]", draft) if match.group(1).isdigit()})
    cited_sources = [source_map[source_id] for source_id in cited_ids if source_id in source_map]
    if not cited_sources:
        return "References\n\nNo sources were cited."

    lines = ["References"]
    for index, source in enumerate(cited_sources, start=1):
        lines.append(f"{index}. {format_reference(source, style=style)}")
    return "\n".join(lines)
