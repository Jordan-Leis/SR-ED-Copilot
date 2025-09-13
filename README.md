# SR&ED Copilot Lite

A self-contained FastAPI service that helps prepare SR&ED documentation from markdown evidence. It ingests project files, tags snippets with SR&ED facets, supports TF-IDF search and patent lookup, and can generate a T661-style draft with citations or export a DOCX report.

## Features
- **Evidence Ingestion**: `POST /upload` accepts a zip containing `.md`/`.txt` docs and `commits.json`, splits text into overlapping chunks, and stores everything in SQLite.
- **Rule-based Tagging**: Uses `data/ontology.yaml` to tag chunks under facets such as Technological_Advancement or Evidence.
- **Search & Retrieval**: TF-IDF utilities power `/evidence` queries and draft generation.
- **SR&ED Drafting**: `POST /draft/sred` returns four template-based sections with inline citations like `[doc.md:10-50]`.
- **IP Scout**: `POST /ip_scout/search` performs cosine-similarity over a small patent CSV and returns a claim skeleton.
- **DOCX Export**: `POST /export/docx` streams a document containing a cover page, draft sections, and an evidence appendix.

## Project Layout
- `app/` – FastAPI app, DB models, ingestion, tagging, retrieval, exporters.
- `data/` – ontology, sample project, and seed patents.
- `static/` – assets for an HTMX/Tailwind UI.
- `tests/` – pytest suite covering all core features.

## Getting Started
Create a virtual environment and install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run the server:
```bash
uvicorn app.main:app --reload
```

Run tests:
```bash
pytest -q
```

### Quick Try
1. Zip the sample project:
```bash
cd data/sample_project && zip -r ../sample_project.zip . && cd ../../
```
2. Upload and ingest:
```bash
curl -F file=@data/sample_project.zip http://localhost:8000/upload
```
3. Fetch evidence tagged with a facet:
```bash
curl 'http://localhost:8000/evidence?facet=Technological_Advancement'
```
4. Generate a draft or search patents via the remaining endpoints.

---
`SR&ED Copilot Lite` stays deliberately small so an LLM agent can extend it with deeper reasoning or UI features.
