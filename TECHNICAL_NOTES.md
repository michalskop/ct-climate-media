# Technical Notes — Lessons Learned for Future Similar Analyses
**Project:** Klimatický rozvrat a média veřejné služby  
**Last updated:** 2026-04-23

These notes record non-obvious technical decisions, traps, and solutions discovered during Phases 0–2.  
Future analysts starting a similar corpus study should read this before writing any code.

---

## 1. Corpus Format

### Files
- All corpus CSV files use **semicolon delimiters** (`sep=";"`) — not commas.
- Load with: `pd.read_csv(path, sep=";", low_memory=False)`
- The `low_memory=False` is important: mixed-type columns (especially `article_id`) cause dtype inference warnings that silently truncate data.

### article_id encoding
```
Format: YYYY E DDD T NNN
  YYYY = year (2012–2022)
  E    = literal 'E'
  DDD  = day of year (001–365)  ← NOT month+day
  T    = document type code
  NNN  = sequence number
```
**Decode day-of-year correctly:**
```python
import datetime
year = int(str(article_id)[:4])
doy  = int(str(article_id)[5:8])
date = datetime.datetime.strptime(f"{year} {doy}", "%Y %j")
```
`pd.Timestamp(f"{year}-{doy:03d}", format="%Y-%j")` returns NaT — do not use it.

### File locations
Base path: `/home/michal/dev/ct/Climate change TV/BackupClimateChangeData/2.data_transformations/data/`  
World Bank data: `…/4.data_analysis/world_data/` (not inside `2.data_transformations`)  
See `CORPORA_INVENTORY.md` for the full file listing.

---

## 2. Country Detection

### Why naive approaches fail
- Simple string matching on country names produces massive false positives in Czech:
  - "Komory" = Comoros (COM) but also Czech for "chambers/attic" → 1,194 false matches
  - "Man" = Isle of Man but also Czech for "manžel" (husband)
  - "Mali" = Mali but appears in many Czech words
- **Always use word-boundary regex** (`\b`) or tokenize first.

### Three-pass fast detection (the working solution)
Running 491 individual regex patterns is too slow (~120s timeout for 3k docs). Use three combined passes:

```python
# Pass 1: tokenize text, look up each word in a dict (handles single-word literals)
# Pass 2: one combined alternation regex for multi-word phrases ("Velká Británie", etc.)
# Pass 3: one combined stem regex for Czech adjective forms ("německ*" → německý/německém/…)
```
This runs in ~33 seconds for 3,000 documents.

### Czech adjective forms
Country adjectives in Czech inflect heavily. Build stem patterns, not exhaustive lists:
- "německý/německého/německém/německým/němečtí" → stem `německ`
- "americký/amerického/americkém…" → stem `americk`
- Watch for Cyrillic characters in stems copied from data (e.g. "běloruск" has Cyrillic "с" and "к") — replace before compiling regex.

### World Bank income classification
`Entities_coded_WB.csv` is **semicolon-delimited** (not comma). Load with `sep=";"`.  
NaN codes appear for some rows (USA, Bonaire) — fix manually before building the lookup.

---

## 3. Speaker Extraction (Czech TV Transcripts)

### Transcript format
Czech Television transcripts follow a consistent format:
```
Firstname SURNAME role Text of what they said...
```
- Surname is ALL CAPS
- Role label follows immediately after surname (lowercase)
- This structure is reliable enough for regex extraction

### Working regex
```python
U = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]'
L = r'[a-záčďéěíňóřšťúůýž]'
W = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]'

SPEAKER_RE = re.compile(
    rf'({U}{L}{{1,11}})\s+({U}{{2,20}}(?:\s{U}{{2,15}})?)\s+({L}{W}*(?:\s{L}{W}*){{0,4}})',
    re.UNICODE,
)
```
Filter: `if len(role) < 4: continue` removes noise fragments.

### False positive rate
About 4–7% of regex matches are not genuine speaker introductions — the LLM's SKIP label handles these. Do not try to eliminate all false positives with the regex alone.

---

## 4. M1–M6 Speaker Classification

### Two-stage approach is cost-effective
1. **Rule-based first** (keyword lookup) — achieves ~95% resolution at zero cost
2. **LLM only for unresolved** — reduces API cost by ~20× vs. classifying everything with LLM

With 56,613 mentions and a 95% rule resolution rate, LLM cost was **~$0.20** using Claude Haiku.

### Modifier stripping is essential
Many roles are compound: "americký prezident", "generální ředitel", "obchodní ředitel".  
Strip adjective modifiers before looking up the noun:
```python
MODIFIERS = {'americký', 'generální', 'obchodní', 'výzkumný', 'tiskový', ...}
clean = [w for w in words if w not in MODIFIERS]
first = clean[0]  # look up only this
```
Without modifier stripping, resolution rate drops from ~95% to ~80%.

### Key modifier omissions that cause failures
These are NOT obvious — add them to MODIFIERS:
`obchodní`, `výrobní`, `výzkumný/á`, `tiskový/á`, `mořský/á`, `rostlinný/á`, `energetický/á`, `republikánský/á`, `projektový/á`, `finanční`, `správní`, `kulturní`, `klimatický/á`

### LLM prompt design
- Return **only** a JSON array — no prose
- Include `SKIP` as a valid type for false positive extractions
- Batch size 30 is optimal: large enough to amortize prompt overhead, small enough to stay within `max_tokens=512`
- Add 0.5s sleep between batches to avoid rate limits

### LLM JSON parsing
Strip markdown fences before parsing:
```python
if text.startswith("```"):
    text = "\n".join(text.split("\n")[1:-1])
```

---

## 5. Gender Classification (Czech Names)

### The suffix rule
```python
def infer_gender(firstname, surname):
    if surname.upper().endswith('Á'):   # -ová, -ská, -ná, -lá → female
        return 'F'
    if surname.upper().endswith('Ů'):   # Janů, Petrů → both genders
        return '?'
    if firstname.endswith('a') or firstname.endswith('e'):
        return 'F?'   # probable female, but needs correction pass
    return 'M'
```

### F? correction is necessary
The `firstname.endswith('e')` rule catches many **male foreign names**: Joe, Charlie, George, Steve, Bruce, Claude, Luca, Dante, Jukka, Ota, Stephane, Christophe.  
Keep a `MALE_FIRST` set and apply a correction pass after extraction — do not try to bake it into the regex.

### -ů surnames
Only 5 cases in climate corpus. Resolve by first name: Zuzana/Miroslava → F, Matyáš/Jaromír/Radim → M.

### Accuracy
- `F` (certain): ~99%+ accurate for Czech names
- `F?` after correction: ~95%+ accurate
- `M`: ~98%+ accurate (some foreign male names with neutral endings)
- Good enough for corpus-level gender analysis; document the method in the paper

---

## 6. Anthropic API Setup

### API key and workspace spending limits
- Credits are **organisation-level** (shared across workspaces)
- But each workspace has its own **monthly spend limit** (default may be $0)
- A $0 workspace limit blocks all API calls even with org credits
- Fix: Console → switch to target workspace → Settings → Limits → set monthly limit

### Which workspace to use
- Create API keys in the **Default workspace** to avoid spending limit issues on new workspaces
- Store in `.env` file at repo root: `ANTHROPIC_API_KEY=sk-ant-api03-...`
- Load with: `from dotenv import load_dotenv; load_dotenv(Path(__file__).parent.parent.parent / ".env")`

### Model choice for batch classification
- `claude-haiku-4-5-20251001` — fast and cheap for structured JSON tasks
- For 1,200 classification pairs at batch size 30: **~$0.20 total**
- `max_tokens=512` is sufficient for a 30-item JSON array response

---

## 7. Visualisation

### GeoPandas world maps
`geopandas.datasets` is **deprecated in GeoPandas 1.0** — `gpd.datasets.get_path('naturalearth_lowres')` will raise an error.  
Use Plotly choropleth instead:
```python
import plotly.express as px
fig = px.choropleth(df, locations='iso_alpha', color='log_docs',
                    color_continuous_scale='YlOrRd')
fig.write_image('map.png')  # requires kaleido: pip install kaleido
```

### Date parsing
`pd.Timestamp(f"{year}-{doy:03d}", format="%Y-%j")` silently returns NaT for day-of-year format.  
Use `datetime.strptime(f"{year} {doy}", "%Y %j")` instead.

---

## 8. Performance Notes

| Task | Docs | Time | Notes |
|------|-----:|-----:|-------|
| Country detection (three-pass) | 3,000 | ~33s | Single-core; parallelise for larger corpora |
| Speaker regex extraction | 2,914 | ~15s | Fast — pure regex |
| Rule-based type classification | 56,613 | <1s | In-memory set lookup |
| LLM classification (Haiku) | 1,168 pairs | ~4min | 50 batches × 0.5s sleep + API latency |
| Stance extraction (regex segments) | 2,914 docs | ~15s | Finds speaker turn boundaries |
| Stance LLM classification (Haiku) | 5,928 segments | ~15min | 297 batches × 0.5s sleep; run with nohup |
| NMF topic model (k=20, 5000 vocab) | 2,914 docs | ~30s | sklearn, single-core |

---

## 10. Stance Coding (Phase 3)

### Speaker turn extraction
To extract what a speaker actually said, find their `Firstname SURNAME role` match in the text, then take all words until the next speaker boundary:
```python
SPEAKER_BOUNDARY = re.compile(rf'{U}{L}{{1,11}}\s+{U}{{2,20}}...\s+{L}{W}*')
next_m = SPEAKER_BOUNDARY.search(text, match_end + 1)
end = next_m.start() if next_m else len(text)
segment = text[match_end:end].strip()
```
Limit to `MAX_WORDS=200` — longer segments don't improve classification and inflate cost.

### LLM stance prompt design
- Include `S0 = Neutral/Other` as a valid label — this captures the majority of procedural/administrative speech (57% in this corpus). Without S0, the model over-assigns S3/S4.
- Include `SKIP` for fragments too short to classify.
- Return confidence 0–3 alongside type — useful for filtering uncertain classifications.
- Batch size 20 (not 30 as in Phase 2) — stance segments are longer, stay within `max_tokens=800`.

### Resume support is essential
With 297 batches at ~3s each, runs take ~15 minutes and will timeout in any sandbox. Always implement resume:
```python
done_keys = set(zip(done["article_id"], done["name"]))
records = [r for r in records if (r["article_id"], r["name"]) not in done_keys]
pd.DataFrame(rows).to_csv(OUT_RESULTS, mode='a', header=write_header, index=False)
```
Run with `nohup python script.py > /tmp/run.log 2>&1 &` and monitor with `tail -3 /tmp/run.log`.

### S0 dominance is expected
57% of segments will be S0 (neutral/procedural). This is not a failure — it reflects that most TV exchanges are administrative ("thank you", "let's turn to…", factual descriptions). Only ~43% of non-journalist speech actually expresses a climate stance.

### False balance detection
Count articles where S1/S2/S3 and S6 co-occur: `art['false_balance'] = art['has_s6'] & art['has_prob']`. Expect ~10% of articles with any non-neutral stances.

---

## 11. Topic Modeling Without Lemmatization

### Problem: journalist names pollute topics
Czech TV transcripts begin every turn with `Firstname SURNAME role`. Without stripping names, NMF picks up anchor names as the most distinctive features (e.g., T00: "daniel, takáč, tomáš"). Fix:
```python
# Suppress all M1 journalist name tokens
m1_names = set(token for name in m1['name'] for token in name.lower().split() if len(token)>3)
all_stops = BASE_STOPWORDS + list(m1_names)
vec = TfidfVectorizer(stop_words=all_stops, ...)
```

### No lemmatization — document in methods
UDPipe is not installed (`pip install ufal.udpipe` and a Czech model file are needed). Without lemmatization, inflected Czech forms are separate terms ("změna", "změny", "změnou"). This reduces topic coherence but topics remain interpretable. **State this explicitly in the methods section** — reviewers will ask.

### Choosing k
- k=10: good overview, topics too broad
- k=20: best balance — 8 substantive topics + named-entity / geopolitical topics
- k=25: some topic splitting (drought→drought/agriculture, forests→bark beetle/forest policy)
- Recommend k=20 for publication

### Topic labels file
After running, create `data/topic_labels_nmf{k}.csv` manually with columns: `topic, label, category, frame`. Categories used: MITIGATION, ADAPTATION, SCIENCE, POLICY, CZ POLICY, US POLICY, EU POLICY, INTERNATIONAL, GEOPOLITICS, ACTIVISM, OTHER.

---

## 9. Project Conventions

- **Output data** → `data/` (never committed to git — corpus files are large and private)
- **Analysis scripts** → `analysis/article{N}/`
- **Visualisations** → `visualizations/article{N}/`
- **Summary documents** → `analysis/article{N}/PHASE{N}_SUMMARY.md`
- **Findings** → `FINDINGS_PHASES*.md` (repo root)
- Corpus files live outside the repo in the `Climate change TV/` directory (see `CORPORA_INVENTORY.md`)
