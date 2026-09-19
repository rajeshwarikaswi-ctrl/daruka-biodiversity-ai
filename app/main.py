from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.conversation.session import store
from app.conversation.clarifier import clarifying_questions, missing_metrics
from app.reasoning.engine import reason
from app.llm.client import polish

app = FastAPI(title="Darukaa Biodiversity AI", version="1.0.0")

def _format_reply(result, questions) -> str:
    lines = []
    if questions:
        lines.append("To give you grounded, non-generic advice I need a bit more context:")
        lines += [f"  - {q}" for q in questions]
        lines.append("")

    if result["recommendations"]:
        lines.append("### Recommended interventions (evidence-backed)\n")
        for i, r in enumerate(result["recommendations"], 1):
            lines.append(f"**{i}. {r.action}**  _(confidence {r.confidence}, horizon: {r.time_horizon})_")
            lines.append(f"- Why: {r.rationale}")
            lines.append(f"- Impacts: {', '.join(r.impacted_metrics)}")
            lines.append(f"- Expected effect: {r.expected_effect}")
            lines.append(f"- References: {'; '.join(r.references)}")
            lines.append("")
    return "\n".join(lines)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    sid = req.session_id or store.new_id()
    store.add_turn(sid, "user", req.message)

    if req.context:
        ctx = store.update_ctx(sid, req.context)
    else:
        ctx = store.get_ctx(sid)

    result = reason(ctx, req.message)
    questions = clarifying_questions(ctx)

    reply = _format_reply(result, questions)
    polished = polish(
        "Rewrite the following structured report as a concise, readable answer "
        "for a land manager. Keep every fact, number and reference.\n\n" + reply
    )
    if polished:
        reply = polished

    store.add_turn(sid, "assistant", reply)

    return ChatResponse(
        session_id=sid,
        reply=reply,
        clarifying_questions=questions,
        recommendations=result["recommendations"],
        retrieved_evidence=result["retrieved_evidence"],
        missing_metrics=missing_metrics(ctx),
        metrics_snapshot=result["metrics_snapshot"],
    )

@app.get("/history/{sid}")
def history(sid: str):
    return {"turns": store.history(sid)}
