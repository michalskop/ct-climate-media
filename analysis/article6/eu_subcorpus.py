"""P6.1 — Build EU climate policy subcorpus from the climate corpus.

Extracts documents mentioning EU climate policy terms (Green Deal, Fit for 55,
ETS, combustion ban, etc.) and saves them with matched keyword groups.

Output:
  data/eu_subcorpus.csv   — 131 docs with article_id, year, matched_groups, text
"""

from pathlib import Path
import pandas as pd

REPO   = Path(__file__).parent.parent.parent
BASE   = REPO / 'Climate change TV/BackupClimateChangeData/2.data_transformations/data'
CORPUS = BASE / 'climate_sub_corpus/climate_corpus_v4_2023.csv'
OUT    = REPO / 'data'

KW_GROUPS = {
    'green_deal':     ['green deal', 'zelená dohoda', 'zelený nový úděl'],
    'fit_for_55':     ['fit for 55', 'fit for fifty', 'balíček 55'],
    'ets':            ['emisní povolen', 'obchodování s emisemi', 'emisní obchodov',
                       'systém ets', 'trh s emisemi'],
    'eu_taxonomy':    ['eu taxonom', 'taxonomie eu', 'zelená taxonom'],
    'combustion_ban': ['spalovací motor', 'zákaz spalov', 'konec spalov'],
    'repower':        ['repowereu', 'repower eu'],
    'cbam':           ['cbam', 'uhlíkové clo'],
    'eu_climate_law': ['evropský klimatický zákon', 'klimatická neutralita 2050',
                       'klimatická neutral'],
}

ALL_KWS = [kw for kws in KW_GROUPS.values() for kw in kws]


def matched_groups(text: str) -> str:
    tl = text.lower() if isinstance(text, str) else ''
    return '; '.join(g for g, kws in KW_GROUPS.items() if any(k in tl for k in kws))


def main():
    print("Loading corpus…")
    corpus = pd.read_csv(CORPUS, sep=';', low_memory=False)
    print(f"  {len(corpus):,} documents")

    mask = corpus['text'].apply(
        lambda t: any(k in t.lower() for k in ALL_KWS) if isinstance(t, str) else False
    )
    sub = corpus[mask].copy()
    sub['year'] = sub['article_id'].astype(str).str[:4].astype(int)
    sub['matched_groups'] = sub['text'].apply(matched_groups)

    print(f"  {len(sub):,} EU climate policy documents ({len(sub)/len(corpus)*100:.1f}%)")
    print(f"  Year distribution: {sub.groupby('year').size().to_dict()}")

    sub[['article_id', 'year', 'matched_groups', 'text']].to_csv(
        OUT / 'eu_subcorpus.csv', index=False)
    print(f"  → data/eu_subcorpus.csv")


if __name__ == '__main__':
    main()
