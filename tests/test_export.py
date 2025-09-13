from pathlib import Path

from app.exporters import export_docx


def test_export_docx(tmp_path):
    sections = [{"section": "Advancement", "text": "Example text"}]
    citations = [
        {"path": "doc1.md", "start": 0, "end": 10, "text": "snippet"}
    ]
    output_path = tmp_path / "out.docx"
    export_docx(sections, citations, output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0
