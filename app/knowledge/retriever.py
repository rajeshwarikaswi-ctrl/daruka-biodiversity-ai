"""
Chroma-based retriever using Chroma's built-in default embedding function.
No torch / sentence-transformers dependency (keeps deploy lightweight).
"""
from typing import List, Dict, Any
import chromadb
from app.config import CHROMA_DIR, DATA_DIR

_client = None
_collection = None

def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection
    _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    _collection = _client.get_or_create_collection("darukaa_corpus")
    if _collection.count() == 0:
        _ingest()
    return _collection

def _ingest():
    corpus_dir = DATA_DIR / "corpus"
    docs, ids, metas = [], [], []
    for fp in sorted(corpus_dir.glob("*.md")):
        text = fp.read_text()
        chunks = [c.strip() for c in text.split("\n\n") if len(c.strip()) > 40]
        for j, chunk in enumerate(chunks):
            ids.append(f"{fp.stem}-{j}")
            docs.append(chunk)
            metas.append({"source": fp.stem, "path": fp.name})
    if docs:
        _collection.add(ids=ids, documents=docs, metadatas=metas)

def retrieve(query: str, k: int = 5) -> List[Dict[str, Any]]:
    col = _get_collection()
    res = col.query(query_texts=[query], n_results=k)
    out = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        out.append({"text": doc, "source": meta.get("source"), "score": 1 - float(dist)})
    return out
