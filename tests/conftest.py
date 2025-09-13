import zipfile
from pathlib import Path
import sys
import os
import importlib
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import db, ingest, models


@pytest.fixture(scope="session")
def sample_zip(tmp_path_factory) -> Path:
    project_dir = Path("data/sample_project")
    zip_path = tmp_path_factory.mktemp("data") / "project.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in project_dir.rglob("*"):
            zf.write(file, file.relative_to(project_dir))
    return zip_path


@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    db_path = tmp_path / "sred.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    importlib.reload(db)
    importlib.reload(models)
    importlib.reload(ingest)
    db.init_db()
    yield
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def ingested(sample_zip):
    ingest.ingest_zip(sample_zip)
    yield
