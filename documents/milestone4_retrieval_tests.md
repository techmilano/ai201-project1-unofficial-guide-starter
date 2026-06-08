# Milestone 4 Retrieval Test Results

Embedding model: all-MiniLM-L6-v2
Vector store: ChromaDB
Collection: ucf_housing
Top-k: 4
Chunking: 600 characters with 120-character overlap

## Summary

Retrieval was tested against three planning.md evaluation questions before adding generation. The top retrieved chunks were manually inspected for relevance, distance score, source metadata, and whether they contained the expected answer.

## Q1 — Overnight guests

Query: `What rules apply to overnight guests or visitors in UCF housing?`

- **Rank 1** — `02_community_living_guide_full.txt` #23, distance **0.3158** — direct hit on Section 31. Contains the **3 consecutive nights**, **7 total nights**, **48-hour roommate notice**, and **2 guests max** rules. This single chunk alone covers the planning.md expected answer.
- Rank 2 — `06_safety.txt` #0, distance 0.3846 — safety overview; tangential, matched on "safety" semantics rather than guest policy.
- Rank 3 — `10_housing_terms_and_conditions.txt` #3, distance 0.3950 — relevant complement: Article 1.8 "Guest and visitor access" (host is responsible for guests' actions, may not admit banned individuals).
- Rank 4 — `02_community_living_guide_full.txt` #24, distance 0.3992 — continuation of Section 31 (clauses G/H). The 120-character overlap captured the tail of the rule.

**Verdict:** Relevant. Rank 1 alone is sufficient; ranks 3 and 4 add complementary context.

## Q2 — Electrical appliances and LED strip lights

Query: `What specific rules or limitations exist for electrical appliances and LED strip lights?`

- **Rank 1** — `02_community_living_guide_full.txt` #14, distance **0.4288** — contains the **adhesive-back LED strip lights not permitted** sentence plus surge-protector requirements.
- **Rank 2** — `02_community_living_guide_full.txt` #13, distance **0.5144** — start of Section 9 ELECTRICAL & APPLIANCES with **<1,000 watts** appliance limit and **<5 cubic feet** refrigerator limit.
- Rank 3 — `02_community_living_guide_full.txt` #15, distance 0.7128 — fire safety; relevance cliff.
- Rank 4 — `02_community_living_guide_full.txt` #22, distance 0.7197 — transportation; relevance cliff.

**Verdict:** Relevant. Ranks 1 + 2 together cover the entire expected answer (wattage, fridge size, LED prohibition). A clear distance jump from ~0.51 to ~0.71 separates "the rule" from "surrounding doc context".

## Q3 — Drops to 0 credit hours

Query: `What happens if a student drops to 0 credit hours while under contract?`

- **Rank 1** — `10_housing_terms_and_conditions.txt` #1, distance **0.4158** — exact hit on **Article 1.4**: "If a student drops to 0 credit hours, they must move out within **72 hours**." Single chunk contains the entire expected answer.
- Rank 2 — `10_housing_terms_and_conditions.txt` #9, distance 0.5230 — rental prepayment / payment terms; neighboring section, lower relevance but not wrong.
- Rank 3 — `10_housing_terms_and_conditions.txt` #14, distance 0.5254 — cancellation rules.
- Rank 4 — `10_housing_terms_and_conditions.txt` #15, distance 0.5274 — student-termination categories.

**Verdict:** Relevant. Rank 1 contains the full expected answer; ranks 2–4 are reasonable neighbors from the same legally binding document.

## Pattern across the three queries

- Top-1 distances cluster in **0.31–0.43** when the chunk contains the answer.
- A jump above **~0.50** marks where the chunk shifts from "the rule" to "the surrounding doc context".
- The 600/120 chunking is behaving as planning.md predicted: each numbered policy (Section 9, Section 31, Article 1.4) lands inside a single chunk, and the 20% overlap is catching tail clauses (visible in Q1, where chunk #24 picked up the end of Section 31 that #23 started).
- All top-k hits carry intact `source_file` + `chunk_index` metadata, so `query.py`'s programmatic citation step has the real filenames to attach in Milestone 5.

Retrieval is ready for grounded generation.
