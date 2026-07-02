import unittest

from essay_writer.nodes.research import make_research_plan_node
from essay_writer.research_tools import ResearchPipeline, SearchClientProvider


class DummyModel:
    def invoke(self, messages):
        class Response:
            content = "Draft text"

        return Response()

    def with_structured_output(self, schema):
        class Structured:
            def invoke(self, messages):
                class Queries:
                    queries = ["test query"]

                return Queries()

        return Structured()


class DummyProvider:
    source_name = "dummy"

    def search(self, query, max_results):
        return [
            {
                "content": "A factual claim about the topic.",
                "title": "Example Source",
                "url": "https://example.com",
            }
        ]


class ResearchSourceFlowTests(unittest.TestCase):
    def test_research_plan_node_returns_sources_for_bibliography(self):
        pipeline = ResearchPipeline(
            wikipedia_providers=[SearchClientProvider("wiki", DummyProvider())],
            web_providers=[SearchClientProvider("web", DummyProvider())],
            academic_providers=[],
        )
        node = make_research_plan_node(DummyModel(), pipeline)

        result = node({"task": "Test topic", "content": []})

        self.assertIn("research_sources", result)
        self.assertEqual(result["research_sources"][0]["title"], "Example Source")


if __name__ == "__main__":
    unittest.main()
