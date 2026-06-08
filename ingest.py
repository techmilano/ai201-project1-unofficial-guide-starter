"""Milestone 1 — Load, clean, and chunk UCF housing documents into JSONL.

Reads every ``.txt`` file under ``data/raw/ucf_housing/``, strips the
``SOURCE/URL/TYPE/...`` metadata header (preserving ``TYPE`` as
``source_type``), normalises whitespace, skips placeholder files (e.g.
Reddit stubs containing ``PASTE THREAD CONTENT BELOW THIS LINE``), then
splits each document into 600-character chunks with 120-character overlap
(20% sliding window, per planning.md Chunking Strategy).

Output: one JSON object per line in ``data/processed/chunks.jsonl`` with
fields ``source_file``, ``chunk_index``, ``source_type``, ``text``.

Run from the project root:

    python ingest.py
    python ingest.py --sample 5     # write JSONL, then print 5 random chunks
    python ingest.py --inspect      # Milestone 3 verification report (no write)
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

RAW_DIR = Path("data/raw/ucf_housing")
OUT_PATH = Path("data/processed/chunks.jsonl")

CHUNK_SIZE = 600
OVERLAP = 120

PLACEHOLDER_MARKERS = (
    "PASTE THREAD CONTENT BELOW THIS LINE",
    "PASTE CONTENT BELOW",
)
MIN_BODY_CHARS = 200


def is_placeholder(text: str) -> bool:
    """Return True if the file is a placeholder/stub, not real source content."""
    upper = text.upper()
    if any(marker in upper for marker in PLACEHOLDER_MARKERS):
        return True
    if len(text.strip()) < MIN_BODY_CHARS:
        return True
    return False


def parse_header(text: str) -> tuple[str, str]:
    """Strip the ``SOURCE/URL/TYPE/.../---`` header block.

    Returns ``(source_type, body)``. If no header block is present the
    whole text is treated as the body and ``source_type`` defaults to
    ``"official"``.
    """
    source_type = "official"
    lines = text.splitlines()
    sep_idx: int | None = None
    for i, line in enumerate(lines[:25]):
        if line.strip() == "---":
            sep_idx = i
            break
    if sep_idx is None:
        return source_type, text
    for line in lines[:sep_idx]:
        if line.startswith("TYPE:"):
            source_type = line.split(":", 1)[1].strip() or source_type
            break
    body = "\n".join(lines[sep_idx + 1 :])
    return source_type, body


def clean_text(text: str) -> str:
    """Collapse intra-line whitespace and drop empty lines."""
    text = re.sub(r"[ \t]+", " ", text)
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return "\n".join(lines)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list[str]:
    """Sliding-window character chunker.

    Yields chunks of up to ``chunk_size`` characters with ``overlap`` chars
    shared between successive chunks. Trailing whitespace-only chunks are
    dropped.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
    stride = chunk_size - overlap
    chunks: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == n:
            break
        start += stride
    return chunks


def iter_raw_files() -> list[Path]:
    return sorted(p for p in RAW_DIR.glob("*.txt"))


def build_chunks(verbose: bool = True) -> tuple[list[dict], list[tuple[str, str]]]:
    """Run the full pipeline in memory.

    Returns ``(records, skipped)`` where ``skipped`` is a list of
    ``(filename, reason)`` pairs for files that were not chunked.
    """
    records: list[dict] = []
    skipped: list[tuple[str, str]] = []
    files_kept = 0
    for path in iter_raw_files():
        raw = path.read_text(encoding="utf-8")
        if is_placeholder(raw):
            if verbose:
                print(f"SKIP placeholder: {path.name}")
            skipped.append((path.name, "placeholder/too-short"))
            continue
        source_type, body = parse_header(raw)
        cleaned = clean_text(body)
        if not cleaned:
            if verbose:
                print(f"SKIP empty after clean: {path.name}")
            skipped.append((path.name, "empty after clean"))
            continue
        chunks = chunk_text(cleaned)
        for i, chunk in enumerate(chunks):
            records.append(
                {
                    "source_file": path.name,
                    "chunk_index": i,
                    "source_type": source_type,
                    "text": chunk,
                }
            )
        if verbose:
            print(f"OK   {path.name}: {len(chunks)} chunks ({len(cleaned)} chars)")
        files_kept += 1
    if verbose:
        print(
            f"\nFiles kept: {files_kept}  skipped: {len(skipped)}  "
            f"total chunks: {len(records)}"
        )
    return records, skipped


def select_representative(records: list[dict], n: int = 5) -> list[dict]:
    """Pick ``n`` evenly-spaced chunks across the corpus.

    Because records are appended in file order, even spacing naturally
    spreads the sample across different source files.
    """
    if not records:
        return []
    if len(records) <= n:
        return list(records)
    step = (len(records) - 1) / (n - 1)
    return [records[round(i * step)] for i in range(n)]


def find_placeholder_chunks(records: list[dict]) -> list[tuple[str, int, str]]:
    """Return ``(source_file, chunk_index, marker)`` for any chunk that
    leaked a placeholder string."""
    contaminated: list[tuple[str, int, str]] = []
    for r in records:
        upper = r["text"].upper()
        for marker in PLACEHOLDER_MARKERS:
            if marker in upper:
                contaminated.append((r["source_file"], r["chunk_index"], marker))
                break
    return contaminated


def inspect_corpus() -> int:
    """Milestone 3 inspection — verify ingest without rewriting JSONL.

    Returns 0 on success, 1 if any chunk contains placeholder text.
    """
    print("=" * 64)
    print("MILESTONE 3 INSPECTION — ingestion & chunking verification")
    print("=" * 64)
    print(f"Chunk strategy: size={CHUNK_SIZE} chars, overlap={OVERLAP} chars  (planning.md)")
    print(f"Raw directory:  {RAW_DIR}\n")

    raw_files = iter_raw_files()
    if not raw_files:
        print(f"ERROR: no .txt files found in {RAW_DIR}", file=sys.stderr)
        return 1

    print(f"Per-file ingest:")
    records, skipped = build_chunks(verbose=True)
    docs_loaded = len(raw_files) - len(skipped)

    print()
    print("Summary")
    print("-------")
    print(f"  Total documents loaded:    {docs_loaded}")
    print(f"  Total chunks created:      {len(records)}")
    print(f"  Skipped placeholder files: {len(skipped)}")
    if skipped:
        for name, reason in skipped:
            print(f"    - {name}  [{reason}]")
    else:
        print("    (none)")

    contaminated = find_placeholder_chunks(records)
    print()
    print("Placeholder contamination check")
    print("-------------------------------")
    if contaminated:
        print(f"  FAIL — {len(contaminated)} chunk(s) contain placeholder text:")
        for sf, ci, marker in contaminated:
            print(f"    - {sf} #{ci}: contains {marker!r}")
    else:
        markers = ", ".join(repr(m) for m in PLACEHOLDER_MARKERS)
        print(f"  PASS — no chunk contains any of: {markers}")

    sample = select_representative(records, 5)
    print()
    print(f"5 representative chunks (full text, up to 600 chars)")
    print("----------------------------------------------------")
    for r in sample:
        print()
        print(
            f"[source_file={r['source_file']}  chunk_index={r['chunk_index']}  "
            f"type={r['source_type']}  len={len(r['text'])}]"
        )
        print(r["text"][:600])
        print("-" * 64)

    return 1 if contaminated else 0


def write_jsonl(records: list[dict]) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as out:
        for r in records:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote: {OUT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        metavar="N",
        help="After ingesting, print N random chunks for manual inspection.",
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help=(
            "Milestone 3 inspection mode: load, clean, and chunk the corpus, "
            "print docs/chunks/skipped counts plus 5 representative chunks, "
            "and verify no chunk contains placeholder text. "
            "Does NOT rewrite chunks.jsonl."
        ),
    )
    args = parser.parse_args()

    if not RAW_DIR.exists():
        print(f"ERROR: {RAW_DIR} does not exist", file=sys.stderr)
        return 1

    if args.inspect:
        return inspect_corpus()

    records, _ = build_chunks()
    if not records:
        print("ERROR: no chunks produced", file=sys.stderr)
        return 1
    write_jsonl(records)

    if args.sample > 0:
        print(f"\n--- {args.sample} random chunk sample ---")
        for r in random.sample(records, min(args.sample, len(records))):
            print(f"\n[{r['source_file']} #{r['chunk_index']}] type={r['source_type']}")
            print(r["text"])
            print("-" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
