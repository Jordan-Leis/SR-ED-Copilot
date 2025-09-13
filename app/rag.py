"""Retrieval helpers based on TF-IDF vectors."""

from __future__ import annotations

from typing import List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .models import Chunk, Tag


def search(query: str, facets: List[str] | None = None, top_k: int = 5) -> List[int]:
    """Search stored chunks using a simple TF-IDF cosine similarity."""

    from .db import SessionLocal  # import inside to respect test fixture reloads

    with SessionLocal() as session:
        q = session.query(Chunk)
        if facets:
            q = q.join(Tag).filter(Tag.facet.in_(facets))
        chunks = q.all()

    texts = [c.text for c in chunks]
    if not texts:
        return []

    vectorizer = TfidfVectorizer().fit(texts)
    matrix = vectorizer.transform(texts)
    query_vec = vectorizer.transform([query])
    scores = (matrix @ query_vec.T).toarray().ravel()

    ranked_idx = np.argsort(scores)[::-1][:top_k]
    return [chunks[i].id for i in ranked_idx if scores[i] > 0]

