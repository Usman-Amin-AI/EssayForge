"""Standalone Python version of the Wikipedia/Arxiv research notebook."""
from __future__ import annotations

from typing import Annotated

from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list, add_messages]


def build_demo_graph(api_key: str | None = None):
    """Construct a small tool-using LangGraph chatbot."""
    arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=300)
    arxiv_tool = ArxivQueryRun(api_wrapper=arxiv_wrapper)

    wikipedia_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=300)
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia_wrapper)

    tools = [arxiv_tool, wiki_tool]
    llm = ChatGroq(groq_api_key=api_key or "YOUR_GROQ_API_KEY", model_name="Gemma2-9b-It")
    llm_with_tools = llm.bind_tools(tools=tools)

    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile()


def run_demo(user_input: str = "Hi there! My name is Alex"):
    """Run a sample conversation through the demo graph."""
    try:
        from langgraph.prebuilt import ToolNode, tools_condition
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Install langgraph with prebuilt support to run the demo graph.") from exc

    graph = build_demo_graph()
    events = graph.stream({"messages": [HumanMessage(content=user_input)]}, stream_mode="values")
    return list(events)


if __name__ == "__main__":
    for event in run_demo():
        print(event)
