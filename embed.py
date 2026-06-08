"""Milestone 2 — Embed chunks with all-MiniLM-L6-v2 into persistent ChromaDB.

Reads ``data/processed/chunks.jsonl`` produced by ``ingest.py``, embeds
the ``text`` field with ``sentence-transformers`` (``all-MiniLM-L6-v2``),
and writes the vectors plus their metadata into a persistent ChromaDB
collection under ``chroma_db/``.

Each chunk gets a stable ID of the form ``<file_stem>__<chunk_index:04d>``
so re-ingesting the same corpus does not duplicate entries. The collection
is dropped-and-recreated on every run so the store stays in sync with the
JSONL file.

Run from the project root:

    python embed.py
    python embed.py --peek 3      # also print 3 stored records
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_PATH = Path("data/processed/chunks.jsonl")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "ucf_housing"
EMBED_MODEL = "all-MiniLM-L6-v2"
BATCH_SIZE = 32


def load_chunks() -> list[dict]:
    if not CHUNKS_PATH.exists():
        raise SystemExit(f"ERROR: {CHUNKS_PATH} not found. Run ingest.py first.")
    records: list[dict] = []
    with CHUNKS_PATH.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def chunk_id(record: dict) -> str:
    stem = Path(record["source_file"]).stem
    return f"{stem}__{int(record['chunk_index']):04d}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--peek", type=int, default=0, help="Print N stored records after writing.")
    args = parser.parse_args()

    records = load_chunks()
    if not records:
        print("ERROR: no chunks to embed", file=sys.stderr)
        return 1
    print(f"Loaded {len(records)} chunks from {CHUNKS_PATH}")

    print(f"Loading embedding model: {EMBED_MODEL}")
    model = SentenceTransformer(EMBED_MODEL)

    CHROMA_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Dropped existing collection: {COLLECTION_NAME}")
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [r["text"] for r in records]
    print(f"Embedding {len(texts)} chunks...")
    vectors = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
    ).tolist()

    ids = [chunk_id(r) for r in records]
    metadatas = [
        {
            "source_file": r["source_file"],
            "chunk_index": int(r["chunk_index"]),
            "source_type": r["source_type"],
        }
        for r in records
    ]

    collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
    stored = collection.count()
    print(f"Stored {stored} vectors in collection '{COLLECTION_NAME}' at {CHROMA_DIR}/")
    if stored != len(records):
        print(
            f"WARNING: stored count ({stored}) does not match input chunk count ({len(records)})",
            file=sys.stderr,
        )

    if args.peek > 0:
        peek = collection.peek(limit=args.peek)
        print(f"\n--- first {args.peek} stored records ---")
        for i in range(len(peek["ids"])):
            print(f"id={peek['ids'][i]}  meta={peek['metadatas'][i]}")
            print(peek["documents"][i][:200], "...")
            print("-" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
