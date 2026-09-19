from typing import Dict, Any, List
from app.schemas import LandContext

def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def _matches(cond: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    for key, rule in cond.items():
        val = ctx.get(key)
        if val is None:
            continue
        if "max" in rule and _num(val) is not None and _num(val) > rule["max"]:
            return False
        if "min" in rule and _num(val) is not None and _num(val) < rule["min"]:
            return False
        if "includes" in rule and isinstance(val, str):
            if not any(tok in val.lower() for tok in rule["includes"]):
                return False
    return True

def select_interventions(ctx: LandContext, interventions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    payload = ctx.model_dump(exclude_none=True)
    matched = [iv for iv in interventions if _matches(iv.get("applies_when", {}), payload)]
    if not matched:
        matched = [iv for iv in interventions if not iv.get("applies_when")]
    return matched
