# EssayForge

EssayForge is a Python project for generating research-backed essays through a LangGraph workflow. The repository combines planning, research gathering, drafting, reflection, bibliography generation, and optional human review checkpoints in a single workflow that can be run from the terminal or through a lightweight web interface.

## What this project does

- Builds an essay-writing workflow with planner, research, generation, reflection, critique, bibliography, and pause nodes
- Uses a research pipeline that can gather content from multiple providers with retry handling and deduplication
- Stores runs, checkpoints, and draft versions so workflows can be resumed or inspected later
- Includes a FastAPI-based UI for simple topic submission and essay preview
- Ships with a CLI entry point for running the workflow directly from Python

## Project structure

- [essay_writer/](essay_writer) — core workflow package and graph implementation
- [app_fastapi.py](app_fastapi.py) — FastAPI web app entry point
- [essay_writer_run.py](essay_writer_run.py) — CLI runner for the workflow
- [templates/](templates) — HTML templates for the web UI
- [tests/](tests) — regression tests for pause handling, persistence, and research sources
- [scripts/](scripts) — helper scripts and demo utilities

## Requirements

- Python 3.11+
- pip and a virtual environment are recommended

## Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the CLI

The default demo workflow uses built-in dummy model and research providers, so you can run it immediately without external API credentials.

Generate an essay from the terminal:

```bash
python essay_writer_run.py run --topic "Climate policy" --words 1200 --style academic
```

Resume a previous run using its stored run ID:

```bash
python essay_writer_run.py run --topic "Climate policy" --words 1200 --style academic --resume <run_id>
```

## Running the web app

Start the FastAPI app:

```bash
uvicorn app_fastapi:app --reload
```

Then open http://127.0.0.1:8000/ in your browser.

The web form accepts a topic, writing style, target word count, and optional long-document section titles.

## Development and testing

Run the regression tests:

```bash
pytest
```

## Deployment notes

The repository includes a [Dockerfile](Dockerfile), [Procfile](Procfile), and [runtime.txt](runtime.txt) for container or platform-based deployment.

### Docker example

```bash
docker build -t essayforge .
docker run -p 8000:8000 essayforge
```

## Important note

This repository is currently a demo-oriented prototype. The default implementation uses placeholder model and research providers. To use real language models or search services, replace the dummy adapters in the workflow and research pipeline with your preferred integrations and keep any secrets in environment variables rather than in source control.
