from typing import Dict, Any

def confidence(iv: Dict[str, Any], ctx: Dict[str, Any], evidence: list) -> float:
    base = 0.55
    base += min(0.15, 0.05 * len(iv.get("references", [])))
    keys = list(iv.get("applies_when", {}).keys())
    if keys:
        have = sum(1 for k in keys if ctx.get(k) is not None)
        base += 0.15 * (have / len(keys))
    else:
        base += 0.10
    base += min(0.10, 0.02 * len(evidence))
    return round(min(base, 0.95), 2)
