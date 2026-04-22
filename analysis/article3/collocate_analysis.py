"""P3.16 — Collocate analysis for key climate terms.

For each seed term, finds the most frequent words appearing within a ±10-word
window across the climate subcorpus. Uses simple word-tokenization (no lemma).

Outputs:
  data/collocates_{term}.csv   — top collocates per seed term
  visualizations/article3/P3.3_collocates.png  — horizontal bar chart (top 4 terms)
"""

from collections import Counter
from pathlib import Path
import re
import pandas as pd
import matplotlib.pyplot as plt

REPO   = Path(__file__).parent.parent.parent
BASE   = REPO / "Climate change TV/BackupClimateChangeData/2.data_transformations/data"
CORPUS = BASE / "climate_sub_corpus/climate_corpus_v4_2023.csv"
OUT    = REPO / "data"
VIZ    = REPO / "visualizations/article3"

SEED_TERMS = {
    "klimatická změna":    ["klimatická změna", "klimatické změny", "klimatickou změnu",
                            "klimatické změně", "klimatickou změnou"],
    "globální oteplování": ["globální oteplování", "globálního oteplování",
                            "globálnímu oteplování"],
    "krize":               ["klimatická krize", "klimatické krize", "klimatickou krizi"],
    "riziko":              ["klimatické riziko", "klimatická rizika", "klimatického rizika"],
}

STOPWORDS = {
    # Czech function words
    'a','ale','aby','ani','ano','avšak','bez','byl','byla','byli','bylo','být',
    'co','což','či','do','hodně','i','já','je','jej','jeho','jej','jejich','jí',
    'jim','jen','jenž','jelikož','jestliže','jak','jako','již','jde','jsme','jsou',
    'jsem','jste','jí','k','kde','kdo','kdy','když','která','které','který','kteří',
    'kvůli','má','mají','mezi','mi','mít','mně','moc','mohl','mohlo','může','my',
    'na','nad','nám','nás','nebo','není','něco','nějak','někdy','někteří','než',
    'nic','nijak','nikdy','no','nyní','o','od','on','ona','oni','ono','pak',
    'plus','po','pod','podle','pokud','poté','pro','proto','protože','při',
    's','se','si','sice','stále','svého','svou','své','svůj','svými','svým',
    'tak','také','takto','takže','tato','tedy','ten','tehdy','to','tohoto',
    'toho','tomu','toto','tu','tuto','tyto','těch','těchto','těm',
    'u','už','v','va','ve','více','vlastně','vše','všechno','všichni','vůbec',
    'z','za','ze','že','aby','jež','dle','skrze','jí','jej','jej','bude',
    'budu','budem','budeme','budou','budeš','budete','bývá','bývají',
    'bylo','byla','byli','bych','bys','by','byste','jsem','jsi','je',
    'jsme','jste','jsou','právě','třeba','muset','mohou','musím','musí',
    # CT transcript roles (appear near every speaker)
    'redaktor','redaktorka','moderátor','moderátorka','zpravodaj','zpravodajka',
    'reportér','reportérka','komentátor','komentátorka',
}

WINDOW = 10


def tokenize(text: str) -> list[str]:
    return re.findall(r'\b[a-záčďéěíňóřšťúůýža-z]{3,}\b', text.lower())


def find_collocates(corpus: pd.DataFrame, seed_forms: list[str], window: int = WINDOW) -> Counter:
    counts: Counter = Counter()
    seed_lower = [s.lower() for s in seed_forms]

    for _, doc in corpus.iterrows():
        text = doc["text"]
        if not isinstance(text, str):
            continue
        text_l = text.lower()
        tokens = tokenize(text)

        for seed in seed_lower:
            idx = 0
            while True:
                pos = text_l.find(seed, idx)
                if pos == -1:
                    break
                # find token position
                pre_text  = text_l[:pos]
                pre_tokens = tokenize(pre_text)
                t_idx = len(pre_tokens)
                left  = max(0, t_idx - window)
                right = min(len(tokens), t_idx + window + len(seed.split()))
                context_tokens = tokens[left:t_idx] + tokens[t_idx + len(seed.split()):right]
                for tok in context_tokens:
                    if tok not in STOPWORDS and len(tok) > 3 and not tok.isdigit():
                        counts[tok] += 1
                idx = pos + 1

    return counts


def main():
    print("Loading corpus…")
    corpus = pd.read_csv(CORPUS, sep=";", low_memory=False)

    results = {}
    for term_label, seed_forms in SEED_TERMS.items():
        print(f"  Collocates for '{term_label}'…")
        counts = find_collocates(corpus, seed_forms)
        top = pd.DataFrame(counts.most_common(50), columns=["word", "count"])
        top["seed"] = term_label
        fname = term_label.replace(" ", "_").replace("/", "_")
        top.to_csv(OUT / f"collocates_{fname}.csv", index=False)
        results[term_label] = top
        print(f"    Top 5: {', '.join(top['word'].head(5).tolist())}")

    # ── Chart: top 15 collocates for key terms ──────────────────────────────────
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    for ax, (term, top) in zip(axes, results.items()):
        top15 = top.head(15).sort_values("count")
        ax.barh(top15["word"], top15["count"], color="#4C72B0")
        ax.set_title(f'"{term}"', fontsize=11, fontweight='bold')
        ax.set_xlabel("Co-occurrence count")
    plt.suptitle("Top collocates of key climate terms — ČT climate corpus (±10 words)",
                 fontsize=13, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(VIZ / "P3.3_collocates.png", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\nChart saved → {VIZ / 'P3.3_collocates.png'}")


if __name__ == "__main__":
    main()
