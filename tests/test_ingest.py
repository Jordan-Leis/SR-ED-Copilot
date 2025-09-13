

def test_ingest_creates_documents_and_tags(sample_zip):
    from app import ingest, models
    from app.db import SessionLocal

    doc_count, chunk_count = ingest.ingest_zip(sample_zip)
    assert doc_count == 3
    assert chunk_count == 3

    with SessionLocal() as session:
        facets = {t.facet for t in session.query(models.Tag).all()}
    assert {
        "Technological_Advancement",
        "Technological_Uncertainty",
        "Systematic_Investigation",
        "Evidence",
    } <= facets
