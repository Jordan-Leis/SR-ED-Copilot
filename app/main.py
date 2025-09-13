"""FastAPI application entry point."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader

from .db import SessionLocal, init_db
from .exporters import export_docx
from .ingest import ingest_zip
from .models import Chunk, Document
from .rag import search
from .ip_scout import render_claim_skeleton, search_patents

app = FastAPI(title="SR&ED Copilot Lite")

TEMPLATES = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))


@app.on_event("startup")
def startup_event() -> None:
    """Initialize database on startup."""
    init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, int]:
    """Accept a zip file and ingest its contents."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)
    doc_count, chunk_count = ingest_zip(tmp_path)
    tmp_path.unlink(missing_ok=True)
    return {"documents": doc_count, "chunks": chunk_count}


@app.get("/evidence")
def evidence(facet: str | None = Query(default=None)) -> list[dict]:
    """Return chunks tagged with the given facet."""
    with SessionLocal() as session:
        q = session.query(Chunk, Document).join(Document)
        if facet:
            q = q.join(Chunk.tags).filter_by(facet=facet)
        results = [
            {
                "text": chunk.text,
                "path": doc.path,
                "start": chunk.start,
                "end": chunk.end,
            }
            for chunk, doc in q.all()
        ]
    return results


DEFAULT_QUERIES = {
    "Advancement": "novel architecture OR improve accuracy",
    "Uncertainty": "unknown OR unstable OR failed",
    "Systematic Investigation": "hypothesis OR experiment OR measured",
    "Evidence": "logs OR dataset OR appendix",
}


def _generate_sections() -> tuple[list[dict], list[dict]]:
    """Create SR&ED draft sections and citation metadata."""
    template = TEMPLATES.get_template("t661_section.j2")
    sections: list[dict] = []
    citations: list[dict] = []

    with SessionLocal() as session:
        for section, query in DEFAULT_QUERIES.items():
            ids = search(query, top_k=3)
            chunk_infos = []
            for cid in ids:
                chunk = session.get(Chunk, cid)
                if not chunk:
                    continue
                doc = session.get(Document, chunk.document_id)
                info = {
                    "text": chunk.text,
                    "path": doc.path if doc else "",
                    "start": chunk.start,
                    "end": chunk.end,
                }
                chunk_infos.append(info)
                citations.append(info)
            sections.append({"section": section, "text": template.render(section=section, chunks=chunk_infos)})

    return sections, citations


@app.post("/draft/sred")
def draft_sred() -> dict:
    """Generate a SR&ED draft with citations."""
    sections, citations = _generate_sections()
    return {"sections": sections, "citations": citations}


@app.post("/ip_scout/search")
def ip_scout(query: str) -> dict:
    patents = search_patents(query)
    skeleton = render_claim_skeleton(query)
    return {"results": patents, "claim": skeleton}


@app.post("/export/docx")
def export() -> FileResponse:
    sections, citations = _generate_sections()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        export_docx(sections, citations, Path(tmp.name))
        tmp_path = Path(tmp.name)
    return FileResponse(
        path=tmp_path,
        filename="sred_draft.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

