from pathlib import Path

from essay_writer.compare import compare_drafts
from essay_writer.store import EssayRunStore


def test_store_persists_checkpoint_and_version(tmp_path):
    store = EssayRunStore(path=tmp_path / "runs.json")
    run = store.create_run("Test topic", {"style": "academic"})
    checkpoint = store.save_checkpoint(run["run_id"], {"plan": "outline"}, label="plan")
    version = store.save_version(run["run_id"], "draft-v1", {"draft": "draft"})

    assert checkpoint["label"] == "plan"
    assert version["label"] == "draft-v1"
    assert store.load_latest_checkpoint(run["run_id"])["label"] == "plan"


def test_compare_drafts_reports_changes():
    result = compare_drafts("Hello world", "Hello there", reason="clarity")
    assert result["changed"] is True
    assert result["reason"] == "clarity"
