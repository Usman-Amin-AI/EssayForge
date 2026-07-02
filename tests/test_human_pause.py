from essay_writer.config import EssayWriterConfig
from essay_writer.nodes.pause import make_human_pause_node


def test_pause_node_applies_resume_content():
    def fake_interrupt(payload):
        return {"content": "Revised outline"}

    node = make_human_pause_node(
        stage_name="plan",
        state_key="plan",
        interrupt_fn=fake_interrupt,
        config=EssayWriterConfig(pause_for_human_approval=True),
    )

    result = node({"plan": "Original outline"})

    assert result["plan"] == "Revised outline"
