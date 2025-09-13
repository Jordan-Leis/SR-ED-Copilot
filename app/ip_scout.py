"""IP Scout utilities for simple patent search."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "seed_patents.csv"
TEMPLATES = Environment(loader=FileSystemLoader(Path(__file__).resolve().parents[0] / "templates"))


def _load_patents() -> list[dict[str, str]]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def search_patents(query: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """Return top-k patent numbers with similarity scores."""

    patents = _load_patents()
    abstracts = [p["abstract"] for p in patents]

    vectorizer = TfidfVectorizer().fit(abstracts)
    matrix = vectorizer.transform(abstracts)
    q_vec = vectorizer.transform([query])
    scores = (matrix @ q_vec.T).toarray().ravel()

    ranked = scores.argsort()[::-1][:top_k]
    return [(patents[i]["number"], float(scores[i])) for i in ranked]


def render_claim_skeleton(query: str) -> str:
    """Render a very naive claim skeleton based on the query words."""

    words = [w for w in query.split() if w.isalpha()]
    domain = words[0] if words else "technology"
    template = TEMPLATES.get_template("claim_skeleton.j2")
    return template.render(
        domain=domain,
        inputs="inputs",
        core_novel_step=query,
        outputs="outputs",
        differentiator="unique aspect",
    )

