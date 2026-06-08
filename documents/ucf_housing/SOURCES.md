# UCF Student Housing & Campus Survival Guide — Source Corpus (Milestone 1)

Domain: A RAG system answering questions about where to live at UCF, how housing works,
residence-hall rules, dining and parking options, and what students say about on-/off-campus
living — distinguishing official policy facts from anecdotal student experience.

Collected: 2026-06-07. All official UCF sources below were fetched and cleaned into plain
text. Student-generated (Reddit) sources are templated for manual collection (Reddit blocks
automated fetching; see each file).

## Official sources (policy / fact) — COLLECTED

| # | File | Source | URL |
|---|------|--------|-----|
| 1 | 01_community_living_guide_page.txt | UCF Housing — Community Living Guide (landing page) | https://www.housing.ucf.edu/community-living-guide/ |
| 2 | 02_community_living_guide_full.txt | UCF Community Living Guide — full PDF (CLG-4_16_26; current edition) | https://www.housing.ucf.edu/wp-content/uploads/sites/97/2026/04/CLG-4_16_26.pdf |
| 3 | 10_housing_terms_and_conditions.txt | UCF Housing Terms & Conditions 2025-2026 PDF | https://www.housing.ucf.edu/wp-content/uploads/sites/97/2025/09/Housing-terms-and-conditions-2025-2026-FE_Revised-3-4-25-UPDATED.pdf |
| 4 | 04_housing_eligibility.txt | UCF Housing Eligibility (Apply page) | https://www.housing.ucf.edu/apply/ |
| 5 | 03_housing_options.txt | UCF Housing Options page | https://www.housing.ucf.edu/housing-options/ |
| 6 | 05_how_to_apply.txt | UCF Housing How to Apply page | https://www.housing.ucf.edu/apply/howto/ |
| 7 | 06_safety.txt | UCF Housing Safety page | https://www.housing.ucf.edu/safety/ |
| 8 | 07_open_housing.txt | UCF Open Housing Options page | https://www.housing.ucf.edu/question/open-housing-options/ |
| 9 | 11_golden_rule_handbook.txt | UCF Golden Rule Student Handbook 2025-2026 PDF | https://scai.sswb.ucf.edu/wp-content/uploads/sites/52/2025/07/Golden-Rule-Student-Handbook-25-26.pdf |
| 10 | 08_dining_options.txt | UCF Dining Options FAQ (+ meal membership detail) | https://www.ucf.edu/admissions/undergraduate/question/what-are-my-dining-options/ |
| 11 | 09_downtown_transportation_parking.txt | UCF Downtown Transportation & Parking page | https://www.ucf.edu/downtown/transportation/ |

## Student-generated sources (anecdotal) — TO COLLECT MANUALLY

| # | File | Thread | Status |
|---|------|--------|--------|
| 12 | 12_reddit_first_year_survival_guide.txt | "The (Un)Official First Year UCF Survival Guide" | Required — paste content |
| + | 13_reddit_on_or_off_campus.txt | "On or off campus housing?" | Optional |
| + | 14_reddit_where_to_start_offcampus.txt | "I don't know where to start ... off campus housing" | Optional |
| + | 15_reddit_pointe_at_central.txt | "Pointe at Central" | Optional |
| + | 16_reddit_offcampus_horror_stories.txt | "Please tell me your off-campus housing horror stories" | Optional |

## Notes on fidelity / changes from the original list
- Source #2: your planning.md listed a "2024" Community Living Guide PDF. The current
  published edition is the April 16, 2026 revision (CLG-4_16_26.pdf), which is what was
  collected — better for a 2025-2026 project.
- Sources #3 and #9 (Terms & Conditions and Golden Rule) are rendered as structured,
  faithful summaries of long official PDFs, with the exact-text URL in each file header.
- The Dining file (#10) merges the admissions FAQ with official UCF Dining meal-membership
  details so the corpus can answer membership questions (Any 10/14, Knights 25/50/80, etc.).

## Which domain questions each source supports
- Eligibility / first-year priority (Q1, Q2): 04, 05, 10(T&C credit-hour rules)
- Agreement types & communities (Q3): 03, 04, 05
- Guests/visitors (Q4): 02 (CLG #31), 10 (T&C 1.8)
- Safety in residence halls (Q5): 06, 02 (CLG Health/Safety)
- Dining options/memberships (Q6): 08
- On- vs off-campus & specific complexes (Q7, Q8): 03 (affiliated: Knights Circle, Pointe at
  Central, UnionWest) + student threads 12-16
- Transfer-student housing (Q9): 04, 03
- Verify-with-official-sources (Q10): contrast official files 01-11 against student files 12-16
