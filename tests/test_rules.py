"""Tests for rule tagging using sample data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import rules


def test_load_ontology_keys():
    ontology = rules.load_ontology()
    assert "Technological_Advancement" in ontology


def test_tag_chunk_matches_multiple_facets():
    ontology = rules.load_ontology()
    tags = rules.tag_chunk("prototype experiment failed attempt", ontology)
    assert "Systematic_Investigation" in tags
    assert "Technological_Uncertainty" in tags
