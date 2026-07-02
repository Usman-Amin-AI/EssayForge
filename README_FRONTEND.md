# EssayForge frontend

This document covers the web UI for EssayForge.

## Start the app

```bash
uvicorn app_fastapi:app --reload
```

Then open http://127.0.0.1:8000/.

## What you can do

- Enter a topic, writing style, and target word count
- Enable long-document mode and provide section titles
- Generate an essay and view the result in the browser
- Export the generated content as a document or PDF when supported by your environment

## Notes

The frontend is intentionally lightweight. It is designed to be a simple deployment-friendly interface while the core workflow remains in the Python package.
