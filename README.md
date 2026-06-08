# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

The domain selected is the **UCF Student Housing & Campus Survival Guide**. It focuses on navigating the complexities of housing eligibility, application timelines, residence hall regulations, dining memberships, and campus parking/transportation at the University of Central Florida.

This knowledge is highly valuable yet notoriously difficult to find because official university policy facts are fragmented across various departmental web pages, complex housing agreements, and lengthy legal PDF handbooks. Conversely, student perspectives are scattered across unverified, unstructured Reddit threads. This system bridges that gap by centralizing official rules alongside real-world student context while maintaining strict programmatic grounding to separate legal facts from casual observations.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | UCF Housing — Community Living Guide (landing page) | Official UCF page | https://www.housing.ucf.edu/community-living-guide/ |
| 2 | UCF Community Living Guide — full handbook (CLG-4_16_26, April 2026 rev.) | Official UCF PDF | https://www.housing.ucf.edu/wp-content/uploads/sites/97/2026/04/CLG-4_16_26.pdf |
| 3 | UCF Housing Options (agreement types & communities) | Official UCF page | https://www.housing.ucf.edu/housing-options/ |
| 4 | UCF Housing Eligibility (by student classification) | Official UCF page | https://www.housing.ucf.edu/apply/ |
| 5 | UCF Housing — How to Apply (steps & timelines) | Official UCF page | https://www.housing.ucf.edu/apply/howto/ |
| 6 | UCF Housing — Safety (locking rules, hurricane prep) | Official UCF page | https://www.housing.ucf.edu/safety/ |
| 7 | UCF Open Housing Options (cross-sex matching rules) | Official UCF page | https://www.housing.ucf.edu/question/open-housing-options/ |
| 8 | UCF Dining Options FAQ (+ meal membership terms) | Official UCF page | https://www.ucf.edu/admissions/undergraduate/question/what-are-my-dining-options/ |
| 9 | UCF Downtown Transportation & Parking | Official UCF page | https://www.ucf.edu/downtown/transportation/ |
| 10 | UCF Housing Terms & Conditions 2025–2026 (binding agreement) | Official UCF PDF | https://www.housing.ucf.edu/wp-content/uploads/sites/97/2025/09/Housing-terms-and-conditions-2025-2026-FE_Revised-3-4-25-UPDATED.pdf |
| 11 | UCF Golden Rule Student Handbook 2025–2026 | Official UCF PDF | https://scai.sswb.ucf.edu/wp-content/uploads/sites/52/2025/07/Golden-Rule-Student-Handbook-25-26.pdf |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
