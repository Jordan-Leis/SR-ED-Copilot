"""Utilities for ingesting project evidence into the database."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Iterator, Tuple

from .models import Chunk, Document, Tag
from .rules import load_ontology, tag_chunk

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def _chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterator[tuple[int, int, str]]:
    """Yield ``(start, end, text)`` tuples for the provided text."""

    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        yield start, end, text[start:end]
        if end == len(text):
            break
        start = end - overlap


def ingest_zip(zip_path: Path) -> Tuple[int, int]:
    """Ingest a zip archive of markdown/text files.

    Extracts ``.md`` and ``.txt`` files, splits them into chunks and stores
    :class:`~app.models.Document`, :class:`~app.models.Chunk` and
    :class:`~app.models.Tag` entries. ``commits.json`` is currently ignored but
    accepted in the archive.

    Args:
        zip_path: Path to the uploaded archive.

    Returns:
        Tuple of ``(document_count, chunk_count)`` stored.
    """

    from .db import SessionLocal  # import inside to pick up test fixture reloads

    ontology = load_ontology()
    doc_count = 0
    chunk_count = 0

    with zipfile.ZipFile(zip_path) as zf, SessionLocal() as session:
        for member in zf.infolist():
            if member.filename.endswith((".md", ".txt")):
                doc_count += 1
                with io.TextIOWrapper(zf.open(member), encoding="utf-8") as f:
                    text = f.read()
                document = Document(project_id="default", path=member.filename, text=text)
                session.add(document)
                session.flush()  # obtain document.id

                for start, end, chunk_text in _chunk_text(text):
                    chunk = Chunk(document_id=document.id, start=start, end=end, text=chunk_text)
                    session.add(chunk)
                    session.flush()
                    chunk_count += 1

                    facets = tag_chunk(chunk_text, ontology)
                    for facet in facets:
                        session.add(Tag(chunk_id=chunk.id, facet=facet))

        session.commit()

    return doc_count, chunk_count

