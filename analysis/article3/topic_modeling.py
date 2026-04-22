"""P3.7/P3.8/P3.10 — NMF topic modeling on climate subcorpus.

Uses sklearn NMF with TF-IDF. No lemmatization (UDPipe not installed) — inflected
forms appear separately but topics are still interpretable. Note this in methods.

Runs NMF for k=10,15,20,25 and prints top terms per topic for manual labeling.

Outputs:
  data/topics_nmf_{k}.csv          — doc × topic weight matrix
  data/topic_terms_nmf_{k}.csv     — top 20 terms per topic
  visualizations/article3/P3.7_topic_heatmap_nmf{k}.png
"""

import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

REPO   = Path(__file__).parent.parent.parent
BASE   = REPO / "Climate change TV/BackupClimateChangeData/2.data_transformations/data"
CORPUS = BASE / "climate_sub_corpus/climate_corpus_v4_2023.csv"
OUT    = REPO / "data"
VIZ    = REPO / "visualizations/article3"
VIZ.mkdir(parents=True, exist_ok=True)

# Czech stopwords — extended list
STOPWORDS = [
    'a','aby','ale','ani','ano','anebo','aniž','aspoň','atd','atp','avšak',
    'az','až','bez','bude','budem','budeme','budou','budeš','budete',
    'bych','bychom','byste','by','byl','byla','byli','bylo','být',
    'co','což','či','dál','dále','díky','do','dost','již','jelikož',
    'jen','jenom','ještě','jinak','jiný','jednak','je','jej','jeho',
    'jejich','jemu','jen','jsou','jsem','jsi','jsme','jste',
    'k','kam','kde','kdo','kdy','když','která','které','který','kteří',
    'kvůli','málo','mezi','mít','mně','moc','mohou','může','my',
    'na','nad','nám','nás','nebo','není','nejen','nejprve','než',
    'nic','nikdy','no','nyní','o','od','on','ona','oni','ono',
    'pak','po','pod','podle','pokud','poté','pro','proto','protože','při',
    'právě','přes','prostě','přesto','přitom','přece',
    's','se','si','sice','spíš','stále','své','svůj','svých','svým',
    'tak','také','takto','takže','tady','tato','tedy','ten','tím',
    'toto','tu','tuto','tyto','těch','těchto','těm',
    'u','už','v','va','ve','více','vlastně','vše','všechno','všichni',
    'z','za','ze','že','zase','zatím','zato','zde','zrovna','zvláště',
    'dnes','teď','tady','zde','ještě','potom','poté','přitom','sám',
    'samotný','samozřejmě','celý','celá','celé','celém','celou',
    # CT transcript boilerplate
    'redaktor','redaktorka','moderátor','moderátorka','zpravodaj',
    'dobrý','večer','dobré','ráno','dobrý','den',
]

N_TOPICS_LIST = [15, 20, 25]
TOP_N_TERMS   = 20


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ''
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    # Remove pure numbers and very short tokens
    tokens = [t for t in text.split() if len(t) > 3 and not t.isdigit()]
    return ' '.join(tokens)


def get_name_stopwords() -> list[str]:
    """Return lowercased name tokens from all M1 journalists to suppress."""
    try:
        final = pd.read_csv(Path(__file__).parent.parent.parent / "data/speakers_final.csv")
        m1 = final[final['type_final'] == 'M1']
        tokens = set()
        for name in m1['name']:
            for part in name.lower().split():
                if len(part) > 3:
                    tokens.add(part)
        return list(tokens)
    except Exception:
        return []


def run_nmf(corpus: pd.DataFrame, n_topics: int):
    print(f"\n{'='*50}")
    print(f"NMF k={n_topics}")
    texts = corpus['text'].apply(clean_text).tolist()
    ids   = corpus['article_id'].tolist()

    all_stops = STOPWORDS + get_name_stopwords()
    vec = TfidfVectorizer(
        max_features=5000,
        min_df=5,           # word must appear in ≥5 docs
        max_df=0.85,        # ignore words in >85% of docs
        stop_words=all_stops,
        ngram_range=(1, 2),
    )
    X = vec.fit_transform(texts)
    terms = vec.get_feature_names_out()
    print(f"  Vocabulary: {len(terms):,} terms, matrix {X.shape}")

    model = NMF(n_components=n_topics, random_state=42, max_iter=500)
    W = model.fit_transform(X)   # doc × topic
    H = model.components_        # topic × term

    # Top terms per topic
    topic_terms = []
    print(f"\nTop terms per topic:")
    for t_idx in range(n_topics):
        top_idx = H[t_idx].argsort()[::-1][:TOP_N_TERMS]
        top_terms = terms[top_idx].tolist()
        topic_terms.append({'topic': t_idx, 'terms': ', '.join(top_terms)})
        print(f"  T{t_idx:02d}: {', '.join(top_terms[:10])}")

    # Save topic terms
    pd.DataFrame(topic_terms).to_csv(OUT / f"topic_terms_nmf_{n_topics}.csv", index=False)

    # Save doc-topic matrix
    doc_topic = pd.DataFrame(W, columns=[f"T{i:02d}" for i in range(n_topics)])
    doc_topic.insert(0, 'article_id', ids)
    doc_topic.insert(1, 'year', [int(str(aid)[:4]) for aid in ids])
    # Dominant topic
    doc_topic['dominant_topic'] = W.argmax(axis=1)
    doc_topic.to_csv(OUT / f"topics_nmf_{n_topics}.csv", index=False)

    return doc_topic, H, terms, model


def main():
    print("Loading corpus…")
    corpus = pd.read_csv(CORPUS, sep=";", low_memory=False)
    print(f"  {len(corpus):,} documents")

    # Run for each k
    for k in N_TOPICS_LIST:
        doc_topic, H, terms, model = run_nmf(corpus, k)

        # Simple heatmap: topic weight by year
        yearly = doc_topic.groupby('year')[[f"T{i:02d}" for i in range(k)]].mean()
        fig, ax = plt.subplots(figsize=(max(10, k//2), 5))
        im = ax.imshow(yearly.values.T, cmap='YlOrRd', aspect='auto')
        ax.set_yticks(range(k))
        ax.set_yticklabels([f"T{i:02d}" for i in range(k)], fontsize=8)
        ax.set_xticks(range(len(yearly.index)))
        ax.set_xticklabels(yearly.index, rotation=45)
        plt.colorbar(im, ax=ax, label='Mean topic weight')
        ax.set_title(f'NMF k={k}: Topic weight by year (climate subcorpus)', fontweight='bold')
        plt.tight_layout()
        plt.savefig(VIZ / f"P3.7_topic_heatmap_nmf{k}.png", dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Saved P3.7_topic_heatmap_nmf{k}.png")

    print("\nDone. Review topic_terms_nmf_*.csv to label topics manually.")


if __name__ == "__main__":
    main()
