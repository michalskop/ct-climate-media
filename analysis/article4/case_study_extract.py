"""P4.1–P4.3 — Case study document extraction and excerpt mining.

For each of three case studies, identifies relevant documents, pulls speaker
statistics, stances, and 3–5 illustrative excerpts.

Case studies:
  CS1: Nuclear energy & renewables (energy transition framing)
  CS2: Drought & floods (adaptation framing; climate linkage)
  CS3: Health impacts (expected near-absence — the silence is the finding)

Outputs:
  data/cs{N}_docs.csv          — relevant article_ids with metadata
  data/cs{N}_speakers.csv      — speaker type/stance breakdown
  data/cs{N}_excerpts.csv      — 5 best illustrative excerpts per case
  analysis/article4/CS{N}_analysis.md  — structured discourse analysis
"""

import re
from pathlib import Path
import pandas as pd

REPO   = Path(__file__).parent.parent.parent
BASE   = REPO / "Climate change TV/BackupClimateChangeData/2.data_transformations/data"
CORPUS = BASE / "climate_sub_corpus/climate_corpus_v4_2023.csv"
OUT    = REPO / "data"
ART4   = Path(__file__).parent

STANCE_LABELS = {'S1':'Denier','S2':'Manipulator','S3':'Delayer',
                 'S4':'Techno-optimist','S5':'Market-only','S6':'Informer','S0':'Neutral'}

# ── Case study keyword definitions ────────────────────────────────────────────
CASE_STUDIES = {
    'CS1': {
        'title': 'Nuclear Energy & Renewables: Framing the Energy Transition',
        'keywords': [
            'jaderná energie','jaderná elektrárna','atomová elektrárna','jaderný reaktor',
            'obnovitelná energie','obnovitelné zdroje','solární elektrárna','větrná elektrárna',
            'větrné elektrárny','fotovoltaika','uhelná elektrárna','odchod od uhlí',
            'konec uhlí','dekarbonizace','energetická transformace',
        ],
        'require_any': ['jaderná','obnovitelná','uhelná','dekarbonizace','energetická transformace'],
        'topic_ids': [7, 19],  # NMF k=20 topic indices
    },
    'CS2': {
        'title': 'Drought & Floods: Extreme Weather and Climate Linkage',
        'keywords': [
            'sucho','povodně','povodeň','záplavy','vlna veder','vedro','extrémní počasí',
            'extrémní sucho','nedostatek vody','zásoby vody','zemědělské sucho',
            'kůrovec','lesní požár','lesní požáry','plameny','hasiči',
        ],
        'require_any': ['sucho','povodeň','povodně','záplavy','vlna veder','extrémní'],
        'topic_ids': [10, 12, 15],
    },
    'CS3': {
        'title': 'Health Impacts: The Silence in ČT Climate Coverage',
        # Only docs where climate AND health are explicitly linked
        'keywords': [
            'dopady klimat','klimatick','vlna veder','horko','tepelný stres',
            'zdraví','zdravotní riziko','znečištění ovzduší',
        ],
        'require_any': ['dopady klimat','zdravotní dopady','klimatick.*zdraví',
                        'horko.*zdraví','vlna veder.*zdraví','zdraví.*klimat'],
        # Must contain both a climate word and a health word in same doc
        'require_all_extra': ['zdraví','zdravotní','úpal','tepelný stres',
                              'respirační','kardiovaskulár','ovzduší'],
        # Narrow further: use regex co-occurrence in find_docs
        'regex_cooccur': [
            r'dopady klimat\w*.*zdraví', r'zdraví.*dopady klimat',
            r'horko.*zdraví.*klimat', r'klimat.*vlna veder.*zdraví',
            r'klimat\w*.*zdravotní riziko',
        ],
        'topic_ids': [],
    },
}


def find_docs(corpus: pd.DataFrame, kws: list[str], require_any: list[str],
              require_all_extra: list[str] | None = None,
              regex_cooccur: list[str] | None = None) -> pd.DataFrame:
    cooccur_pats = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in (regex_cooccur or [])]
    hits = []
    for _, doc in corpus.iterrows():
        text = doc['text']
        if not isinstance(text, str):
            continue
        text_l = text.lower()
        if not any(r.lower() in text_l for r in require_any):
            continue
        if require_all_extra and not any(r.lower() in text_l for r in require_all_extra):
            continue
        # If regex co-occurrence patterns are defined, at least one must match
        if cooccur_pats and not any(p.search(text_l) for p in cooccur_pats):
            continue
        matched = [kw for kw in kws if kw.lower() in text_l]
        if matched:
            hits.append({
                'article_id': doc['article_id'],
                'year': int(str(doc['article_id'])[:4]),
                'n_kw_matches': len(matched),
                'matched_kws': '; '.join(matched[:5]),
            })
    return pd.DataFrame(hits).sort_values('n_kw_matches', ascending=False)


def get_speaker_stats(article_ids: set, stance_results: pd.DataFrame,
                      speakers_final: pd.DataFrame) -> pd.DataFrame:
    sub = stance_results[stance_results['article_id'].isin(article_ids)]
    sub = sub[sub['stance'].isin(STANCE_LABELS.keys())]
    return sub.groupby(['type_final','stance']).size().reset_index(name='count')


def extract_excerpts(corpus: pd.DataFrame, article_ids: list,
                     keywords: list[str], n: int = 5) -> list[dict]:
    excerpts = []
    kw_pats = [re.compile(r'\b' + re.escape(kw.lower()) + r'\b') for kw in keywords]

    for aid in article_ids[:50]:  # check first 50 docs by relevance
        rows = corpus[corpus['article_id'] == aid]
        if rows.empty:
            continue
        text = rows.iloc[0]['text']
        if not isinstance(text, str):
            continue
        text_l = text.lower()

        for pat in kw_pats:
            m = pat.search(text_l)
            if not m:
                continue
            # Extract ±150 words around the match
            pre  = text_l[:m.start()].split()
            post = text_l[m.end():].split()
            snippet_l = ' '.join(pre[-60:]) + ' [**' + text[m.start():m.end()] + '**] ' + ' '.join(post[:80])
            # Use original case text for readability
            start = max(0, m.start() - 300)
            end   = min(len(text), m.end() + 400)
            snippet = text[start:end].strip().replace('\n', ' ')

            excerpts.append({
                'article_id': aid,
                'year': int(str(aid)[:4]),
                'keyword': pat.pattern.strip(r'\b'),
                'excerpt': snippet[:600],
            })
            break  # one excerpt per doc

        if len(excerpts) >= n:
            break

    return excerpts[:n]


def write_md(cs_id: str, title: str, docs: pd.DataFrame, stats: pd.DataFrame,
             excerpts: list[dict], corpus_size: int):
    lines = [
        f"# Case Study {cs_id[-1]}: {title}",
        f"**Documents identified:** {len(docs):,} of {corpus_size:,} ({len(docs)/corpus_size*100:.1f}%)",
        f"**Year range:** {docs['year'].min()}–{docs['year'].max()} | "
        f"**Peak year:** {docs.groupby('year').size().idxmax()} "
        f"({docs.groupby('year').size().max()} docs)",
        "",
        "---",
        "",
        "## Speaker & Stance Profile",
        "",
    ]

    if not stats.empty:
        lines.append("| Type | Stance | Count |")
        lines.append("|------|--------|------:|")
        for _, r in stats.sort_values('count', ascending=False).head(15).iterrows():
            lines.append(f"| {r['type_final']} | {STANCE_LABELS.get(r['stance'],r['stance'])} | {r['count']} |")
    else:
        lines.append("_No stance data matched._")

    lines += ["", "---", "", "## Illustrative Excerpts", ""]

    if excerpts:
        for i, ex in enumerate(excerpts, 1):
            lines.append(f"### Excerpt {i} ({ex['year']}, doc {ex['article_id']})")
            lines.append(f"**Keyword trigger:** `{ex['keyword']}`")
            lines.append("")
            lines.append(f"> {ex['excerpt']}")
            lines.append("")
    else:
        lines.append("_No excerpts found — the absence of matching excerpts is itself a finding._")

    lines += ["", "---", "", "## Key Observations", "",
              "_[To be completed by analyst — qualitative discourse analysis]_", ""]

    (ART4 / f"{cs_id}_analysis.md").write_text('\n'.join(lines), encoding='utf-8')


def main():
    print("Loading corpus…")
    corpus  = pd.read_csv(CORPUS, sep=";", low_memory=False)
    stance  = pd.read_csv(OUT / "stance_results.csv")
    spk_fin = pd.read_csv(OUT / "speakers_final.csv")
    print(f"  {len(corpus):,} documents")

    for cs_id, cs in CASE_STUDIES.items():
        print(f"\n── {cs_id}: {cs['title'][:50]}…")
        docs = find_docs(corpus, cs['keywords'], cs['require_any'],
                         cs.get('require_all_extra'), cs.get('regex_cooccur'))
        docs.to_csv(OUT / f"{cs_id}_docs.csv", index=False)
        print(f"  {len(docs):,} documents matched")

        if not docs.empty:
            print(f"  Year distribution: {docs.groupby('year').size().to_dict()}")
            aid_set = set(docs['article_id'])
            stats = get_speaker_stats(aid_set, stance, spk_fin)
            stats.to_csv(OUT / f"{cs_id}_speakers.csv", index=False)

            excerpts = extract_excerpts(corpus, docs['article_id'].tolist(), cs['keywords'])
            ex_df = pd.DataFrame(excerpts)
            ex_df.to_csv(OUT / f"{cs_id}_excerpts.csv", index=False)
            print(f"  Excerpts extracted: {len(excerpts)}")

            write_md(cs_id, cs['title'], docs, stats, excerpts, len(corpus))
            print(f"  → {cs_id}_analysis.md")


if __name__ == "__main__":
    main()
