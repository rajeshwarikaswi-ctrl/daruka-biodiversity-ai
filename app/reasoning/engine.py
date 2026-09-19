from typing import Dict, Any, List
from app.schemas import LandContext, Recommendation
from app.knowledge.structured_kb import all_interventions, metric_health, metric_meta
from app.knowledge.retriever import retrieve
from app.reasoning.rules import select_interventions
from app.reasoning.scorer import confidence

def _metrics_snapshot(ctx: LandContext) -> Dict[str, Any]:
    snap = {}
    for name, val in ctx.model_dump(exclude_none=True).items():
        m = metric_meta(name)
        if m and isinstance(val, (int, float)):
            snap[name] = {"value": val, "status": metric_health(name, val), "unit": m.get("unit")}
        else:
            snap[name] = {"value": val}
    return snap

def reason(ctx: LandContext, user_query: str) -> Dict[str, Any]:
    interventions = all_interventions()
    matched = select_interventions(ctx, interventions)

    recommendations: List[Recommendation] = []
    retrieved_all: List[Dict[str, Any]] = []

    for iv in matched:
        query = f"{iv['action']} {iv['rationale']} {user_query}"
        evidence = retrieve(query, k=3)
        retrieved_all.extend(evidence)
        conf = confidence(iv, ctx.model_dump(exclude_none=True), evidence)
        linked = _cross_metric_link(iv, ctx)

        rec = Recommendation(
            action=iv["action"],
            rationale=iv["rationale"] + ((" " + linked) if linked else ""),
            impacted_metrics=iv["impacted_metrics"],
            time_horizon=iv["time_horizon"],
            expected_effect="; ".join(f"{k}: {v}" for k, v in iv.get("effect_estimates", {}).items()),
            references=iv.get("references", []),
            confidence=conf,
        )
        recommendations.append(rec)

    recommendations.sort(key=lambda r: r.confidence, reverse=True)
    recommendations = recommendations[:4]

    return {
        "recommendations": recommendations,
        "retrieved_evidence": _dedupe(retrieved_all)[:6],
        "metrics_snapshot": _metrics_snapshot(ctx),
    }

def _cross_metric_link(iv: Dict[str, Any], ctx: LandContext) -> str:
    present = {k: v for k, v in ctx.model_dump(exclude_none=True).items()
               if isinstance(v, (int, float, str))}
    impacted = iv.get("impacted_metrics", [])
    if len(present) < 3:
        return ""
    drivers = [f"{k}={v}" for k, v in list(present.items())[:4]]
    return (f"Cross-metric reasoning: given {', '.join(drivers)}, this intervention "
            f"jointly affects {', '.join(impacted)}, coupling soil-water-biodiversity dynamics "
            f"rather than optimising a single variable.")

def _dedupe(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen, out = set(), []
    for it in items:
        key = (it.get("source"), it.get("text", "")[:60])
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out
