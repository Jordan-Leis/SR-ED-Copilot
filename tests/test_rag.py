

def test_search_filters_by_facet(ingested):
    from app.rag import search
    from app.models import Chunk, Document
    from app.db import SessionLocal

    ids = search("unknown behaviour", facets=["Technological_Uncertainty"])
    assert ids, "search returned no results"
    with SessionLocal() as session:
        chunk = session.get(Chunk, ids[0])
        doc = session.get(Document, chunk.document_id)
    assert doc.path.endswith("doc2.md")
