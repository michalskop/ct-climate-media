"""P5 — Regenerate all key charts with unified visual style.

Reads the already-computed data CSVs and redraws each chart using the
shared viz_style palette (dark red #8B1A1A, cream background).

Charts produced:
  Article 1: world map (skipped — plotly/kaleido), GNI comparison, monthly timeseries
  Article 2: speaker types by year, gender by type, top-20 speakers
  Article 3: urgency trend, stance distribution, stance by type, topic categories, TJ radar
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO / 'analysis'))
from viz_style import apply_style, COLORS, PALETTE, STANCE_COLORS, STANCE_LABELS, TYPE_COLORS

apply_style()

DATA = REPO / 'data'
OUT1 = REPO / 'visualizations/article1'
OUT2 = REPO / 'visualizations/article2'
OUT3 = REPO / 'visualizations/article3'
OUT5 = REPO / 'visualizations/article5'
OUT5.mkdir(parents=True, exist_ok=True)

SUFFIX = '_v2'   # append to avoid overwriting originals until reviewed


# ── helpers ────────────────────────────────────────────────────────────────────

def save(fig, path: Path):
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)
    print(f"  saved → {path.name}")


# ── Article 1 charts ───────────────────────────────────────────────────────────

def chart_subcorpus_sizes():
    sizes = {
        'Climate change':      2914,
        'Social / poverty':    4853,
        'Debt enforcement':    3379,
        'COVID-19':           33284,
        'Motorist / transport': 63496,
    }
    labels = list(sizes.keys())
    values = list(sizes.values())
    colors = [COLORS['primary'] if 'Climate' in l else COLORS['grid'] for l in labels]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(labels, values, color=colors, edgecolor='white', linewidth=0.8)
    ax.set_xlabel('Documents')
    ax.set_title('ČT Corpus — Subcorpus Sizes', fontweight='bold')
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 400, bar.get_y() + bar.get_height() / 2,
                f'{val:,}', va='center', fontsize=10)
    ax.set_xlim(0, max(values) * 1.15)
    save(fig, OUT5 / f'P1.13_subcorpus_sizes{SUFFIX}.png')


def chart_income_groups():
    data = {
        'Debt enforcement': {'High': 86.8, 'Upper middle': 9.1, 'Lower middle': 3.0, 'Low': 0.9},
        'COVID-19':         {'High': 84.1, 'Upper middle': 11.7,'Lower middle': 3.4, 'Low': 0.7},
        'Motorist':         {'High': 83.1, 'Upper middle': 11.1,'Lower middle': 3.8, 'Low': 1.9},
        'Social/poverty':   {'High': 77.9, 'Upper middle': 13.3,'Lower middle': 5.4, 'Low': 3.1},
        'Climate':          {'High': 75.6, 'Upper middle': 15.8,'Lower middle': 6.0, 'Low': 2.5},
    }
    groups = ['High', 'Upper middle', 'Lower middle', 'Low']
    gcolors = [COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['neutral']]
    subcorpora = list(data.keys())
    x = np.arange(len(subcorpora))
    width = 0.2

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (grp, col) in enumerate(zip(groups, gcolors)):
        vals = [data[s][grp] for s in subcorpora]
        ax.bar(x + i * width, vals, width, label=grp, color=col)
    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(subcorpora, rotation=15, ha='right')
    ax.set_ylabel('% of country mentions')
    ax.set_title('Geographic Coverage by Income Group — Cross-Subcorpus', fontweight='bold')
    ax.legend(title='Income group', loc='upper right')
    save(fig, OUT5 / f'P1.11b_gni_comparison{SUFFIX}.png')


def chart_monthly_timeseries():
    try:
        freq = pd.read_csv(DATA / 'frequency_combined.csv')
    except FileNotFoundError:
        print("  [skip] frequency_combined.csv not found")
        return
    # Use yearly aggregation from stance_results as proxy for doc count
    try:
        stance = pd.read_csv(DATA / 'stance_results.csv')
        yearly = stance.groupby(stance['article_id'].astype(str).str[:4])['article_id'].nunique()
        yearly.index = yearly.index.astype(int)
    except Exception:
        print("  [skip] stance_results.csv not available for timeseries")
        return

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(yearly.index, yearly.values, color=COLORS['primary'], alpha=0.85, width=0.7)
    ax.set_xlabel('Year')
    ax.set_ylabel('Documents')
    ax.set_title('ČT Climate Coverage — Annual Document Count (2012–2022)', fontweight='bold')
    ax.set_xticks(yearly.index)
    ax.tick_params(axis='x', rotation=45)
    save(fig, OUT5 / f'P1.14_annual_docs{SUFFIX}.png')


# ── Article 2 charts ───────────────────────────────────────────────────────────

def chart_speaker_types_by_year():
    try:
        stance = pd.read_csv(DATA / 'stance_results.csv')
    except FileNotFoundError:
        print("  [skip] stance_results.csv not found")
        return

    stance['year'] = stance['article_id'].astype(str).str[:4].astype(int)
    pt = stance.groupby(['year','type_final']).size().unstack(fill_value=0)
    types = [t for t in ['M1','M2','M3','M4','M5','M6'] if t in pt.columns]
    pt = pt[types]

    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(len(pt))
    for t in types:
        ax.bar(pt.index, pt[t], bottom=bottom, label=t,
               color=TYPE_COLORS.get(t, PALETTE[0]), alpha=0.9)
        bottom += pt[t].values
    ax.set_xlabel('Year')
    ax.set_ylabel('Speaker mentions')
    ax.set_title('Speaker Types by Year — ČT Climate Coverage', fontweight='bold')
    ax.legend(title='Type', loc='upper left', ncol=2)
    ax.set_xticks(pt.index)
    ax.tick_params(axis='x', rotation=45)
    save(fig, OUT5 / f'P2.1_speaker_types_by_year{SUFFIX}.png')


def chart_gender_by_type():
    try:
        spk = pd.read_csv(DATA / 'speakers_final.csv')
    except FileNotFoundError:
        print("  [skip] speakers_final.csv not found")
        return

    gender_pct = {}
    for t, grp in spk.groupby('type_final'):
        total = len(grp)
        female = ((grp['gender_final'] == 'F') | (grp['gender_final'] == 'F?')).sum()
        gender_pct[t] = female / total * 100 if total else 0

    types = sorted(gender_pct.keys())
    vals  = [gender_pct[t] for t in types]
    colors = [COLORS['primary'] if v < 30 else COLORS['secondary'] for v in vals]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(types, vals, color=colors, edgecolor='white')
    ax.axhline(40, color=COLORS['neutral'], linestyle='--', alpha=0.6, label='40% parity threshold')
    ax.set_ylabel('% female speakers')
    ax.set_title('Female Speaker Share by Type', fontweight='bold')
    ax.set_ylim(0, 55)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1, f'{val:.1f}%',
                ha='center', fontsize=10)
    ax.legend()
    save(fig, OUT5 / f'P2.2_gender_by_type{SUFFIX}.png')


# ── Article 3 charts ───────────────────────────────────────────────────────────

def chart_stance_overall():
    counts = {'S0':2799,'S1':48,'S2':77,'S3':148,'S4':95,'S5':7,'S6':1728}
    labels = [STANCE_LABELS[k] for k in counts]
    values = list(counts.values())
    colors = [STANCE_COLORS[k] for k in counts]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, edgecolor='white')
    ax.set_ylabel('Segments')
    ax.set_title('Stance Distribution — All Classified Segments', fontweight='bold')
    ax.tick_params(axis='x', rotation=20)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f'{val:,}', ha='center', fontsize=9)
    save(fig, OUT5 / f'P3.4_stance_overall{SUFFIX}.png')


def chart_urgency_trend():
    try:
        freq = pd.read_csv(DATA / 'frequency_combined.csv')
    except FileNotFoundError:
        print("  [skip] frequency_combined.csv not found")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(freq['year'], freq['urgency_crisis_per100'], 'o-', color=COLORS['primary'],
            label='Crisis language', linewidth=2.5)
    ax.plot(freq['year'], freq['urgency_action_per100'], 's--', color=COLORS['positive'],
            label='Action calls', linewidth=2.5)
    ax.fill_between(freq['year'], freq['urgency_action_per100'], freq['urgency_crisis_per100'],
                    alpha=0.12, color=COLORS['primary'])
    ax.set_xlabel('Year')
    ax.set_ylabel('Occurrences per 100 documents')
    ax.set_title('Urgency Without Agency: Crisis Language vs Action Calls', fontweight='bold')
    ax.legend()
    ax.set_xticks(freq['year'])
    ax.tick_params(axis='x', rotation=45)
    save(fig, OUT5 / f'P3.1_urgency_trend{SUFFIX}.png')


def chart_topic_categories_by_year():
    try:
        topics = pd.read_csv(DATA / 'topics_nmf_20.csv')
        labels = pd.read_csv(DATA / 'topic_labels_nmf20.csv')
    except FileNotFoundError:
        print("  [skip] topic data not found")
        return

    # dominant topic per doc
    topic_cols = [c for c in topics.columns if c.startswith('T')]
    topics['dominant'] = topics[topic_cols].idxmax(axis=1)
    topics['year'] = topics['article_id'].astype(str).str[:4].astype(int)

    cat_map = labels.set_index('topic')['category'].to_dict()
    topics['category'] = topics['dominant'].map(cat_map).fillna('OTHER')

    cat_order = ['SCIENCE','MITIGATION','ADAPTATION','CZ POLICY','EU POLICY',
                 'US POLICY','INTERNATIONAL','GEOPOLITICS','ACTIVISM','OTHER']
    cat_colors = dict(zip(cat_order, PALETTE[:len(cat_order)]))

    pt = topics.groupby(['year','category']).size().unstack(fill_value=0)
    pt_pct = pt.div(pt.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(pt_pct))
    for cat in cat_order:
        if cat not in pt_pct.columns:
            continue
        ax.bar(pt_pct.index, pt_pct[cat], bottom=bottom,
               label=cat, color=cat_colors[cat], alpha=0.9)
        bottom += pt_pct[cat].values

    ax.set_xlabel('Year')
    ax.set_ylabel('% of documents')
    ax.set_title('Topic Categories by Year (NMF k=20)', fontweight='bold')
    ax.legend(loc='upper left', ncol=2, fontsize=9)
    ax.set_ylim(0, 105)
    ax.set_xticks(pt_pct.index)
    ax.tick_params(axis='x', rotation=45)
    save(fig, OUT5 / f'P3.8_topic_categories{SUFFIX}.png')


def chart_tj_radar():
    from viz_style import COLORS
    criteria = ['De-polarization', 'Urgency &\nsolution framing', 'Just\ntransformation']
    values   = [7.0, 3.0, 1.5]
    values  += values[:1]

    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True),
                           facecolor=COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    ax.plot(angles, values, 'o-', linewidth=2.5, color=COLORS['primary'])
    ax.fill(angles, values, alpha=0.20, color=COLORS['primary'])
    ax.set_ylim(0, 10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria, size=11, fontweight='bold', color=COLORS['text'])
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2','4','6','8','10'], size=8, color=COLORS['neutral'])
    ax.yaxis.grid(True, color=COLORS['grid'], linewidth=0.8)
    ax.xaxis.grid(True, color=COLORS['grid'], linewidth=0.8)
    ax.spines['polar'].set_color(COLORS['grid'])
    ax.axhline(y=5, color=COLORS['neutral'], linestyle='--', alpha=0.35, linewidth=1)
    ax.set_title('ČT Climate Coverage\nTransformative Journalism Score',
                 fontsize=13, fontweight='bold', pad=20, color=COLORS['text'])
    for angle, val, label in zip(angles[:-1], values[:-1], criteria):
        ax.annotate(f'{val:.0f}/10', xy=(angle, val), xytext=(angle, val + 0.9),
                    ha='center', fontsize=11, color=COLORS['primary'], fontweight='bold')
    save(fig, OUT5 / f'P3.9_tj_radar{SUFFIX}.png')


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    print("Article 1 charts")
    chart_subcorpus_sizes()
    chart_income_groups()
    chart_monthly_timeseries()

    print("\nArticle 2 charts")
    chart_speaker_types_by_year()
    chart_gender_by_type()

    print("\nArticle 3 charts")
    chart_stance_overall()
    chart_urgency_trend()
    chart_topic_categories_by_year()
    chart_tj_radar()

    print(f"\nDone. Restyled charts saved to visualizations/article5/")


if __name__ == "__main__":
    main()
