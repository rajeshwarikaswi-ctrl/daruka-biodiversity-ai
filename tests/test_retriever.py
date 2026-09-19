from app.knowledge.retriever import retrieve

def test_retrieval_returns_sources():
    hits = retrieve("legume cover crops soil organic carbon", k=3)
    assert hits, "expected retrieval hits"
    assert all("source" in h for h in hits)
