from __future__ import annotations

import os
import tempfile
import uuid
from typing import Any

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates

from essay_writer.cli import DummyModel, build_pipeline
from essay_writer.config import EssayWriterConfig
from essay_writer.exporters import export_docx, export_pdf
from essay_writer.graph import create_essay_writer_graph
from essay_writer.long_document import build_long_document_sections
from essay_writer.store import EssayRunStore

app = FastAPI(title="EssayForge")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/generate")
async def generate(
    topic: str = Form(...),
    style: str = Form("academic"),
    words: int = Form(1200),
    long_document: bool = Form(False),
    sections: str = Form(""),
) -> HTMLResponse:
    config = EssayWriterConfig(target_word_count=words, style=style, pause_for_human_approval=True)
    graph = create_essay_writer_graph(DummyModel(), build_pipeline(), config=config)
    result = graph.invoke(
        {
            "task": topic,
            "max_revisions": config.max_reflect_cycles,
            "revision_number": 1,
            "research_sources": [],
            "config": {"words": words, "style": style, "long_document": long_document, "sections": [s.strip() for s in sections.splitlines() if s.strip()]},
        }
    )
    final_text = result.get("draft", "") + "\n\n" + (result.get("bibliography", "") or "")
    if long_document:
        long_doc = build_long_document_sections(topic, [s.strip() for s in sections.splitlines() if s.strip()], final_text)
        final_text = long_doc["assembled"]
    run_id = str(uuid.uuid4())
    store = EssayRunStore(path=os.path.join(tempfile.gettempdir(), "essayforge_runs.json"))
    store.create_run(topic, {"style": style, "words": words})
    store.save_version(run_id, "final", {"draft": final_text})
    return templates.TemplateResponse(
        "result.html",
        {"request": Request({"type": "http"}), "topic": topic, "result": final_text, "run_id": run_id},
    )


@app.get("/export/{kind}")
async def export(kind: str) -> FileResponse:
    text = "Generated essay"
    temp_dir = tempfile.gettempdir()
    if kind == "docx":
        path = export_docx(text, os.path.join(temp_dir, "essay.docx"))
        return FileResponse(path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="essay.docx")
    path = export_pdf(text, os.path.join(temp_dir, "essay.pdf"))
    return FileResponse(path, media_type="application/pdf", filename="essay.pdf")
