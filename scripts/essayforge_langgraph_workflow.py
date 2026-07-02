"""Standalone Python version of the LangGraph essay workflow notebook."""
from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from tavily import TavilyClient

from essay_writer import create_essay_writer_graph


load_dotenv()


def build_workflow() -> Any:
    """Create and compile the essay-writing workflow graph."""
    memory = SqliteSaver.from_conn_string(":memory:")
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY", ""))
    builder = create_essay_writer_graph(model, tavily)
    return builder.compile(checkpointer=memory)


def run_demo(topic: str = "What is the difference between LangChain and LangSmith?") -> list[dict[str, Any]]:
    """Run the workflow for a sample topic and return emitted events."""
    graph = build_workflow()
    thread = {"configurable": {"thread_id": "demo-run"}}
    events: list[dict[str, Any]] = []
    for event in graph.stream(
        {
            "task": topic,
            "max_revisions": 2,
            "revision_number": 1,
        },
        thread,
    ):
        events.append(event)
    return events


if __name__ == "__main__":
    for item in run_demo():
        print(item)
