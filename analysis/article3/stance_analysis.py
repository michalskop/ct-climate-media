"""P3.4/P3.6 — Stance distribution analysis and visualization.

Reads stance_final.csv and produces:
  - S1–S6 distribution overall and by speaker type
  - Yearly stance trend
  - M-type × S-type heatmap

Outputs:
  data/stance_by_type.csv
  data/stance_by_year.csv
  visualizations/article3/P3.4_stance_overall.png
  visualizations/article3/P3.5_stance_by_type_heatmap.png
  visualizations/article3/P3.6_stance_trend.png
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

REPO    = Path(__file__).parent.parent.parent
RESULTS = REPO / "data/stance_results.csv"
ALL_M   = REPO / "data/speakers_all.csv"
FINAL   = REPO / "data/speakers_final.csv"
OUT     = REPO / "data"
VIZ     = REPO / "visualizations/article3"
VIZ.mkdir(parents=True, exist_ok=True)

STANCE_LABELS = {
    'S1': 'S1 Denier',
    'S2': 'S2 Manipulator',
    'S3': 'S3 Delayer',
    'S4': 'S4 Techno-optimist',
    'S5': 'S5 Market-only',
    'S6': 'S6 Informer',
    'S0': 'S0 Neutral',
}
STANCE_COLORS = {
    'S1': '#C44E52', 'S2': '#DD8452', 'S3': '#E8A842',
    'S4': '#8172B2', 'S5': '#CCB974',
    'S6': '#55A868', 'S0': '#9E9E9E',
}
TYPE_LABELS = {'M2':'Citizen','M3':'Scientist','M4':'Pseudo-sci','M5':'Stakeholder','M6':'Politician'}


def main():
    results = pd.read_csv(RESULTS)
    all_m   = pd.read_csv(ALL_M)

    # Merge year back in via all_mentions
    year_map = all_m[['article_id']].copy()
    year_map['year'] = all_m['article_id'].astype(str).str[:4].astype(int)
    year_map = year_map.drop_duplicates('article_id').set_index('article_id')['year'].to_dict()
    results['year'] = results['article_id'].map(year_map)

    # Filter to meaningful stances (exclude SKIP and ?)
    classified = results[results['stance'].isin(['S1','S2','S3','S4','S5','S6','S0'])]
    non_neutral = classified[classified['stance'] != 'S0']

    print(f"Total classified segments: {len(classified):,}")
    print(f"Non-neutral stances: {len(non_neutral):,}")

    print("\n=== Overall stance distribution (classified only) ===")
    dist = classified['stance'].value_counts()
    print(dist)
    dist.to_csv(OUT / "stance_overall.csv")

    print("\n=== Non-neutral stance distribution ===")
    print(non_neutral['stance'].value_counts())

    # ── Chart 1: Overall stance bar ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(9, 4))
    stances = [s for s in ['S6','S0','S4','S5','S3','S2','S1'] if s in dist.index]
    vals  = [dist.get(s, 0) for s in stances]
    labels = [STANCE_LABELS.get(s, s) for s in stances]
    colors = [STANCE_COLORS.get(s, '#999') for s in stances]
    bars = ax.bar(labels, vals, color=colors, width=0.7)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(v), ha='center', va='bottom', fontsize=9)
    ax.set_ylabel('Speaker-article segments')
    ax.set_title('Climate stance distribution in ČT coverage\n(non-journalist speakers, 2012–2022)',
                 fontweight='bold')
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    plt.savefig(VIZ / 'P3.4_stance_overall.png', dpi=150, bbox_inches='tight')
    plt.close()

    # ── Chart 2: M-type × S-type heatmap ─────────────────────────────────────
    ct = pd.crosstab(classified['type_final'], classified['stance'])
    ct = ct[[s for s in ['S6','S0','S4','S5','S3','S2','S1'] if s in ct.columns]]
    ct_pct = ct.div(ct.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(ct_pct.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=80)
    ax.set_xticks(range(len(ct_pct.columns)))
    ax.set_xticklabels([STANCE_LABELS.get(c, c) for c in ct_pct.columns], rotation=20, ha='right')
    ax.set_yticks(range(len(ct_pct.index)))
    ax.set_yticklabels([TYPE_LABELS.get(t, t) for t in ct_pct.index])
    for i in range(len(ct_pct.index)):
        for j in range(len(ct_pct.columns)):
            v = ct_pct.values[i, j]
            ax.text(j, i, f'{v:.0f}%', ha='center', va='center',
                    fontsize=9, color='black' if v < 60 else 'white')
    plt.colorbar(im, ax=ax, label='% of speaker type')
    ax.set_title('Speaker type × Climate stance (% within type)', fontweight='bold')
    plt.tight_layout()
    plt.savefig(VIZ / 'P3.5_stance_by_type_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

    # ── Chart 3: Yearly stance trend (non-neutral) ────────────────────────────
    yr = (non_neutral.groupby(['year','stance']).size()
          .unstack(fill_value=0)
          .reindex(columns=['S1','S2','S3','S4','S5','S6'], fill_value=0))
    doc_yr = non_neutral.groupby('year')['article_id'].nunique()

    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = pd.Series(0, index=yr.index)
    for s in ['S1','S2','S3','S5','S4','S6']:
        if s not in yr.columns:
            continue
        ax.bar(yr.index, yr[s], bottom=bottom,
               label=STANCE_LABELS.get(s, s), color=STANCE_COLORS.get(s, '#999'), width=0.75)
        bottom += yr[s]
    ax.set_xlabel('Year'); ax.set_ylabel('Speaker-article segments')
    ax.set_title('Climate stance over time — non-neutral speakers\n(ČT climate coverage 2012–2022)',
                 fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.set_xticks(yr.index)
    plt.tight_layout()
    plt.savefig(VIZ / 'P3.6_stance_trend.png', dpi=150, bbox_inches='tight')
    plt.close()

    print("\nCharts saved:")
    print("  P3.4_stance_overall.png")
    print("  P3.5_stance_by_type_heatmap.png")
    print("  P3.6_stance_trend.png")

    # Save data tables
    ct.to_csv(OUT / 'stance_by_type.csv')
    yr.to_csv(OUT / 'stance_by_year.csv')


if __name__ == "__main__":
    main()
