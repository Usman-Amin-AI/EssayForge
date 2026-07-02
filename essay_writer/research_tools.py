"""Research provider abstractions and search orchestration utilities."""
from __future__ import annotations
import random
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Protocol, TypedDict


class ResearchDocument(TypedDict, total=False):
    """A normalized document returned from a research provider."""

    source: str
    content: str
    url: str


class ResearchProvider(Protocol):
    """Defines the interface for a research provider."""

    source_name: str

    def search(self, query: str, max_results: int) -> List[ResearchDocument]:
        ...


def retry_with_backoff(func, max_attempts: int = 3, base_delay: float = 0.5, max_delay: float = 5.0):
    """Retry a callable with exponential backoff and jitter."""
    last_exception: Optional[Exception] = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func()
        except Exception as exc:  # noqa: BLE001
            last_exception = exc
            if attempt == max_attempts:
                raise
            delay = min(base_delay * 2 ** (attempt - 1), max_delay)
            jitter = random.uniform(0, base_delay)
            time.sleep(delay + jitter)
    raise last_exception  # pragma: no cover


def _normalize_search_results(raw_response: Any, source_name: str) -> List[ResearchDocument]:
    """Normalize search responses into a list of research documents."""
    if raw_response is None:
        return []

    results: List[Any]
    if isinstance(raw_response, dict) and "results" in raw_response:
        results = raw_response["results"]
    elif isinstance(raw_response, list):
        results = raw_response
    else:
        results = [raw_response]

    documents: List[ResearchDocument] = []
    for entry in results:
        if isinstance(entry, str):
            documents.append({"source": source_name, "content": entry})
            continue

        if not isinstance(entry, dict):
            continue

        content = entry.get("content") or entry.get("summary") or entry.get("text") or ""
        if not content:
            continue

        document: ResearchDocument = {
            "source": source_name,
            "content": content,
        }
        if "title" in entry and entry.get("title"):
            document["title"] = entry["title"]
        elif "name" in entry and entry.get("name"):
            document["title"] = entry["name"]
        if "url" in entry:
            document["url"] = entry["url"]
        elif "link" in entry:
            document["url"] = entry["link"]
        if "authors" in entry:
            document["authors"] = entry["authors"]
        if "year" in entry:
            document["year"] = entry["year"]
        if "publisher" in entry:
            document["publisher"] = entry["publisher"]
        documents.append(document)

    return documents


def _search_client_call(search_client: Any, query: str, max_results: int) -> Any:
    """Call a generic search client with fallback methods."""
    if hasattr(search_client, "search"):
        return search_client.search(query=query, max_results=max_results)
    if hasattr(search_client, "run"):
        return search_client.run(query)
    if hasattr(search_client, "invoke"):
        return search_client.invoke(query)
    if callable(search_client):
        return search_client(query, max_results=max_results)
    raise AttributeError("Search client does not support search, run, or invoke methods.")


@dataclass(frozen=True)
class SearchClientProvider:
    """Adapter for any search client to expose a ResearchProvider interface."""

    source_name: str
    search_client: Any

    def search(self, query: str, max_results: int) -> List[ResearchDocument]:
        raw_response = retry_with_backoff(
            lambda: _search_client_call(self.search_client, query, max_results)
        )
        return _normalize_search_results(raw_response, self.source_name)


@dataclass
class ResearchPipeline:
    """Selects providers and deduplicates returned research documents."""

    wikipedia_providers: List[ResearchProvider]
    web_providers: List[ResearchProvider]
    academic_providers: List[ResearchProvider]

    academic_keywords: List[str] = (
        "academic",
        "research paper",
        "arxiv",
        "study",
        "journal",
        "scientific",
        "science",
        "experiment",
        "theory",
        "evidence",
    )

    def select_providers(self, task: str) -> List[ResearchProvider]:
        task_lower = task.lower()
        if any(keyword in task_lower for keyword in self.academic_keywords):
            return [*self.academic_providers, *self.web_providers]
        return [*self.wikipedia_providers, *self.web_providers]

    def gather_texts(
        self,
        task: str,
        queries: List[str],
        existing_content: Optional[List[str]] = None,
        max_results: int = 2,
    ) -> dict[str, Any]:
        existing_content = list(existing_content or [])
        providers = self.select_providers(task)

        deduped_texts = {self._normalize_text(text) for text in existing_content}
        collected_texts: List[str] = []
        collected_sources: List[Dict[str, Any]] = []

        for query in queries:
            for provider in providers:
                documents = provider.search(query, max_results=max_results)
                for document in documents:
                    normalized = self._normalize_text(document["content"])
                    if normalized in deduped_texts:
                        continue
                    deduped_texts.add(normalized)
                    collected_texts.append(document["content"])
                    source_payload = dict(document)
                    source_payload.setdefault("id", len(collected_sources) + 1)
                    collected_sources.append(source_payload)

        return {
            "content": [*existing_content, *collected_texts],
            "research_sources": collected_sources,
        }

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join(text.lower().strip().split())
