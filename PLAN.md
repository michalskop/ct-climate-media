# Climate Media Project — Master Analysis Plan
**"Klimatický rozvrat a média veřejné služby"**
Andrea Culková (PI) | Michal (analyst/developer) | March 2026

> Legend: ✅ DONE · 🔄 PARTIAL (code/data exists, needs work) · ⬜ TODO · 🆕 NEW (out of original scope)

---

## Open Questions (resolve before starting affected tasks)

| ID | Question | Affects |
|----|----------|---------|
| ~~Q1~~ | ~~What exactly is in `sic_articles_truncated.csv`?~~ **RESOLVED:** SIC = social issues corpus (4,853 docs). Terrorism = `execution_articles_truncated.csv` (3,379 docs). | ✅ |
| ~~Q2~~ | ~~Is the COVID subcorpus a separate file locally?~~ **RESOLVED:** Yes — `covid_articles_v2_truncated.csv` (33,284 docs). | ✅ |
| Q3 | Named entity/NER lists format (CSV/JSON/plain text)? Per subcorpus or whole corpus? Irene Elmerot did this work — likely keyword-separated. | P2.1 |
| Q4 | Does Andrea still have Sketch Engine access? | P3.16 |
| Q5 | FAMU public page — existing infrastructure or build from scratch? Contact: Tomáš Šín +420 234 244 308 | P5.3, P5.4 |

---

## Critical Path

```
P0 → everything else. Do not start any phase until P0 is complete.

Article 1:  P0 → P1A → P1B → P1C → write
Article 2:  P0 → P1A → P2A → P2B → write
Article 3:  P0 → P1A → P2A → P3A → P3B → P3C → P3D → P4 → write
FAMU page:  P1–P4 → P5
Brussels:   P2A → P6 (optional)
```

---

## PHASE 0 — Infrastructure & Audit *(do this first)*

Purpose: Organize everything before any new analysis. No research output, but makes everything else reproducible and hand-off-ready.

| ID | Task | Status | Output |
|----|------|--------|--------|
| P0.1 | Set up GitHub repository — folders: `/data`, `/corpora`, `/analysis/article1`, `/analysis/article2`, `/analysis/article3`, `/visualizations`, `/utils`; commit all existing code | ✅ DONE | https://github.com/michalskop/ct-climate-media |
| P0.2 | Document all corpus files — filenames, sizes, versions, creation dates, cleaning steps applied | ✅ DONE | `CORPORA_INVENTORY.md` |
| P0.3 | Audit all existing R and Python scripts — annotate what each does, flag broken/outdated; convert R to Python where feasible | ✅ DONE | 29 files migrated to repo (see below) |
| P0.4 | Verify all corpora load in Python — test `climate_corpus_v4.csv`, `sic_articles_truncated.csv`, and all others | ✅ DONE | `data_check.py` — all 10 files load OK |
| P0.5 | Identify what SIC subcorpus actually contains — open file, check keywords → resolve Q1 | ✅ DONE | **SIC = social issues corpus** (4,853 rows); terrorism = `execution_articles_truncated.csv` (3,379 rows) |

**Code migrated to repo:**
- `utils/data_extraction/` — 8 R scripts (Newton Media Archive API)
- `utils/data_transformation/` — 7 R/Rmd + 1 Python (regex, UDPipe, subcorpus building)
- `utils/czech_stemmer.py` — Czech stemmer utility
- `analysis/article1/frequency_analysis/` — 5 R/Rmd keyword frequency scripts
- `analysis/article3/topic_modeling/` — BERTopic notebooks (cloud + prototype)
- `analysis/article3/sentiment_analysis/` — Kaggle sentiment workflow
- `visualizations/climate_change_web/` — LDA/NMF interactive HTML

**Open questions resolved:** Q1 ✅ (SIC=social), Q2 ✅ (COVID=33,284 docs as separate file)
**Still open:** Q3 (NER format), Q4 (Sketch Engine), Q5 (FAMU page infrastructure)

---

## PHASE 1 — Data Foundations *(feeds Articles 1 & 3 + FAMU page)*

Purpose: Clean, verified subcorpora + corrected geographic analysis. Article 1 (Triple Silences) is fully completable here.

### 1A — Subcorpora Audit & Completion

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P1.1 | Review climate subcorpus v4 (2,914 docs) — verify bi/trigram keyword list matches Poznan presentation; confirm `klimatický podmínky` exclusion (X-coded docs) was applied | 🔄 PARTIAL | |
| P1.2 | Confirm social/poverty subcorpus (4,853 docs) — verify keywords (`chudoba*`, `bezdomovectví`, `sociální vyloučení`…); check consistency with Irene Elmerot's results | 🔄 PARTIAL | |
| P1.3 | Confirm motorist subcorpus (63,496 docs) — keywords verified in Poznan (`Dálnic*`, `Automobil*`, `Spalovac* Motor*`…) | ✅ DONE | Verify Python load |
| P1.4 | Confirm COVID subcorpus — load from local drive or extract from full corpus using keyword matching | ⬜ TODO | Resolves Q2 |
| P1.5 | Confirm terrorism/SIC subcorpus — open `sic_articles_truncated.csv`, check keyword list, verify matches NMF Topic 16 | ⬜ TODO | Resolves Q1 |
| P1.6 | Build subcorpus size comparison table — counts + % of total corpus for all 5 subcorpora | 🔄 PARTIAL | R chart exists; needs Python reproducible script |

### 1B — Geographic / Country Analysis *(fix errors from Poznan)*

Andrea flagged errors caused by variant Czech country name forms (`Německo` vs `německý`, `USA` vs `Spojené státy` vs `americký`).

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P1.7 | Build country name lookup table — all Czech variant forms per country (official, adjective, demonym, abbreviations, historical); use LLM API | ✅ DONE | `analysis/article1/country_variants.csv` — 491 rows (453 literals + 47 adj stems); word-boundary matching; false positives removed (COM "Komory"=chambers, IMN "Man", MLI "Mali") |
| P1.8 | Re-run country detection on whole corpus with corrected table — map to canonical names + World Bank GNI 2022 categories | ⬜ TODO | Script ready: `analysis/article1/country_detection.py --corpus climate/social/motor/covid/terror`; ~33s per 3k docs |
| P1.9 | Re-run country detection on climate subcorpus v4 — same process | ✅ DONE | `data/country_counts_climate.csv` — 9,973 rows; CZE=2076, USA=951, DEU=647, GBR=530, RUS=520; High income=7538, UpperMid=1577, LowerMid=599, Low=252 |
| P1.10 | Special check: Palestine vs Israel disproportion — verify counts, flag explicitly | ✅ DONE | ISR=79 docs vs PSE=13 docs in climate subcorpus — 6:1 ratio; Andrea's noted finding confirmed |
| P1.11 | Produce geographic blind-spots map — global map, countries with <100 mentions over 10 years; separate for whole corpus + climate subcorpus | ✅ DONE | `visualizations/article1/P1.11_world_map_climate.png` — 173 countries detected; 101 appear in <10 docs; Global South nearly invisible (SSA, LatAm, Pacific) |
| P1.12 | Yearly GNI category trend charts — line charts by income category (whole corpus + climate subcorpus) | ✅ DONE | `visualizations/article1/P1.12_gni_trends_climate.png` — High income 67–83%; spike in Upper middle 2014+2022 (Russia/Ukraine); Low income never exceeds 6% |

### 1C — Subcorpus Frequency & Time Trend Visualizations *(core Article 1 charts)*

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P1.13 | Subcorpus size bar chart — absolute counts, all 5 subcorpora vs total corpus | 🔄 PARTIAL | R chart exists; redo in Python |
| P1.14 | Time-series chart — % docs per month with climate/social/motor/terror/COVID terms, 2012–2022 | ✅ DONE | Shown in Poznan; reproduce in Python with corrected data |
| P1.15 | Per-article frequency tables — CSV with doc-id, date, show name, term count per subcorpus | ⬜ TODO | Input for Phase 2 actor analysis |

---

## PHASE 2 — Actor Detection & Classification *(core of Article 2)*

Purpose: Identify and classify all speakers in the climate subcorpus into M1–M6 types. Requires LLM API calls.

**Speaker types:**
- M1 = Moderátor (anchor/host)
- M2 = Občan (ordinary citizen)
- M3 = Vědec (scientist)
- M4 = Popularizátor / Pseudovědec
- M5 = Stakeholder (NGO, business, activist)
- M6 = Politik (politician/official)

### 2A — Speaker Detection

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P2.1 | Review existing NER results — load entity/proper noun lists; document format, coverage, quality for climate subcorpus | 🔄 PARTIAL | Irene Elmerot did NER on whole corpus; resolves Q3 |
| P2.2 | Re-run/validate speaker detection on climate subcorpus v4 — extract `Jméno PŘÍJMENÍ` patterns (ALL CAPS surname format used in transcripts); regex + NER | 🔄 PARTIAL | |
| P2.3 | For each speaker, extract 5 fields: doc-id, full name, profession/org (from transcript), speaker type M1–M6, gender | ⬜ TODO | |
| P2.4 | Classify speakers into M1–M6 via LLM API — send name + profession/org description; batch calls to minimize cost (~2,914 docs) | ⬜ TODO | Prompt must include full category definitions |
| P2.5 | Classify gender via LLM API — Czech names usually obvious; flag ambiguous cases for manual review | ⬜ TODO | |
| P2.6 | Validate ~100 speaker classifications manually — calculate agreement; adjust prompt if <85% | ⬜ TODO | Quality gate |
| P2.7 | Produce master speaker table — `speakers_climate.csv`; deduplicated by person name | ⬜ TODO | Key input for all Article 2 visualizations and Phase 3 |

### 2B — Actor Salience & Marginalization Analysis

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P2.8 | Calculate speaker salience scores — mentions per speaker, per type (M1–M6), per year | ⬜ TODO | Output: `salience_by_speaker.csv`, `salience_by_type_year.csv` |
| P2.9 | Identify marginalized actors — under-represented types (citizens M2, scientists M3 vs politicians M6?) | ⬜ TODO | Key Article 2 finding: is ČT coverage elitist? |
| P2.10 | Visualize speaker type distribution — stacked bar + yearly trend | ⬜ TODO | 2 charts |
| P2.11 | Visualize gender breakdown by speaker type — M/F ratio within each M1–M6 | ⬜ TODO | 1 chart |
| P2.12 | Visualize top 20 most mentioned speakers — horizontal bar chart | ⬜ TODO | 1 chart |

---

## PHASE 3 — Stance, Topic Modeling & Transformative Journalism *(core of Article 3)*

Purpose: Add stance coding (S1–S6) to speakers, run topic modeling on climate subcorpus, analyze against TJ criteria.

**Stance categories:**
- S1 = Denier · S2 = Manipulator · S3 = Delayer · S4 = Techno-optimist · S5 = Market fundamentalist · S6 = Informer

### 3A — Stance Coding (S1–S6)

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P3.1 | Define stance classification prompt — detailed LLM prompt for S1–S6 with full category definitions; test on 20 manually coded examples | ⬜ TODO | Include Czech-language examples |
| P3.2 | Run stance classification on all speakers — send: doc-id + speaker name + profession + ±200 words context to LLM | ⬜ TODO | Output: 6th column added to master speaker table; same person may have different stances in different docs |
| P3.3 | Validate 150 cases (25 per category) manually — adjust prompt if precision <80% | ⬜ TODO | Quality gate before publication use |
| P3.4 | Analyze stance distribution — frequency table S1–S6 × speaker type M1–M6 | ⬜ TODO | Key finding: proportion of deniers vs informers |
| P3.5 | Polarization analysis — for each doc, flag if contradictory stances co-occur (S1 Denier + S6 Informer = 'false balance') | ⬜ TODO | Key Article 3 finding: false equivalence? |
| P3.6 | Visualize stance distribution — stacked bar + M-type × S-type heatmap | ⬜ TODO | 2 charts |

### 3B — Topic Modeling on Climate Subcorpus

Note: whole-corpus NMF 20 found **no climate topic** — the key finding. Climate subcorpus modeling reveals *what* climate coverage is actually about.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P3.7 | Prepare climate subcorpus for topic modeling — Czech lemmatization (MorfFlex), doc-term matrix, stopwords filter; reuse existing 2,910-word library | 🔄 PARTIAL | |
| P3.8 | Run NMF (20, 25, 30, 35, 40, 50 topics) on climate subcorpus — compute coherence scores | ⬜ TODO | Reference: climate-topics.netlify.app approach |
| P3.9 | Run LDA (same range) — compute coherence at λ=0.6; compare with NMF | ⬜ TODO | |
| P3.10 | Select best model — validate manually; label each topic; priority labels: nuclear/renewables, drought/floods, health, EU Green Deal | ⬜ TODO | |
| P3.11 | Classify topics as mitigation vs adaptation | ⬜ TODO | Key finding: is ČT more focused on adaptation (floods) than mitigation (decarbonization)? |
| P3.12 | Link topics to speakers — join topic output (doc-id → topic) with speaker table (doc-id → speaker, type, stance) | ⬜ TODO | Crucial cross-phase linkage |
| P3.13 | Visualize topic model — interactive pyLDAvis / Flourish; topic × speaker-type heatmap; topic × stance heatmap | ⬜ TODO | 3 visualizations; adapt climate-topics.netlify.app |

### 3C — Urgency, Mitigation, Planetary Limits (Frequency Analysis)

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P3.14 | Extend frequency analysis code — add keyword groups: urgency terms (`naléhavost`, `krize`, `hrozba`, `kolaps`), planetary limits, fossil fuel terms, net-zero/carbon neutral terms | 🔄 PARTIAL | Existing code needs extension |
| P3.15 | Run extended frequency analysis on climate subcorpus — yearly counts per keyword group | ⬜ TODO | Output: `frequency_urgency.csv`, `frequency_mitigation.csv` (absolute + normalized) |
| P3.16 | Collocate analysis — co-occurrences with `klimatická změna`, `globální oteplování`, `riziko`, `krize` | ⬜ TODO | Use Python NLTK/spaCy or Sketch Engine (resolves Q4) |
| P3.17 | Visualize urgency/mitigation trends — line chart, yearly urgency term frequency | ⬜ TODO | 1 chart |

### 3D — Transformative Journalism Assessment

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P3.18 | Operationalize TJ criteria as measurable indicators — map 3 TJ principles to outputs from Phases 2 & 3 (e.g., De-polarization = % false balance docs; Urgency = urgency term frequency; Just Transformation = proportion of M2/M3 + social justice framing) | ⬜ TODO | |
| P3.19 | Produce TJ assessment summary table — per criterion: finding + evidence + meets/partially meets/does not meet | ⬜ TODO | Drives Article 3 conclusions |

---

## PHASE 4 — Case Studies *(Article 3, qualitative)*

Purpose: Three in-depth discourse analyses using doc-ids from Phase 3 topic model.

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P4.1 | Case Study 1: Nuclear energy & renewables (OZE) — identify docs via topic model/keywords; analyze framing, speaker types, stances | ⬜ TODO | Is nuclear presented as climate solution? Are renewables framed negatively? |
| P4.2 | Case Study 2: Drought and floods — analyze whether extreme weather is linked to climate change or treated as isolated events | ⬜ TODO | Key TJ criterion: restorative narrative — adaptation + mitigation mentioned together? |
| P4.3 | Case Study 3: Health impacts — keyword `zdraví` + climate context; expected to be nearly absent — the absence is the finding | ⬜ TODO | |
| P4.4 | For each case study: discourse analysis narrative with 3–5 illustrative excerpts; apply TJ framework | ⬜ TODO | Output: 3–6 pages each for Article 3 |

---

## PHASE 5 — Visual Unification & FAMU Public Page

Purpose: Unify all chart aesthetics; build public-facing page at FAMU.

**Visual style** (from Poznan presentation): dark red `#8B1A1A`, cream background, bold sans-serif.

### 5A — Visual Style Guide

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P5.1 | Define unified style — color palette, typography, matplotlib/seaborn template, Flourish theme | ⬜ TODO | Output: `style_guide.md` + Python template file |
| P5.2 | Reproduce all existing Poznan charts in new unified Python style | 🔄 PARTIAL | Charts exist as images; need reproducible Python code |

### 5B — Visualization Inventory

| ID | Chart | Status | Article |
|----|-------|--------|---------|
| V1 | Subcorpus size comparison bar chart | 🔄 PARTIAL | Art. 1 / FAMU |
| V2 | Time series: % docs/month by topic (climate/social/motor/terror/COVID) | ✅ DONE | Art. 1 / FAMU |
| V3 | World map: country blind spots — whole corpus | ⬜ TODO | Art. 1 / FAMU |
| V4 | World map: country blind spots — climate subcorpus | ⬜ TODO | Art. 1 / FAMU |
| V5 | GNI yearly trend — whole corpus | ✅ DONE | Art. 1 / FAMU |
| V6 | GNI yearly trend — climate subcorpus | ✅ DONE | Art. 1 / FAMU |
| V7 | GNI total mentions bar — whole corpus | ✅ DONE | Art. 1 / FAMU |
| V8 | GNI total mentions bar — climate subcorpus (normalized) | ✅ DONE | Art. 1 / FAMU |
| V9 | Speaker type distribution (M1–M6) overall | ⬜ TODO | Art. 2 / FAMU |
| V10 | Speaker type yearly evolution | ⬜ TODO | Art. 2 / FAMU |
| V11 | Gender breakdown by speaker type | ⬜ TODO | Art. 2 / FAMU |
| V12 | Top 20 most mentioned speakers | ⬜ TODO | Art. 2 / FAMU |
| V13 | Stance distribution (S1–S6) overall | ⬜ TODO | Art. 3 / FAMU |
| V14 | M-type × S-type heatmap | ⬜ TODO | Art. 3 / FAMU |
| V15 | Interactive topic model (pyLDAvis / Flourish) | ⬜ TODO | Art. 3 / FAMU |
| V16 | Topic × speaker-type heatmap | ⬜ TODO | Art. 3 / FAMU |
| V17 | Urgency/mitigation keyword frequency over time | ⬜ TODO | Art. 3 / FAMU |
| V18 | Mitigation vs adaptation topic proportions | ⬜ TODO | Art. 3 / FAMU |

### 5C — FAMU Public Page

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P5.3 | Design page structure — sections, visualization order, narrative text in Czech | ⬜ TODO | Story arc: how much does ČT cover climate? Who speaks? What stances? What silences? |
| P5.4 | Build/configure FAMU subpage — embed Flourish charts, Czech text, mobile-friendly layout | ⬜ TODO | Coordinate with Tomáš Šín +420 234 244 308; resolves Q5 |
| P5.5 | Write Czech explanatory captions for each visualization (2–3 sentences, accessible to general public) | ⬜ TODO | |

---

## PHASE 6 — Optional: Brussels / EU Climate Policy *(potential 4th article)*

| ID | Task | Status | Notes |
|----|------|--------|-------|
| P6.1 | Build Brussels/EU Green Policy subcorpus — extract docs with terms: Green Deal, Fit for 55, ETS, EU taxonomy, combustion engine ban, `Brusel`, `Zelená dohoda`, etc. | 🆕 NEW | |
| P6.2 | Sentiment analysis on EU climate policy subcorpus — positive/neutral/negative toward EU climate policy; LLM API | 🆕 NEW | Key question: is Brussels/Green Deal presented as friend or enemy? |
| P6.3 | Temporal analysis — how does sentiment toward EU climate policy change over time? Does it shift with political cycles (e.g., after ODS/SPOLU election victory)? | 🆕 NEW | |
| P6.4 | Actor analysis — who speaks in EU climate policy stories? Cross-reference with master speaker table from P2.7 | 🆕 NEW | |

---

## Summary Counts

| Phase | ✅ Done | 🔄 Partial | ⬜ TODO | 🆕 New |
|-------|---------|-----------|--------|--------|
| 0 | 5 | 0 | 0 | 0 |
| 1A | 1 | 2 | 2 | 0 |
| 1B | 1 | 3 | 2 | 0 |
| 1C | 1 | 1 | 1 | 0 |
| 2A | 0 | 2 | 5 | 0 |
| 2B | 0 | 0 | 5 | 0 |
| 3A | 0 | 0 | 6 | 0 |
| 3B | 0 | 1 | 6 | 0 |
| 3C | 0 | 1 | 3 | 0 |
| 3D | 0 | 0 | 2 | 0 |
| 4 | 0 | 0 | 4 | 0 |
| 5A-C | 0 | 1 | 7 | 0 |
| Viz | 5 | 1 | 12 | 0 |
| 6 | 0 | 0 | 0 | 4 |
| **Total** | **8** | **12** | **60** | **4** |

---

*Source: `Climate Media Task Plan.docx` (Andrea Culková, March 2026) + Poznan/CADAAD 2024 presentation.*
*Update task statuses as work progresses.*
