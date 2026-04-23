# Climate Media Project — Master Analysis Plan
**"Klimatický rozvrat a média veřejné služby"**
Andrea Culková (PI) | Michal (analyst/developer) | Updated: 2026-04-23

> Legend: ✅ DONE · 🔄 PARTIAL (built, needs follow-up) · ⬜ TODO/BLOCKED · 🆕 NEW (out of original scope)

---

## Key Documents

| File | Purpose | Audience |
|------|---------|----------|
| `FINDINGS.md` | **All research findings** — 9 findings with numbers, tables, interpretations | Andrea, co-authors |
| `analysis/article4/CS{1,2,3}_analysis.md` | Case study discourse analyses | Andrea (review Key Observations) |
| `docs/index.html` | Czech public summary page — GitHub Pages at michalskop.github.io/ct-climate-media | FAMU public |
| `TECHNICAL_NOTES.md` | Implementation traps and recipes | Developer |

## Pending Manual Work

| File | Who | What |
|------|-----|------|
| `data/stance_validation_sample.csv` (182 rows) | Michal/Andrea | Fill `correct_stance` column → LLM accuracy score |
| `data/validation_sample_p26.csv` (80 rows) | Michal | Fill `correct_type` column → Phase 2 accuracy score |
| `data/topic_labels_nmf20.csv` | Andrea | Verify T13–T19 labels look right |
| `analysis/article4/CS{1,2,3}_analysis.md` | Andrea | Review/edit Key Observations sections |
| `public/index.html` | Andrea + Tomáš Šín | Review Czech text; deploy to FAMU server (contact: +420 234 244 308) |

---

## Open Questions

| ID | Question | Status |
|----|----------|--------|
| ~~Q1~~ | What is `sic_articles_truncated.csv`? | ✅ **RESOLVED:** SIC = social issues (4,853 docs); terrorism = debt enforcement (`exekuce`) |
| ~~Q2~~ | Is COVID subcorpus a separate file? | ✅ **RESOLVED:** `covid_articles_v2_truncated.csv` (33,284 docs) |
| ~~Q3~~ | NER lists format from Irene Elmerot? | ✅ **RESOLVED:** Not needed — built own speaker extraction pipeline |
| ~~Q4~~ | Sketch Engine access? | ✅ **RESOLVED:** Not used — collocate analysis done in Python |
| Q5 | FAMU page hosting infrastructure? | 🔄 HTML built (`public/index.html`); deployment pending — Tomáš Šín +420 234 244 308 |

---

## PHASE 0 — Infrastructure & Audit ✅ COMPLETE

| ID | Task | Status |
|----|------|--------|
| P0.1 | GitHub repository setup | ✅ https://github.com/michalskop/ct-climate-media |
| P0.2 | Document all corpus files | ✅ `CORPORA_INVENTORY.md` |
| P0.3 | Audit existing R/Python scripts | ✅ 29 files migrated |
| P0.4 | Verify all corpora load in Python | ✅ `data_check.py` — all 10 files load OK |
| P0.5 | Identify SIC subcorpus content | ✅ SIC = social issues; debt enforcement ≠ terrorism |

---

## PHASE 1 — Data Foundations ✅ COMPLETE

| ID | Task | Status | Output |
|----|------|--------|--------|
| P1.1 | Verify climate subcorpus v4 keywords | ✅ | 12 motorway false positives (0.4%) noted |
| P1.2 | Confirm social/poverty subcorpus | ✅ | 4,853 docs, 7 active keywords |
| P1.3 | Confirm motorist subcorpus | ✅ | 63,496 docs |
| P1.4 | Confirm COVID subcorpus | ✅ | 33,284 docs; pre-2020 false positives noted |
| P1.5 | Confirm debt enforcement subcorpus | ✅ | Not terrorism — Czech bailiff proceedings |
| P1.6 | Subcorpus size comparison table | ✅ | `analysis/article1/subcorpus_sizes.py` |
| P1.7 | Country name lookup table (Czech variants) | ✅ | `country_variants.csv` — 491 rows |
| P1.8 | Country detection — all 5 subcorpora | ✅ | `data/country_counts_*.csv` |
| P1.9 | Country detection — climate subcorpus | ✅ | CZE=2076, USA=951, High income=75.6% |
| P1.10 | Palestine vs Israel check | ✅ | ISR=79, PSE=13 → 6:1 ratio confirmed |
| P1.11 | World map — climate subcorpus | ✅ | `visualizations/article5/P1.11_world_map_climate_v2.png` |
| P1.12 | GNI yearly trend charts | ✅ | `visualizations/article1/P1.12_gni_trends_climate.png` |
| P1.13 | Subcorpus size bar chart | ✅ | `visualizations/article5/P1.13_subcorpus_sizes_v2.png` |
| P1.14 | Monthly time-series chart | ✅ | `visualizations/article1/P1.14_monthly_timeseries.png` |
| P1.15 | Per-article tables with show names | ⬜ BLOCKED | Show names absent from corpus files; needs Newton Media API |

---

## PHASE 2 — Actor Detection & Classification ✅ COMPLETE

| ID | Task | Status | Output |
|----|------|--------|--------|
| P2.1–P2.3 | Speaker extraction (regex, ALL CAPS surname pattern) | ✅ | `analysis/article2/speaker_extraction.py` |
| P2.4 | LLM classification M1–M6 (Claude Haiku, ~$0.20) | ✅ | 95.2% rule-based; 1,168 pairs via LLM |
| P2.5 | Gender classification (suffix rule + correction pass) | ✅ | `analysis/article2/gender_correction.py` |
| P2.6 | Validation sample (80 rows) | 🔄 | `data/validation_sample_p26.csv` — **fill `correct_type` column** |
| P2.7 | Master speaker table | ✅ | `data/speakers_final.csv` — 4,960 unique (name, role) pairs |
| P2.8–P2.9 | Salience scores + marginalization analysis | ✅ | Finding 3: citizens=2.0%, scientists outnumbered 2.6:1 by politicians |
| P2.10 | Speaker type distribution chart | ✅ | `visualizations/article5/P2.1_speaker_types_by_year_v2.png` |
| P2.11 | Gender breakdown by type chart | ✅ | `visualizations/article5/P2.2_gender_by_type_v2.png` |
| P2.12 | Top 20 speakers chart | ✅ | `visualizations/article2/P2.3_top20_speakers.png` |

---

## PHASE 3 — Stance, Topics & TJ Assessment ✅ COMPLETE

| ID | Task | Status | Output |
|----|------|--------|--------|
| P3.1–P3.2 | Stance prompt + LLM classification S0–S6 (~$2.15) | ✅ | `data/stance_results.csv` — 5,928 segments |
| P3.3 | Stance validation sample (182 rows) | 🔄 | `data/stance_validation_sample.csv` — **fill `correct_stance` column** |
| P3.4 | Stance distribution analysis | ✅ | S6=82.2%, S1=2.3%, no M3 ever S1 |
| P3.5 | False balance detection | ✅ | 10.2% of non-neutral articles show false balance |
| P3.6 | Stance visualizations | ✅ | `visualizations/article3/P3.4–P3.6_stance_*.png` |
| P3.7–P3.8 | NMF topic modeling (k=10,15,20,25) | ✅ | `data/topics_nmf_20.csv` — k=20 selected |
| P3.9 | LDA comparison | ⬜ NOT DONE | Skipped — NMF sufficient for publication |
| P3.10 | Topic labels | 🔄 | `data/topic_labels_nmf20.csv` — **verify T13–T19** |
| P3.11–P3.12 | Mitigation vs adaptation; link topics to speakers | ✅ | Finding 7: science topics 33%→13% (2012→2022) |
| P3.13 | Topic visualizations (static) | ✅ | `visualizations/article3/P3.7–P3.8_topic_*.png` |
| P3.13 | Interactive topic model (pyLDAvis) | ⬜ NOT DONE | Existing `climate-topics.netlify.app` can serve this |
| P3.14–P3.17 | Frequency + collocate analysis | ✅ | `data/frequency_combined.csv`; `visualizations/article3/P3.1–P3.3_*.png` |
| P3.18–P3.19 | TJ assessment | ✅ | `data/tj_assessment.csv`; scores: De-polar 7, Urgency 3, Just 1.5 |

---

## PHASE 4 — Case Studies ✅ COMPLETE

| ID | Task | Status | Output |
|----|------|--------|--------|
| P4.1 | CS1: Nuclear & renewables (88 docs) | ✅ | `analysis/article4/CS1_analysis.md` |
| P4.2 | CS2: Drought & floods (586 docs) | ✅ | `analysis/article4/CS2_analysis.md` |
| P4.3 | CS3: Health impacts — silence (17 docs) | ✅ | `analysis/article4/CS3_analysis.md` |
| P4.4 | Discourse analysis + excerpts for each | 🔄 | Key Observations written; **Andrea to review/edit** |

---

## PHASE 5 — Visual Unification & Public Page ✅ COMPLETE

| ID | Task | Status | Output |
|----|------|--------|--------|
| P5.1 | Unified style module | ✅ | `analysis/viz_style.py` — #8B1A1A, cream #FFFAF5 |
| P5.2 | Restyle all key charts | ✅ | `visualizations/article5/` — 9 charts with `_v2` suffix |
| P5.3–P5.5 | Czech public page with captions | ✅ | `docs/index.html` (985 KB, all charts embedded) |
| Deploy GitHub Pages | Enable Pages in repo settings | ⬜ | Settings → Pages → main branch → /docs → Save |
| Deploy FAMU | Mirror to FAMU server if needed | ⬜ | Contact Tomáš Šín +420 234 244 308 |

---

## PHASE 6 — Optional: Brussels / EU Climate Policy

| ID | Task | Status |
|----|------|--------|
| P6.1–P6.4 | EU Green Deal sentiment subcorpus analysis | 🆕 Not started — potential 4th article |

---

## Summary

| Phase | Status |
|-------|--------|
| 0 Infrastructure | ✅ Complete |
| 1 Data foundations | ✅ Complete (P1.15 blocked permanently) |
| 2 Speaker classification | ✅ Complete (validation CSV pending manual fill) |
| 3 Stance + topics + TJ | ✅ Complete (validation CSV + T13–T19 labels pending) |
| 4 Case studies | ✅ Complete (Key Observations need Andrea review) |
| 5 Style + public page | ✅ Complete (FAMU deployment pending) |
| 6 EU policy | 🆕 Optional future work |

*Last updated: 2026-04-23*
