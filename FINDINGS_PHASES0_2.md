# Research Findings — Phases 0–2
**Project:** Klimatický rozvrat a média veřejné služby (Climate breakdown and public service media)  
**PI:** Andrea Culková | **Analyst:** Michal  
**Corpus:** Czech Television (ČT) news transcripts, Jan 2012 – Apr 2022, 531,593 documents  
**Last updated:** 2026-04-23

---

## Corpus Overview

| Subcorpus | Docs | % of whole | Period |
|-----------|-----:|----------:|--------|
| Climate change | 2,914 | 0.55% | 2012–2022 |
| Social/poverty | 4,853 | 0.91% | 2012–2022 |
| Debt enforcement | 3,379 | 0.64% | 2012–2022 |
| COVID-19 | 33,284 | 6.26% | 2012–2022 |
| Motorist/transport | 63,496 | 11.94% | 2012–2022 |
| **Whole corpus** | **531,593** | 100% | 2012–2022 |

---

## Finding 1 — Geographic Coverage Is Heavily Skewed Toward Wealthy Nations

### Climate subcorpus — top countries mentioned

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
| … | Izrael (ISR) | 79 | High |
| … | Palestina (PSE) | 13 | Upper middle |

### Income group breakdown — climate subcorpus

| Income group | Docs | % |
|-------------|-----:|--:|
| High income | 7,538 | 75.6% |
| Upper middle | 1,577 | 15.8% |
| Lower middle | 599 | 6.0% |
| Low income | 252 | 2.5% |

**101 countries appear in fewer than 10 documents** over the entire 10-year period. Sub-Saharan Africa, Central America, and Pacific Island nations — among the most climate-vulnerable regions on earth — are nearly invisible in ČT climate coverage.

### Cross-subcorpus comparison — this is a structural bias, not climate-specific

| Subcorpus | High income | Upper middle | Lower middle | Low income |
|-----------|------------:|-------------:|-------------:|-----------:|
| Debt enforcement | 86.8% | 9.1% | 3.0% | 0.9% |
| COVID | 84.1% | 11.7% | 3.4% | 0.7% |
| Motorist | 83.1% | 11.1% | 3.8% | 1.9% |
| Social/poverty | 77.9% | 13.3% | 5.4% | 3.1% |
| **Climate** | **75.6%** | **15.8%** | **6.0%** | **2.5%** |

The climate subcorpus is actually the **most globally diverse** of all five — but still severely biased toward wealthy nations. This is a structural property of Czech Television, not specific to climate reporting.

### Israel–Palestine disparity
ISR = 79 documents, PSE = 13 documents → **6:1 ratio** in favour of Israeli coverage over the 10-year period.

### Yearly trend (climate, high-income share)
- Stable at 67–83% throughout the decade
- Upper-middle spikes: **2014** (Crimea annexation → Russia coverage), **2022** (Ukraine war)
- Low-income coverage never exceeds 6% in any year

---

## Finding 2 — Temporal Patterns Reflect Global Events

| Subcorpus | Peak month | Peak count | Driver |
|-----------|-----------|------------|--------|
| Climate | Sep 2019 | 128 docs | Global Climate Strike (Greta Thunberg) |
| COVID | Mar 2020 | 2,113 docs | Czech lockdown |
| Motorist | Apr 2022 | 975 docs | Fuel price crisis (Ukraine war) |
| Debt enforcement | Mar 2012 | 68 docs | Post-2008 debt enforcement wave |
| Social/poverty | Feb 2012 | 117 docs | Winter homelessness |

Climate coverage volume roughly doubled after the 2019 strike movement and remained elevated through COP26 (2021).

---

## Finding 3 — Speaker Type Distribution in Climate Coverage

### Who speaks about climate on Czech Television?

| Type | Label | Unique speakers | Mentions | % of mentions |
|------|-------|----------------:|---------:|--------------:|
| M1 | Journalist/anchor | 737 | 31,034 | 54.8% |
| M6 | Politician/official | 1,480 | 12,797 | 22.6% |
| M5 | Stakeholder (NGO/business) | 1,140 | 6,240 | 11.0% |
| M3 | Scientist/academic | 630 | 4,871 | 8.6% |
| M2 | Ordinary citizen | 609 | 1,143 | 2.0% |
| M4 | Pseudoscientist | 5 | 87 | 0.2% |

**M1 dominance** reflects the transcript structure — every interview has a journalist asking questions.

**M4 near-absent:** only 5 unique pseudoscientist/climate-denier speakers across 10 years, 87 total mentions. Czech Television did not platform climate denial or alternative science voices at any meaningful scale. This is a notable finding for the debate about public service media responsibility.

**Scientists (M3) are outnumbered by politicians (M6) 2.6:1** in unique speakers and 2.6:1 in mentions. Climate is primarily covered as a political issue, not a scientific one.

**Citizens (M2) are the least heard voice** outside of journalists — only 2.0% of mentions despite being the population most affected.

### Yearly speaker trend
- 2019 is the largest year across all types (Climate Strikes)
- 2021 second-largest (COP26/Glasgow)
- M6 (politicians) surge most strongly around both events

---

## Finding 4 — Systemic Gender Gap, Especially in Expert Roles

### Female representation by speaker type

| Type | % Female mentions | Context |
|------|------------------:|---------|
| M1 Journalist | **39.4%** | Closest to parity — ČT internal hiring practices |
| M2 Citizen | 30.3% | Reasonable balance in street interviews |
| M6 Politician | 12.6% | Mirrors Czech political gender gap |
| M3 Scientist | **12.0%** | Low — reflects academic pipeline + who gets invited |
| M5 Stakeholder | **10.7%** | Lowest — NGO/business leadership heavily male |

**Overall:** 27.6% female across all classified speaker mentions (15,478 F / 40,709 M).

The expert voice gap is particularly striking: when ČT brings in scientists (M3) or institutional experts (M5) to explain climate change, only about 1 in 8 is a woman. This is lower than the actual share of women in Czech academia (~35–40%), suggesting a selection bias in who journalists call.

---

## Data Quality Notes

1. **12 climate false positives** — documents where `klimatický podmínka` was the only matching keyword, describing motorway conditions or local weather, not climate change. Impact: 0.4% of corpus. Noted for transparency.

2. **"Terrorism" corpus is debt enforcement** — the `execution_articles_truncated.csv` file uses keywords `exekuce` / `exekutor` (Czech bailiff proceedings), not terrorism. Renamed in all documentation.

3. **COVID corpus has pre-2020 articles** — `korona*` matches "koronace" (coronation) and "koronární" (coronary). A handful of pre-2020 false positives; the COVID-19 bulk starts correctly in March 2020.

4. **Social/poverty keywords** — only 7 of 14 planned keywords produced matches. The subcorpus appears to have been built from lemmatised forms. Total count (4,853) matches the Poznan presentation exactly, so the corpus itself is correct.

---

## Outputs Reference

| File | Contents |
|------|----------|
| `data/country_counts_climate.csv` | Country mentions — climate subcorpus |
| `data/speakers_final.csv` | 4,960 unique (name, role) pairs with type + gender |
| `data/speakers_all.csv` | 56,613 individual speaker mentions |
| `data/validation_sample_p26.csv` | 80-row manual validation sample (fill `correct` column) |
| `visualizations/article1/P1.11_world_map_climate.png` | World map — climate geographic coverage |
| `visualizations/article1/P1.11b_gni_comparison_all_subcorpora.png` | Cross-subcorpus GNI bar chart |
| `visualizations/article1/P1.12_gni_trends_climate.png` | Yearly GNI trend — climate |
| `visualizations/article1/P1.13_subcorpus_sizes.png` | Subcorpus size comparison |
| `visualizations/article1/P1.14_monthly_timeseries.png` | Monthly document counts |
| `visualizations/article2/P2.1_speaker_types_by_year.png` | Speaker types by year (stacked bar) |
| `visualizations/article2/P2.2_gender_by_type.png` | Female % by speaker type |
