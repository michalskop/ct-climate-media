# Corpora Inventory
*All corpus files are stored locally only — never committed to git.*
*Local base path: `/home/michal/dev/ct/Climate change TV/BackupClimateChangeData/2.data_transformations/data/`*

---

## Corpus Files

| Corpus | Filename | Size | Docs | Status | Notes |
|--------|----------|------|------|--------|-------|
| **Climate v4 2023** | `climate_sub_corpus/climate_corpus_v4_2023.csv` | ~24 MB | **2,914** | ✅ **PRIMARY** | This is the Poznan version (2,914 matches presentation); semicolon-delimited |
| Climate v4 (older) | `climate_sub_corpus/climate_corpus_v4.csv` | ~32 MB | 3,741 | ⚠️ Older build | 3,741 rows — older version, pre-dates 2023 filtering; do not use as primary |
| Climate v4 (dup) | `climate_corpus_v4.csv` *(root of transformations/)* | ~32 MB | 3,741 | ⚠️ Duplicate | Identical to older v4 above, different path |
| Climate string v2 | `climate_sub_corpus/climate_articles_string_v2.csv` | ~65 MB | 8,888 | 🔄 Earlier version | Semicolon-delimited; broader filtering, pre-bigram refinement |
| **Social/poverty** | `sic_sub_corpus/sic_articles_truncated.csv` | ~40 MB | **4,853** | ✅ **Q1 RESOLVED** | SIC = social issues corpus (matches Poznan 4,853 exactly); NOT terrorism |
| Social v2 | `sic_sub_corpus/sic_articles_v2_truncated.csv` | ~40 MB | 4,853 | ✅ Same count | Second version — check column differences |
| Social labelled | `sic_sub_corpus/sic_corpus_v2_labelled.csv` | ~35 MB | 4,984 | 🔄 Check | Has labels column; tab-delimited; 131 extra rows — investigate |
| **Terrorism** | `sic_sub_corpus/execution_articles_truncated.csv` | ~29 MB | **3,379** | ✅ Identified | Execution/terrorism corpus — separate from social; verify keyword list |
| **Motorist** | `motor_sub_corpus/motor_articles_v2_truncated.csv` | ~293 MB | **63,496** | ✅ Verified | Keywords: Dálnic\*, Silnic\*, Automobil\*, Spalovac\* Motor\*, Benzín\*, etc. |
| **COVID** | `covid_sub_corpus/covid_articles_v2_truncated.csv` | ~153 MB | **33,284** | ✅ **Q2 RESOLVED** | Exists as separate file; 33,284 docs |
| Terror dir | `terror_sub_corpus/` | — | ? | 🔄 Check | Separate directory — check if different from execution corpus |

## NER / Named Entity Files

| File | Location | Notes |
|------|----------|-------|
| Named entity lists | Unknown — check with Irene Elmerot | Q3: format CSV/JSON/plain text? Per subcorpus or whole corpus? |
| UDPipe lemma IDs | `data/Udpipe_lemma_id/` | UDPipe processing output |

## Analysis Data Files

| File | Location | Size | Notes |
|------|----------|------|-------|
| Country counts per doc | `4.data_analysis/world_data/Country_counts_per_doc.csv` | ~9 MB | Geographic analysis — **has known errors**, fix in P1.7–P1.9 |
| Top 5000 lemmata | `3.data_exploration/top_5000_lemmata.csv` | ~2 MB | Word frequency list for whole corpus |
| Other terms | `3.data_exploration/other_terms.csv` | ~8 MB | Extended term frequencies |
| NMF 20 topic data | `climate_change_web/data/nmf_20.json` | — | Topic model output for interactive viz |
| NMF 45/50 topic data | `climate_change_web/data/nmf_45.json`, `nmf_50.json` | ~600 KB each | |
| LDA 50 topic data | `climate_change_web/data/lda_50.json` | ~530 KB | |
| CO2 emissions | `4.data_analysis/world_data/cumulative-co-emissions.csv` | ~790 KB | External reference data |

## Keyword Lists (subcorpus definitions)

### Climate v4 (bi/trigrams)
`změna klima`, `klima se měnit`, `měnící se klima`, `globální oteplování`, `oteplování planeta`,
`klimatický změna`, `klimatický podmínka*` *(excluded — X-coded)*, `klimatický dopad`, `klimatický důsledek`,
`klimatický model`, `klimatický opatření`, `klimatický krize`, `klimatický kolaps`, `klimatický katastrofa`,
`klimaticky neutrální`, `klimatický neutralita`, `klimatický plán`, `klimatický rozvrat`, `klimatický zákon`,
`klimatický závazek`, `klimatický žaloba`, `klimatický vzdělávání`

### Social / Poverty
`chudoba*`, `hmotná nouze`, `chudá domácnost`, `bezdomovectví`, `bezdomovec`, `lidé bez domova`,
`člověk bez domova`, `člověk bez přístřeší`, `sociální vyloučení`, `sociální začleňování`,
`znevýhodněná osoba`, `znevýhodněné osoby`, `bytová nouze`, `sociální dávky`

### Motorist
`Dálnic*`, `Dálničn*`, `Silnic*`, `Silničn*`, `Aut*`, `Automobil*`, `Motorist*`,
`Elektrick* Motor*`, `Spalovac* Motor*`, `Benzín*`, `Naft*`, `Dopravní nehod*`

---

*Last updated: 2026-04-22. Run `data_check.py` to verify current row counts.*
