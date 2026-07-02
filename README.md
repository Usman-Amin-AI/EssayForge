# EssayForge

EssayForge is a Python package and web app for generating research-backed essays with LangGraph. The workflow covers planning, research gathering, drafting, reflection, citation tagging, bibliography generation, human review checkpoints, run persistence, and export-ready output.

## What the project includes

- A LangGraph workflow with planner, research, generation, reflection, critique, bibliography, and pause nodes
- A research abstraction that can be extended to multiple providers with retry/backoff and deduplication
- Inline source tracking so claims can be tagged and validated against the sources used
- APA/MLA bibliography support for the sources actually cited in the final draft
- A FastAPI-based web UI for generating and exporting essays
- A CLI entry point for running workflows from the terminal
- Persistence helpers for resuming runs and saving checkpoints

## Project structure

- [essay_writer/](essay_writer) — core workflow package
- [app_fastapi.py](app_fastapi.py) — FastAPI web application
- [essay_writer_run.py](essay_writer_run.py) — CLI entry point
- [templates/](templates) — HTML templates for the web UI
- [tests/](tests) — regression tests for graph behavior, citations, and persistence
- [essayforge_langgraph_workflow.ipynb](essayforge_langgraph_workflow.ipynb) — notebook version of the workflow
- [essayforge_wikipedia_research_demo.ipynb](essayforge_wikipedia_research_demo.ipynb) — notebook showing the research flow

## Installation

1. Clone the repository.
2. Create and activate a virtual environment if desired.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the CLI

Generate an essay from the terminal:

```bash
python essay_writer_run.py run --topic "Climate policy" --words 1200 --style academic
```

Resume a saved run:

```bash
python essay_writer_run.py run --topic "Climate policy" --words 1200 --style academic --resume <run_id>
```

## Running the web app

Start the server:

```bash
uvicorn app_fastapi:app --reload
```

Then open http://127.0.0.1:8000/.

## Deployment options

### Docker

```bash
docker build -t essayforge .
docker run -p 8000:8000 essayforge
```

### Platform deployment

The repository includes a [Procfile](Procfile) and [runtime.txt](runtime.txt) for services that support them.

## Notes

- The current demo setup uses placeholder model and provider adapters. Replace them with your preferred LLM or search integration for production use.
- Keep secrets and API keys outside the repository. Prefer environment variables or a local secrets file.
