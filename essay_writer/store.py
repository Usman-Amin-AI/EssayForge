"""Simple JSON-backed persistence for essay runs and checkpoints."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "value"):
        return {"type": type(value).__name__, "value": _json_safe(getattr(value, "value")), "id": getattr(value, "id", None)}
    return str(value)


class EssayRunStore:
    """Persist essay runs, checkpoints, and draft versions as JSON."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path or Path(__file__).resolve().parent / "runs.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def _load(self) -> Dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, payload: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def create_run(self, topic: str, config: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load()
        run_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()
        run = {
            "run_id": run_id,
            "topic": topic,
            "created_at": now,
            "updated_at": now,
            "config": config,
            "events": [],
            "checkpoints": [],
            "versions": [],
        }
        data[run_id] = run
        self._save(data)
        return run

    def save_checkpoint(self, run_id: str, state: Dict[str, Any], label: str | None = None) -> Dict[str, Any]:
        data = self._load()
        run = data.setdefault(run_id, {"run_id": run_id, "events": [], "checkpoints": [], "versions": []})
        checkpoint = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "label": label or "checkpoint",
            "state": _json_safe(state),
        }
        run.setdefault("checkpoints", []).append(checkpoint)
        run["updated_at"] = checkpoint["timestamp"]
        data[run_id] = run
        self._save(data)
        return checkpoint

    def save_event(self, run_id: str, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load()
        run = data.setdefault(run_id, {"run_id": run_id, "events": [], "checkpoints": [], "versions": []})
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "payload": _json_safe(payload),
        }
        run.setdefault("events", []).append(event)
        run["updated_at"] = event["timestamp"]
        data[run_id] = run
        self._save(data)
        return event

    def save_version(self, run_id: str, label: str, state: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load()
        run = data.setdefault(run_id, {"run_id": run_id, "events": [], "checkpoints": [], "versions": []})
        version = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "label": label,
            "state": _json_safe(state),
        }
        run.setdefault("versions", []).append(version)
        run["updated_at"] = version["timestamp"]
        data[run_id] = run
        self._save(data)
        return version

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self._load().get(run_id)

    def list_runs(self) -> List[Dict[str, Any]]:
        return list(self._load().values())

    def load_latest_checkpoint(self, run_id: str) -> Optional[Dict[str, Any]]:
        run = self.get_run(run_id)
        checkpoints = run.get("checkpoints", []) if run else []
        return checkpoints[-1] if checkpoints else None
