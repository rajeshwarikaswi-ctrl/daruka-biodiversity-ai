from typing import List
from app.schemas import LandContext

REQUIRED_FOR_STRONG_RECS = [
    ("soil_organic_carbon_pct", "What is the soil organic carbon % (typical ag soils: 0.3-2%)?"),
    ("rainfall_mm_annual",     "What is the approximate annual rainfall (mm)?"),
    ("land_use",               "What is the current land use / crop (e.g. monoculture wheat, pasture)?"),
    ("region",                 "Which region/climate zone (e.g. semi-arid, tropical, temperate)?"),
]

def missing_metrics(ctx: LandContext) -> List[str]:
    d = ctx.model_dump(exclude_none=True)
    return [k for k, _ in REQUIRED_FOR_STRONG_RECS if k not in d]

def clarifying_questions(ctx: LandContext) -> List[str]:
    d = ctx.model_dump(exclude_none=True)
    return [q for k, q in REQUIRED_FOR_STRONG_RECS if k not in d]
