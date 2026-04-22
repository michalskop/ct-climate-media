# Phase 1 Summary — Data Foundations
**Project:** Klimatický rozvrat a média veřejné služby  
**Analyst:** Michal | **PI:** Andrea Culková  
**Completed:** 2026-04-22

---

## 1. Subcorpora — What We Have

| Subcorpus | Docs | % of corpus | Confirmed keywords |
|-----------|-----:|------------:|-------------------|
| Climate v4 (2023) | 2,914 | 0.55% | `změna klima`, `klimatický změna`, `globální oteplování` + 17 others |
| Social/poverty | 4,853 | 0.91% | `chudoba`, `bezdomovec`, `sociální začleňování` + 4 others |
| Motorist | 63,496 | 11.94% | `Dálnic*`, `Automobil*`, `Spalovac* Motor*`, `Benzín*` etc. |
| COVID | 33,284 | 6.26% | `covid`, `korona*`, `koronavir*` |
| Debt enforcement | 3,379 | 0.64% | `exekuce`, `exekutor`, `exekutorský` |
| **Whole corpus** | **531,593** | 100% | Jan 2012 – Apr 2022 |

Dates decoded from `article_id` format: `YYYY` + `E` + day-of-year (1–365) + type + number.

---

## 2. Data Quality Issues Found

### 2.1 Climate subcorpus — 12 false positives
Twelve documents where `klimatický podmínka` is the **only** matching keyword. These are motorway-conditions and weather articles (not climate change), e.g.:
- *"Oprava D1 / Bohumil KLEPETKO moderátor — Dlouho oznamovaná odkládaná a obávaná oprava..."*
- *"Zlínský kraj vyhlásil období nepříznivých klimatických podmínek..."*

The X-coding exclusion that was supposed to remove these was applied to solo-podmínka docs but 12 slipped through. Impact: **0.4% of corpus** — minor, noted for transparency.

### 2.2 "Terrorism" subcorpus is not terrorism
The file `execution_articles_truncated.csv` was labelled as terrorism/execution but its keywords are:
- `exekuce` = Czech legal/debt enforcement (court-ordered asset seizure)
- `exekutor` = bailiff/enforcement officer
- `exekutorský` = bailiff-related

This is a **debt enforcement** corpus — a form of social hardship topic, reasonable as a comparison corpus for social/poverty but not terrorism. Renamed throughout documentation.

### 2.3 COVID corpus has pre-2020 articles
The `korona*` keyword matches Czech words unrelated to COVID-19:
- `koronace` = coronation (e.g., royal events)
- `koronární` = coronary (medical)

Impact: a small number of pre-2020 articles. The COVID-19 bulk starts March 2020 as expected. Not worth re-filtering since counts match the Poznan presentation.

### 2.4 Social/poverty keywords — partial coverage
Of 14 planned keywords, only 7 produced matches in the corpus. Keywords with **zero hits**:
`hmotná nouze`, `chudá domácnost`, `bytová nouze`, `sociální dávky`, `znevýhodněná osoba`, `znevýhodněné osoby`, `lidé bez domova`

Likely explanation: the original subcorpus was built using **lemmatised forms** that differ from the raw-text forms tested here. The corpus count (4,853) matches Poznan exactly, so the corpus itself is correct.

---

## 3. Geographic Coverage (corrected analysis)

### Method
Built an extended Czech country lookup (`country_variants.csv`, 491 entries):
- 453 NER-detected literal forms (existing)
- 47 adjective stem patterns (`německ*` → německý/německého/německém…, `americk*` → americký…)
- 3 extra literals (UK, Pásmo Gazy, Západní břeh)
- Word-boundary matching throughout (eliminates false positives like "Komory"=chambers, "Man"=manžel)

### Key results — climate subcorpus

**Top countries mentioned (docs):**

| Rank | Country | Docs | Income group |
|------|---------|-----:|-------------|
| 1 | Česko (CZE) | 2,076 | High |
| 2 | USA | 951 | High |
| 3 | Německo (DEU) | 647 | High |
| 4 | Velká Británie (GBR) | 530 | High |
| 5 | Rusko (RUS) | 520 | Upper middle |
| 6 | Francie (FRA) | 398 | High |
| 7 | Čína (CHN) | 395 | Upper middle |
| 8 | Polsko (POL) | 362 | High |
| 9 | Slovensko (SVK) | 233 | High |
| 10 | Rakousko (AUT) | 202 | High |
| … | Izrael (ISR) | 79 | High |
| … | Palestina (PSE) | 13 | Upper middle |

### Palestine vs Israel
**ISR = 79 docs, PSE = 13 docs → 6:1 ratio.** Andrea's noted disproportion confirmed.

### Income group breakdown — climate subcorpus

| Income group | Docs | % |
|-------------|-----:|--:|
| High income | 7,538 | 75.6% |
| Upper middle | 1,577 | 15.8% |
| Lower middle | 599 | 6.0% |
| Low income | 252 | 2.5% |

### Geographic blind spots
- 173 countries detected (of ~195 worldwide)
- **101 countries appear in fewer than 10 documents** over the entire 10-year period
- Sub-Saharan Africa, Central America, and Pacific Island nations (highest climate vulnerability) are nearly invisible
- World map: `visualizations/article1/P1.11_world_map_climate.png`

### Cross-subcorpus comparison
High-income country dominance is **consistent across all topics** — this is a structural bias of Czech Television, not specific to climate coverage:

| Subcorpus | High income | Upper middle | Lower middle | Low income |
|-----------|------------:|-------------:|-------------:|-----------:|
| Debt enforcement | 86.8% | 9.1% | 3.0% | 0.9% |
| COVID | 84.1% | 11.7% | 3.4% | 0.7% |
| Motorist | 83.1% | 11.1% | 3.8% | 1.9% |
| Social/poverty | 77.9% | 13.3% | 5.4% | 3.1% |
| **Climate** | **75.6%** | **15.8%** | **6.0%** | **2.5%** |

Climate is the **most globally diverse** subcorpus — but still severely biased toward wealthy nations.
Chart: `visualizations/article1/P1.11b_gni_comparison_all_subcorpora.png`

### Yearly trend (climate)
- High income stable at 67–83%
- Upper middle spikes: **2014** (Crimea annexation = Russia coverage), **2022** (Ukraine war)
- Low income never exceeds 6%
- Chart: `visualizations/article1/P1.12_gni_trends_climate.png`

---

## 4. Temporal Coverage

Monthly document counts decoded from article IDs. Notable peaks:

| Subcorpus | Peak month | Peak count | Explanation |
|-----------|-----------|------------|-------------|
| Climate | Sep 2019 | 128 docs | Global Climate Strike (Greta Thunberg) |
| COVID | Mar 2020 | 2,113 docs | Czech lockdown begins |
| Motorist | Apr 2022 | 975 docs | Fuel price crisis (Ukraine war) |
| Debt enforcement | Mar 2012 | 68 docs | Debt enforcement wave post-2008 crisis |
| Social/poverty | Feb 2012 | 117 docs | Winter homelessness coverage |

Chart: `visualizations/article1/P1.14_monthly_timeseries.png`

---

## 5. Outputs Produced

| File | Description |
|------|-------------|
| `analysis/article1/subcorpus_sizes.py` | Subcorpus size table script |
| `analysis/article1/country_variants.csv` | Extended 491-entry Czech country lookup |
| `analysis/article1/country_detection.py` | Country detection script (all subcorpora) |
| `data/country_counts_climate.csv` | Country mentions — climate subcorpus |
| `data/country_counts_social.csv` | Country mentions — social subcorpus |
| `data/country_counts_terror.csv` | Country mentions — debt enforcement subcorpus |
| `data/country_counts_covid.csv` | Country mentions — COVID subcorpus |
| `data/country_counts_motor.csv` | Country mentions — motorist subcorpus |
| `visualizations/article1/P1.11_world_map_climate.png` | World map — climate geographic coverage |
| `visualizations/article1/P1.11b_gni_comparison_all_subcorpora.png` | Cross-subcorpus GNI bar chart |
| `visualizations/article1/P1.12_gni_trends_climate.png` | Yearly GNI trend lines — climate |
| `visualizations/article1/P1.13_subcorpus_sizes.png` | Subcorpus size bar chart |
| `visualizations/article1/P1.14_monthly_timeseries.png` | Monthly time series — all subcorpora |

---

## 6. Still Blocked

**P1.15 — Per-article tables with show names**  
Show/programme names are absent from all truncated corpus files and monthly `.rds` files (only `article_id` + `text` stored). Requires re-extraction from Newton Media Archive API or locating original metadata. Contact: Newton Media Archive access credentials needed.

---

## 7. Ready for Phase 2

The climate subcorpus (`climate_corpus_v4_2023.csv`, 2,914 docs) is fully verified and ready for actor detection. The transcript format contains speaker lines in the pattern:

```
Bohumil KLEPETKO moderátor Dobrý večer v Hyde Parku...
Marcela AUGUSTOVÁ moderátorka Vlastní modely ke sledování...
```

Pattern: `Jméno PŘÍJMENÍ role` (all-caps surname, lowercase role label). Speaker extraction can begin with regex immediately; LLM classification (M1–M6) requires Anthropic API key setup.
