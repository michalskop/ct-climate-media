"""P6.3/P6.4 — EU climate policy: temporal sentiment + actor analysis.

Reads eu_sentiment.csv and stance_results.csv to produce:
  - Sentiment distribution overall and by year
  - Actor analysis: who speaks in EU climate policy docs (M1–M6 × sentiment)
  - Topic group breakdown (which EU policy areas dominate)
  - Visualizations

Outputs:
  data/eu_analysis_summary.csv
  visualizations/article6/P6.1_eu_sentiment_by_year.png
  visualizations/article6/P6.2_eu_actors.png
  visualizations/article6/P6.3_eu_topic_groups.png
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / 'analysis'))
from viz_style import apply_style, COLORS, PALETTE

apply_style()

DATA = REPO / 'data'
VIZ  = REPO / 'visualizations/article6'
VIZ.mkdir(parents=True, exist_ok=True)

SENT_COLORS = {
    'EU_POS':  '#2E6B3E',   # green
    'EU_NEU':  '#AAAAAA',   # grey
    'EU_NEG':  '#8B1A1A',   # dark red
    'SKIP':    '#E0D8CF',   # cream
}
SENT_LABELS = {
    'EU_POS': 'Positive (EU policy as solution)',
    'EU_NEU': 'Neutral (factual reporting)',
    'EU_NEG': 'Negative (EU overreach framing)',
    'SKIP':   'Incidental mention',
}


def chart_sentiment_by_year(sent: pd.DataFrame):
    # Exclude SKIP from year chart
    s = sent[sent['sentiment'] != 'SKIP'].copy()
    pt = s.groupby(['year', 'sentiment']).size().unstack(fill_value=0)
    pt_pct = pt.div(pt.sum(axis=1), axis=0) * 100

    order = ['EU_POS', 'EU_NEU', 'EU_NEG']
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Stacked bar — absolute
    ax = axes[0]
    bottom = np.zeros(len(pt))
    for s_label in order:
        if s_label not in pt.columns:
            continue
        ax.bar(pt.index, pt[s_label], bottom=bottom,
               color=SENT_COLORS[s_label], label=SENT_LABELS[s_label], alpha=0.9)
        bottom += pt[s_label].values
    ax.set_title('EU Climate Policy Framing — Annual Count', fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Documents')
    ax.set_xticks(pt.index)
    ax.tick_params(axis='x', rotation=45)
    ax.legend(fontsize=9)

    # Stacked bar — %
    ax = axes[1]
    bottom = np.zeros(len(pt_pct))
    for s_label in order:
        if s_label not in pt_pct.columns:
            continue
        ax.bar(pt_pct.index, pt_pct[s_label], bottom=bottom,
               color=SENT_COLORS[s_label], label=SENT_LABELS[s_label], alpha=0.9)
        bottom += pt_pct[s_label].values
    ax.set_title('EU Climate Policy Framing — Annual % (excl. SKIP)', fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('% of documents')
    ax.set_xticks(pt_pct.index)
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylim(0, 105)

    plt.tight_layout()
    fig.savefig(VIZ / 'P6.1_eu_sentiment_by_year.png', bbox_inches='tight')
    plt.close(fig)
    print("  → P6.1_eu_sentiment_by_year.png")


def chart_actors(sent: pd.DataFrame, stance: pd.DataFrame):
    eu_ids = set(sent[sent['sentiment'] != 'SKIP']['article_id'].astype(str))
    sub = stance[stance['article_id'].astype(str).isin(eu_ids)]

    if sub.empty:
        print("  [skip] no stance data for EU docs")
        return

    # Speaker type counts
    type_counts = sub.groupby('type_final').size().sort_values(ascending=False)

    # Cross-tabulate type × EU sentiment
    merged = sub.merge(
        sent[['article_id', 'sentiment']].assign(article_id=lambda d: d['article_id'].astype(str)),
        on='article_id', how='left')
    ct = merged.groupby(['type_final', 'sentiment']).size().unstack(fill_value=0)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Speaker type bar
    ax = axes[0]
    types = type_counts.index.tolist()
    type_colors = {'M1':'#6B6B6B','M2':'#4C6B9A','M3':'#2E6B3E',
                   'M4':'#8B1A1A','M5':'#9A7A4C','M6':'#C44E52'}
    ax.bar(types, [type_counts[t] for t in types],
           color=[type_colors.get(t, COLORS['primary']) for t in types])
    ax.set_title('Speaker Types in EU Climate Policy Docs', fontweight='bold')
    ax.set_ylabel('Speaker segments')
    for i, (t, v) in enumerate(zip(types, [type_counts[t] for t in types])):
        ax.text(i, v + 1, str(v), ha='center', fontsize=10)

    # Heatmap: sentiment × speaker type (normalised per sentiment)
    ax = axes[1]
    order_sent = ['EU_POS', 'EU_NEU', 'EU_NEG']
    order_type = ['M6', 'M5', 'M3', 'M2', 'M1']
    matrix = ct.reindex(index=order_type, columns=order_sent, fill_value=0)
    matrix_pct = matrix.div(matrix.sum(axis=0).replace(0, 1), axis=1) * 100

    im = ax.imshow(matrix_pct.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=60)
    ax.set_xticks(range(len(order_sent)))
    ax.set_xticklabels([SENT_LABELS[s].split('(')[0].strip() for s in order_sent], fontsize=10)
    ax.set_yticks(range(len(order_type)))
    ax.set_yticklabels(order_type)
    ax.set_title('Speaker Type × EU Framing\n(% of column)', fontweight='bold')
    for i in range(len(order_type)):
        for j in range(len(order_sent)):
            v = matrix_pct.values[i, j]
            ax.text(j, i, f'{v:.0f}%', ha='center', va='center',
                    fontsize=10, color='black' if v < 40 else 'white')
    plt.colorbar(im, ax=ax, label='% of sentiment column')

    plt.tight_layout()
    fig.savefig(VIZ / 'P6.2_eu_actors.png', bbox_inches='tight')
    plt.close(fig)
    print("  → P6.2_eu_actors.png")


def chart_topic_groups(sent: pd.DataFrame):
    from collections import Counter
    groups = Counter(
        g.strip()
        for gs in sent['matched_groups'].dropna()
        for g in gs.split(';')
        if g.strip()
    )
    labels = list(groups.keys())
    values = [groups[l] for l in labels]
    idx = sorted(range(len(values)), key=lambda i: -values[i])
    labels = [labels[i] for i in idx]
    values = [values[i] for i in idx]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(labels, values, color=COLORS['primary'], alpha=0.85)
    ax.set_title('EU Climate Policy — Document Count by Policy Area', fontweight='bold')
    ax.set_ylabel('Documents')
    ax.tick_params(axis='x', rotation=30)
    for i, v in enumerate(values):
        ax.text(i, v + 0.3, str(v), ha='center', fontsize=10)
    plt.tight_layout()
    fig.savefig(VIZ / 'P6.3_eu_topic_groups.png', bbox_inches='tight')
    plt.close(fig)
    print("  → P6.3_eu_topic_groups.png")


def print_summary(sent: pd.DataFrame):
    print("\n=== EU Climate Policy Sentiment Summary ===\n")
    dist = sent['sentiment'].value_counts()
    total = len(sent)
    for s, n in dist.items():
        print(f"  {s:10} {n:4d}  ({n/total*100:.1f}%)")

    print("\nBy year (excl. SKIP):")
    s = sent[sent['sentiment'] != 'SKIP']
    pt = s.groupby(['year','sentiment']).size().unstack(fill_value=0)
    print(pt.to_string())

    print("\nSample EU_NEG rationales:")
    neg = sent[sent['sentiment'] == 'EU_NEG'][['article_id','year','rationale']].head(8)
    for _, r in neg.iterrows():
        print(f"  [{r['year']}] {r['rationale']}")

    sent.to_csv(DATA / 'eu_analysis_summary.csv', index=False)
    print("\n→ data/eu_analysis_summary.csv")


def main():
    sent   = pd.read_csv(DATA / 'eu_sentiment.csv')
    stance = pd.read_csv(DATA / 'stance_results.csv')

    print_summary(sent)
    chart_sentiment_by_year(sent)
    chart_actors(sent, stance)
    chart_topic_groups(sent)
    print("\nDone.")


if __name__ == '__main__':
    main()
