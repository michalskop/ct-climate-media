# Phase 2 Summary — Actor Detection
**Project:** Klimatický rozvrat a média veřejné služby  
**Analyst:** Michal | **PI:** Andrea Culková  
**Completed:** 2026-04-23

---

## 1. Method

### Speaker extraction (P2.2–P2.3)
Regex pattern `(Jméno)\s+(PŘÍJMENÍ)\s+(role)` applied to all 2,914 climate subcorpus documents.  
Pattern exploits the Czech Television transcript convention: all-caps surname, lowercase role label immediately following.

**Results:** 56,613 speaker mentions, 3,824 unique names, 4,960 unique (name, role) pairs.

### Type classification (P2.3–P2.4)
Two-stage approach:

| Stage | Method | Resolved |
|-------|--------|----------|
| Rule-based | Keyword lookup (M1–M6 sets + modifier stripping) | 95.2% |
| LLM (Claude Haiku) | Batch classification of remaining pairs | +4.1% |
| Unresolved / SKIP | False positives + genuinely ambiguous | 0.7% |

LLM cost: ~$0.20 for 1,168 pairs (30/batch, claude-haiku-4-5-20251001).

### Gender classification (P2.5)
Czech surname suffix rule:
- Surname ends `-á` (all adjective-form: -ová, -ská, -ná…) → **F** (certain)
- Surname ends `-ů` (Janů, Petrů — both genders) → resolved by first name
- First name ends `-a` / `-e` → **F** (probable) — then corrected for known male foreign names (Joe, Claude, George, Luca, Ota, Jukka…)
- Otherwise → **M**

Correction pass removed all F? and ? categories; 286 rows reclassified.

---

## 2. Speaker Type Distribution

### Unique (name, role) pairs

| Type | Label | Unique pairs | % |
|------|-------|-------------:|--:|
| M1 | Journalist/anchor | 737 | 14.8% |
| M2 | Ordinary citizen | 609 | 12.3% |
| M3 | Scientist/academic | 630 | 12.7% |
| M4 | Pseudoscientist | 5 | 0.1% |
| M5 | Stakeholder (NGO/business) | 1,140 | 23.0% |
| M6 | Politician/official | 1,480 | 29.8% |
| ? | Unresolved | 359 | 7.2% |

### Mention counts (all 56,613 occurrences)

| Type | Mentions | % |
|------|--------:|--:|
| M1 | 31,034 | 54.8% |
| M6 | 12,797 | 22.6% |
| M5 | 6,240 | 11.0% |
| M3 | 4,871 | 8.6% |
| M2 | 1,143 | 2.0% |
| M4 | 87 | 0.2% |
| ? | 441 | 0.8% |

**Key finding:** M4 (pseudoscientist) is nearly absent from Czech Television climate coverage — only 87 mentions across 2,914 documents over 10 years. ČT did not platform climate deniers or alternative science voices at meaningful scale.

### Yearly trend
Notable peaks:
- **2019** — Global Climate Strikes (Greta Thunberg); largest single-year spike across all types
- **2021** — COP26 (Glasgow); strong politician (M6) surge

Chart: `visualizations/article2/P2.1_speaker_types_by_year.png`

---

## 3. Gender

### Female representation by type (mention counts)

| Type | % Female | Interpretation |
|------|--------:|----------------|
| M1 Journalist | **39.4%** | Closest to parity — ČT internal hiring |
| M2 Citizen | 30.3% | Reasonable street-interview balance |
| M6 Politician | 12.6% | Reflects political gender gap |
| M3 Scientist | 12.0% | Reflects academic gender gap + Czech academia |
| M5 Stakeholder | 10.7% | Lowest — NGO/business leadership skews male |

Overall female share across all classified mentions: **27.6%** (15,478 F / 40,709 M).

Chart: `visualizations/article2/P2.2_gender_by_type.png`

---

## 4. Top Speakers

To be added after producing `speakers_top.csv` (most-mentioned individuals per type).

---

## 5. Quality Check (P2.6)

Validation sample of 80 randomly selected (name, role, type) pairs stored at:  
`data/validation_sample_p26.csv`

Columns: `name`, `role_raw`, `type_final`, `gender_final`, `n_mentions`, `source`, `correct` (Y/N/?), `notes`

**Known issue spotted in sample:** row 8 — "Františka Čížková / módní kritička" classified M1 (journalist) but role suggests M5 (stakeholder/cultural commentator). Indicates boundary cases between M1 and M5 for invited commentators.

---

## 6. Outputs Produced

| File | Description |
|------|-------------|
| `analysis/article2/speaker_extraction.py` | Regex extraction + M1–M6 rule classifier |
| `analysis/article2/speaker_llm_classify.py` | LLM batch classifier (Claude Haiku) |
| `analysis/article2/gender_correction.py` | P2.5 gender correction pass |
| `data/speakers_all.csv` | 56,613 mention rows |
| `data/speakers_unique.csv` | 4,960 unique (name, role) pairs — rule-based |
| `data/speakers_for_llm.csv` | 1,168 pairs sent to LLM |
| `data/speakers_llm_results.csv` | Raw LLM classifications |
| `data/speakers_final.csv` | Final table with type_final + gender_final |
| `data/validation_sample_p26.csv` | 80-row manual validation sample |
| `visualizations/article2/P2.1_speaker_types_by_year.png` | Stacked bar: types by year |
| `visualizations/article2/P2.2_gender_by_type.png` | % female by speaker type |

---

## 7. Ready for Phase 3

Phase 3 input: `speakers_final.csv` with columns `name`, `role_raw`, `type_final`, `gender_final`, `n_mentions`, `n_docs`.

Next: stance coding (S1–S6) — classifying whether each speaker promotes, questions, or opposes climate action.
