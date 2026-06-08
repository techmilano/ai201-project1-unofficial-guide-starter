"""Milestone 4 — Retrieval + grounded generation via Groq llama-3.3-70b-versatile.

``ask(question)`` runs ``retrieve.retrieve`` first, hands ONLY the top-k
chunks to the LLM as context, and instructs the model to answer strictly
from those excerpts (refusing with a fixed sentence otherwise).

Source attribution is **not** trusted to the LLM — it is appended
programmatically from the retrieval hits so the cited filenames are always
real corpus files (planning.md, Grounded Generation section).

Command-line test mode:

    python query.py "What rules apply to overnight guests?"
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve

load_dotenv()

LLM_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TOP_K = 4

REFUSAL = "I do not have enough information in the provided sources to answer that."

SYSTEM_PROMPT = (
    "You are a careful assistant for UCF student housing and campus survival questions. "
    "You must answer ONLY using the SOURCE EXCERPTS provided in the user message. "
    "Do not use outside knowledge, prior conversation, or assumptions about UCF. "
    "If the SOURCE EXCERPTS do not contain enough information to answer the question, "
    f'respond with EXACTLY this sentence and nothing else: "{REFUSAL}" '
    "When the excerpts do contain the answer, write a concise, factual response that "
    "only states what the excerpts state. "
    "Do NOT invent citations, URLs, or filenames in your response — source attribution "
    "is appended by the system after your reply."
)

_client: Groq | None = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        key = os.environ.get("GROQ_API_KEY")
        if not key or key == "your_key_here":
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        _client = Groq(api_key=key)
    return _client


def _format_context(hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits, start=1):
        blocks.append(
            f"[Excerpt {i} | source: {h['source_file']} | chunk {h['chunk_index']}]\n"
            f"{h['text']}"
        )
    return "\n\n".join(blocks)


def _build_user_prompt(question: str, hits: list[dict]) -> str:
    return (
        "SOURCE EXCERPTS:\n"
        f"{_format_context(hits)}\n\n"
        f"QUESTION: {question}\n\n"
        "Answer using only the excerpts above."
    )


def _collect_sources(hits: list[dict]) -> list[dict]:
    """Group retrieved hits by filename, preserving retrieval order.

    Returns ``[{"source_file": str, "chunk_indexes": [int, ...]}, ...]`` with
    one entry per distinct ``source_file``. Chunk indexes are ordered by the
    rank at which they were retrieved.
    """
    order: list[str] = []
    by_file: dict[str, list[int]] = {}
    for h in hits:
        f = h["source_file"]
        if f not in by_file:
            by_file[f] = []
            order.append(f)
        idx = int(h["chunk_index"])
        if idx not in by_file[f]:
            by_file[f].append(idx)
    return [{"source_file": f, "chunk_indexes": by_file[f]} for f in order]


def _format_sources_inline(sources: list[dict]) -> str:
    """Render the structured sources list as an inline citation string."""
    parts: list[str] = []
    for s in sources:
        idxs = s["chunk_indexes"]
        if len(idxs) == 1:
            parts.append(f"{s['source_file']} (chunk {idxs[0]})")
        else:
            parts.append(f"{s['source_file']} (chunks {', '.join(str(i) for i in idxs)})")
    return "; ".join(parts)


def _is_refusal(text: str) -> bool:
    """Match the refusal sentence, tolerating trailing punctuation/whitespace."""
    return text.strip().rstrip(".") == REFUSAL.rstrip(".")


def ask(question: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Run retrieval + grounded generation.

    Returns a structured object:

    .. code-block:: python

        {
            "answer": str,                # final answer (with citations appended unless refused)
            "sources": list[dict],        # deduped per-file, with chunk_indexes
            "retrieved_chunks": list[dict],  # raw top-k hits from retrieve()
        }
    """
    hits = retrieve(question, top_k=top_k)
    if not hits:
        return {"answer": REFUSAL, "sources": [], "retrieved_chunks": []}

    client = _get_client()
    response = client.chat.completions.create(
        model=LLM_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(question, hits)},
        ],
    )
    raw_answer = response.choices[0].message.content.strip()

    if _is_refusal(raw_answer):
        return {"answer": REFUSAL, "sources": [], "retrieved_chunks": hits}

    sources = _collect_sources(hits)
    answer_with_citations = f"{raw_answer}\n\nSources: {_format_sources_inline(sources)}"
    return {
        "answer": answer_with_citations,
        "sources": sources,
        "retrieved_chunks": hits,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python query.py "your question"', file=sys.stderr)
        return 1
    question = " ".join(sys.argv[1:])
    result = ask(question)
    print(result["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
