"""Milestone 5 — Gradio interface for the UCF Unofficial Guide RAG system.

A minimal UI suitable for a 3–5 minute demo:
- one Question input
- a submit button (also fires on Enter)
- an Answer box (grounded, LLM-generated)
- a Sources box (deduped filenames pulled directly from retrieval)

Run from the project root:

    python app.py
"""

from __future__ import annotations

import gradio as gr

from query import ask

EXAMPLES = [
    "What rules apply to overnight guests or visitors in UCF housing?",
    "What specific rules or limitations exist for electrical appliances and LED strip lights?",
    "What happens if a student drops to 0 credit hours while under contract?",
    "Is UCF or DHRL responsible for a student's belongings if a hurricane causes damage?",
    "What are the operating parameters for the UCF Downtown Express Shuttles?",
]


def answer_question(question: str) -> tuple[str, str]:
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question.strip())
    if result["sources"]:
        sources_md = "\n".join(f"- `{s}`" for s in result["sources"])
    else:
        sources_md = "_(no sources retrieved)_"
    return result["answer"], sources_md


with gr.Blocks(title="UCF Unofficial Guide") as demo:
    gr.Markdown(
        "# UCF Unofficial Guide\n"
        "Ask a question about UCF housing, dining, safety, transportation, "
        "or student conduct. Answers come only from the official UCF source "
        "documents retrieved for your question."
    )
    question = gr.Textbox(
        label="Question",
        placeholder="e.g. What rules apply to overnight guests?",
        lines=2,
    )
    submit = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=10, show_copy_button=True)
    gr.Markdown("### Sources")
    sources = gr.Markdown()
    gr.Examples(examples=EXAMPLES, inputs=question)

    submit.click(answer_question, inputs=question, outputs=[answer, sources])
    question.submit(answer_question, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
