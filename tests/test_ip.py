from app.ip_scout import search_patents, render_claim_skeleton


def test_search_patents_returns_example():
    results = search_patents("adaptive beamforming")
    numbers = [r[0] for r in results]
    assert "US2019000001" in numbers


def test_render_claim_skeleton():
    claim = render_claim_skeleton("adaptive beamforming system")
    assert "adaptive" in claim
