"""Milestone 3 — Top-k semantic retrieval over the UCF housing ChromaDB.

Exposes ``retrieve(query, top_k=4)`` returning a list of hit dicts with
fields ``id``, ``text``, ``source_file``, ``chunk_index``, ``source_type``,
``distance`` — preserving the source metadata that ``embed.py`` stored, so
``query.py`` can ground its answers and cite real filenames.

The model and the Chroma collection are loaded lazily on first call and
cached at module scope so importers (``query.py``, ``app.py``) pay the
load cost only once per process.

Command-line test mode:

    python retrieve.py "What rules apply to overnight guests?"
"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "ucf_housing"
EMBED_MODEL = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 4

_model: SentenceTransformer | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        if not CHROMA_DIR.exists():
            raise RuntimeError(
                f"{CHROMA_DIR} does not exist. Run embed.py before retrieving."
            )
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """Return the top-k chunks for ``query``, sorted by ascending distance."""
    if not query or not query.strip():
        return []
    model = _get_model()
    collection = _get_collection()
    embedding = model.encode([query], convert_to_numpy=True).tolist()
    results = collection.query(
        query_embeddings=embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    ids = results["ids"][0]
    hits: list[dict] = []
    for i in range(len(docs)):
        hits.append(
            {
                "id": ids[i],
                "text": docs[i],
                "source_file": metas[i]["source_file"],
                "chunk_index": int(metas[i]["chunk_index"]),
                "source_type": metas[i].get("source_type", "official"),
                "distance": float(dists[i]),
            }
        )
    return hits


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python retrieve.py "your question"', file=sys.stderr)
        return 1
    query = " ".join(sys.argv[1:])
    print(f"Query: {query}\n")
    hits = retrieve(query)
    if not hits:
        print("(no hits)")
        return 0
    for h in hits:
        print(f"[{h['source_file']} #{h['chunk_index']}] distance={h['distance']:.4f}")
        print(h["text"])
        print("-" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
