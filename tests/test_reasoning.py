from app.schemas import LandContext
from app.reasoning.engine import reason

def test_semi_arid_wheat_returns_recommendations():
    ctx = LandContext(
        soil_organic_carbon_pct=0.3,
        rainfall_mm_annual=350.0,
        land_use="monoculture wheat",
        region="semi-arid",
    )
    out = reason(ctx, "Biodiversity is declining on my land")
    assert out["recommendations"], "expected at least one recommendation"
    assert all(r.references for r in out["recommendations"])

def test_multi_metric_linkage_present():
    ctx = LandContext(
        soil_organic_carbon_pct=0.3,
        rainfall_mm_annual=350.0,
        land_use="monoculture wheat",
        region="semi-arid",
    )
    out = reason(ctx, "test")
    joined = " ".join(r.rationale for r in out["recommendations"])
    assert "Cross-metric reasoning" in joined
