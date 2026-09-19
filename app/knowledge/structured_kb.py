import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import DATA_DIR

def _load(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text())

_INTERVENTIONS = _load("interventions.json")
_METRICS = _load("metrics.json")

def all_interventions() -> List[Dict[str, Any]]:
    return _INTERVENTIONS

def metric_meta(name: str) -> Optional[Dict[str, Any]]:
    return _METRICS.get(name)

def metric_health(name: str, value: float) -> str:
    m = _METRICS.get(name)
    if not m or value is None:
        return "unknown"
    if m["direction"] == "higher_better":
        return "healthy" if value >= m.get("healthy_min", 0) else "degraded"
    if m["direction"] == "lower_better":
        return "healthy" if value <= m.get("healthy_max", 1e9) else "degraded"
    lo, hi = m.get("healthy_min", -1e9), m.get("healthy_max", 1e9)
    return "healthy" if lo <= value <= hi else "degraded"
