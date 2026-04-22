"""P3.18/P3.19 — Transformative Journalism (TJ) assessment.

Maps empirical findings from Phases 2 & 3 onto three TJ criteria:
  1. De-polarization — does ČT avoid false balance and fringe amplification?
  2. Urgency & solution framing — does ČT communicate urgency AND solutions?
  3. Just transformation — are marginalized voices and climate justice present?

Produces a structured assessment table and a summary radar chart.

Output:
  data/tj_assessment.csv
  visualizations/article3/P3.9_tj_radar.png
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

REPO = Path(__file__).parent.parent.parent
VIZ  = REPO / 'visualizations/article3'
VIZ.mkdir(parents=True, exist_ok=True)

# ── Indicator data (from earlier analyses) ────────────────────────────────────
INDICATORS = [
    # De-polarization criterion
    {
        'criterion':    'De-polarization',
        'indicator':    'S1 denial rate (all classified segments)',
        'value':        '1.0%',
        'value_num':     1.0,
        'benchmark':    '<5% = good',
        'verdict':      'MEETS',
        'finding':      '48 S1 (denier) segments out of 4,902 classified. No scientist (M3) ever classified as S1.',
    },
    {
        'criterion':    'De-polarization',
        'indicator':    'False balance rate (S1/S2/S3 + S6 in same article)',
        'value':        '10.2%',
        'value_num':    10.2,
        'benchmark':    '<15% = acceptable',
        'verdict':      'PARTIALLY MEETS',
        'finding':      '121 of 1,189 articles with non-neutral stances show false balance. '
                       'Concentrated in M6 politicians as the problematic voice.',
    },
    {
        'criterion':    'De-polarization',
        'indicator':    'M4 pseudoscientist share of all mentions',
        'value':        '0.2%',
        'value_num':     0.2,
        'benchmark':    '<1% = good',
        'verdict':      'MEETS',
        'finding':      'Only 87 M4 mentions across 10 years. ČT does not platform alternative-science voices.',
    },

    # Urgency & solution framing criterion
    {
        'criterion':    'Urgency & solution framing',
        'indicator':    'Action call / crisis framing ratio',
        'value':        '0.09–0.26',
        'value_num':     0.13,
        'benchmark':    '>0.4 = good',
        'verdict':      'DOES NOT MEET',
        'finding':      'Crisis language is common (40–104 per 100 docs) but explicit action calls '
                       'are rare (5–16 per 100 docs). Ratio declining over time — crisis without agency.',
    },
    {
        'criterion':    'Urgency & solution framing',
        'indicator':    'Neutral/procedural stance share (S0)',
        'value':        '57.1%',
        'value_num':    57.1,
        'benchmark':    '<40% = good',
        'verdict':      'DOES NOT MEET',
        'finding':      '2,799 of 4,902 classified segments express no stance on climate action. '
                       'Climate treated as information item, not as crisis requiring action.',
    },
    {
        'criterion':    'Urgency & solution framing',
        'indicator':    'Mitigation vs adaptation topic balance',
        'value':        '18% vs 15%',
        'value_num':    55.0,   # mitigation as % of mit+adap
        'benchmark':    'Balanced = good; mitigation-dominated = meets',
        'verdict':      'PARTIALLY MEETS',
        'finding':      'Mitigation (18%) and adaptation (15%) topics roughly comparable. '
                       '2022 spike: geopolitics (Ukraine/energy) crowded out both frames.',
    },
    {
        'criterion':    'Urgency & solution framing',
        'indicator':    'EU Green Deal coverage growth',
        'value':        '1.0 → 25.4 per 100 docs',
        'value_num':    25.4,
        'benchmark':    'Growth = positive signal',
        'verdict':      'PARTIALLY MEETS',
        'finding':      'EU Green Deal language grew 25× post-2020 — policy solutions are entering coverage. '
                       'But driven by EU events, not ČT editorial initiative.',
    },

    # Just transformation criterion
    {
        'criterion':    'Just transformation',
        'indicator':    'Citizen (M2) share of non-journalist mentions',
        'value':        '2.0%',
        'value_num':     2.0,
        'benchmark':    '>10% = good',
        'verdict':      'DOES NOT MEET',
        'finding':      'Citizens produce only 1,143 of 56,613 mentions. '
                       'Coverage is dominated by élites (M6 politicians: 22.6%).',
    },
    {
        'criterion':    'Just transformation',
        'indicator':    'Climate justice keyword rate',
        'value':        '<2 per 100 docs',
        'value_num':     1.0,
        'benchmark':    '>10 per 100 docs = good',
        'verdict':      'DOES NOT MEET',
        'finding':      'Climate justice, just transition, and global south framing virtually absent '
                       'throughout the entire 10-year period.',
    },
    {
        'criterion':    'Just transformation',
        'indicator':    'Female speaker share',
        'value':        '27.6%',
        'value_num':    27.6,
        'benchmark':    '>40% = good',
        'verdict':      'DOES NOT MEET',
        'finding':      'Female speakers: 39.4% among journalists but only 10.7–12.6% '
                       'among scientists, stakeholders, and politicians.',
    },
    {
        'criterion':    'Just transformation',
        'indicator':    'Global South country coverage share',
        'value':        '8.5%',
        'value_num':     8.5,
        'benchmark':    '>15% = good',
        'verdict':      'DOES NOT MEET',
        'finding':      'Low-income countries = 2.5%, lower-middle = 6.0% of all country mentions. '
                       '101 countries (inc. most climate-vulnerable) appear in <10 docs over 10 years.',
    },
]

TJ_SCORES = {
    'De-polarization': 2,           # 2/3 meet; scaled 0–10 → ~7
    'Urgency & solution framing': 1, # 1/4 fully meet; → ~3
    'Just transformation': 0,       # 0/4 meet; → 1
}
TJ_SCORE_10 = {
    'De-polarization': 7.0,
    'Urgency & solution framing': 3.0,
    'Just transformation': 1.5,
}


def main():
    df = pd.DataFrame(INDICATORS)
    df.to_csv(REPO / 'data/tj_assessment.csv', index=False)
    print("=== TJ Assessment Summary ===\n")
    for crit in ['De-polarization','Urgency & solution framing','Just transformation']:
        rows = df[df['criterion']==crit]
        print(f"\n{'─'*60}")
        print(f"CRITERION: {crit}")
        for _, r in rows.iterrows():
            print(f"  [{r['verdict']:20}] {r['indicator']}: {r['value']}")
            print(f"    → {r['finding']}")

    # ── Radar chart ────────────────────────────────────────────────────────────
    criteria = list(TJ_SCORE_10.keys())
    values   = list(TJ_SCORE_10.values())
    values  += values[:1]   # close the polygon

    angles = np.linspace(0, 2 * np.pi, len(criteria), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, 'o-', linewidth=2, color='#C44E52')
    ax.fill(angles, values, alpha=0.25, color='#C44E52')
    ax.set_ylim(0, 10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria, size=11, fontweight='bold')
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2','4','6','8','10'], size=8)
    ax.axhline(y=5, color='gray', linestyle='--', alpha=0.4)
    ax.set_title('ČT Climate Coverage\nTransformative Journalism Score',
                 fontsize=13, fontweight='bold', pad=20)
    for angle, val, label in zip(angles[:-1], values[:-1], criteria):
        ax.annotate(f'{val:.0f}/10', xy=(angle, val), xytext=(angle, val+0.8),
                    ha='center', fontsize=10, color='#C44E52', fontweight='bold')
    plt.tight_layout()
    plt.savefig(VIZ / 'P3.9_tj_radar.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n\nTJ Scores (0–10 scale):")
    for c, s in TJ_SCORE_10.items():
        print(f"  {c:35} {s:.1f}/10")
    print(f"\nSaved tj_assessment.csv and P3.9_tj_radar.png")


if __name__ == "__main__":
    main()
