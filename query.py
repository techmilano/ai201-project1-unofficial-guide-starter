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


def _dedupe_sources(hits: list[dict]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        f = h["source_file"]
        if f not in seen:
            seen.add(f)
            ordered.append(f)
    return ordered


def ask(question: str, top_k: int = DEFAULT_TOP_K) -> dict:
    """Return ``{"answer": str, "sources": list[str], "hits": list[dict]}``.

    ``answer`` already has the deduped source filenames appended (unless the
    model refused). ``sources`` is the same list as a structured field for
    the UI. ``hits`` is the raw retrieval result for debugging.
    """
    hits = retrieve(question, top_k=top_k)
    if not hits:
        return {"answer": REFUSAL, "sources": [], "hits": []}

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

    sources = _dedupe_sources(hits)
    if raw_answer.strip().rstrip(".") == REFUSAL.rstrip("."):
        return {"answer": REFUSAL, "sources": [], "hits": hits}

    answer_with_citations = f"{raw_answer}\n\nSources: " + ", ".join(sources)
    return {"answer": answer_with_citations, "sources": sources, "hits": hits}


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
