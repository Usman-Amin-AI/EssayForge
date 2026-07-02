"""CLI entry point for the essay writer package."""
from __future__ import annotations

import argparse
import json
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import GraphInterrupt
from langgraph.types import Command

from .config import EssayWriterConfig
from .graph import create_essay_writer_graph
from .research_tools import ResearchPipeline, SearchClientProvider
from .store import EssayRunStore


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "value"):
        return {
            "type": type(value).__name__,
            "value": _to_jsonable(getattr(value, "value")),
            "id": getattr(value, "id", None),
        }
    return str(value)


class DummyProvider:
    source_name = "dummy"

    def search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        return [
            {
                "content": f"Research context for {query}.",
                "title": "Example Source",
                "url": "https://example.com",
            }
        ]


def build_pipeline() -> ResearchPipeline:
    return ResearchPipeline(
        wikipedia_providers=[SearchClientProvider("wiki", DummyProvider())],
        web_providers=[SearchClientProvider("web", DummyProvider())],
        academic_providers=[],
    )


class DummyModel:
    def invoke(self, messages):
        class Response:
            content = "This is a generated essay draft."

        return Response()

    def with_structured_output(self, schema):
        class Structured:
            def invoke(self, messages):
                class Queries:
                    queries = ["topic overview"]

                return Queries()

        return Structured()


def run_cli(
    topic: str,
    words: int,
    style: str,
    resume: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    store = EssayRunStore()
    config = EssayWriterConfig(target_word_count=words, style=style, pause_for_human_approval=True)
    graph = create_essay_writer_graph(
        DummyModel(), build_pipeline(), config=config, store=store
    ).compile(checkpointer=MemorySaver())
    thread_config = {"configurable": {"thread_id": "essay-run"}}
    if resume:
        checkpoint = store.load_latest_checkpoint(resume)
        state = checkpoint["state"] if checkpoint else {"task": topic}
        state.setdefault("task", topic)
        state.setdefault("research_sources", [])
        try:
            result = graph.invoke(Command(resume=json.loads(resume)), config=thread_config)
            return result
        except GraphInterrupt as exc:
            return {"status": "interrupted", "interrupt": exc.value}

    run = store.create_run(topic, {"words": words, "style": style})
    run_id = run["run_id"]
    state = {
        "task": topic,
        "run_id": run_id,
        "max_revisions": config.max_reflect_cycles,
        "revision_number": 1,
        "research_sources": [],
    }

    try:
        result = graph.invoke(state, config=thread_config)
    except GraphInterrupt as exc:
        store.save_event(run_id, "interrupt", {"interrupt": str(exc.value)})
        return {"run_id": run_id, "status": "interrupted", "interrupt": exc.value}

    store.save_event(run_id, "completed", {"state": result})
    return {"run_id": run_id, **result}


def main() -> None:
    parser = argparse.ArgumentParser(prog="essay_writer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--topic", required=True)
    run_parser.add_argument("--words", type=int, default=1200)
    run_parser.add_argument("--style", choices=["academic", "persuasive", "narrative"], default="academic")
    run_parser.add_argument("--resume", default=None)
    run_parser.add_argument("--run-id", default=None)

    args = parser.parse_args()
    if args.command == "run":
        result = run_cli(args.topic, args.words, args.style, resume=args.resume, run_id=args.run_id)
        print(json.dumps(_to_jsonable(result), indent=2))


if __name__ == "__main__":
    main()
