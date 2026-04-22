"""P3.14/P3.15 — Urgency, mitigation, and planetary limits keyword frequency analysis.

Counts keyword group occurrences per year in the climate subcorpus.
Uses simple substring matching (case-insensitive, diacritic-sensitive).

Outputs:
  data/frequency_urgency.csv      — urgency terms by year (absolute + per-doc)
  data/frequency_mitigation.csv   — mitigation/fossil/net-zero terms by year
  data/frequency_combined.csv     — all groups in one wide table
  visualizations/article3/P3.1_urgency_trend.png
  visualizations/article3/P3.2_mitigation_trend.png
"""

import re
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

REPO   = Path(__file__).parent.parent.parent
BASE   = REPO / "Climate change TV/BackupClimateChangeData/2.data_transformations/data"
CORPUS = BASE / "climate_sub_corpus/climate_corpus_v4_2023.csv"
OUT    = REPO / "data"
VIZ    = REPO / "visualizations/article3"
VIZ.mkdir(parents=True, exist_ok=True)

# ── Keyword groups ─────────────────────────────────────────────────────────────
KEYWORD_GROUPS = {

    # Urgency / crisis framing
    "urgency_crisis": [
        "krize", "klimatická krize", "klimatický kolaps", "klimatický rozvrat",
        "naléhavost", "naléhavý", "katastrofa", "katastrofický",
        "hrozba", "hrozí", "alarm", "alarmující", "nebezpeč",
        "tipping point", "bod zlomu", "nevratný", "nevratné",
    ],
    "urgency_action": [
        "okamžitě", "okamžitá akce", "bezodkladně", "nutně jednat",
        "musíme jednat", "čas běží", "zbývá málo času", "poslední šance",
    ],

    # Mitigation — decarbonisation
    "mitigation_decarb": [
        "dekarbonizace", "uhlíková neutralita", "klimatická neutralita",
        "uhlíkově neutrální", "nulové emise", "čistá nula", "net zero",
        "snížení emisí", "redukce emisí", "emise CO2", "emise skleníkových",
    ],
    "mitigation_renewables": [
        "obnovitelná energie", "obnovitelné zdroje", "solární", "větrná energie",
        "větrné elektrárny", "fotovoltaika", "fotovoltaický",
        "tepelná čerpadla", "geotermální",
    ],
    "mitigation_nuclear": [
        "jaderná energie", "jaderná elektrárna", "atomová elektrárna",
        "jaderný reaktor", "nová jaderná", "jaderný blok",
    ],

    # Fossil fuels
    "fossil_fuels": [
        "fosilní paliva", "uhlí", "uhelná elektrárna", "hnědé uhlí",
        "ropa", "zemní plyn", "spalování fosilních", "odchod od uhlí",
        "konec uhlí", "uhlíková daň",
    ],

    # EU Green Deal / policy
    "eu_green_deal": [
        "zelená dohoda", "green deal", "Fit for 55", "fit for 55",
        "evropská taxonomie", "emisní povolenky", "ETS", "EU ETS",
        "Green Deal", "zelený úděl",
    ],

    # Planetary / ecological limits
    "planetary_limits": [
        "planetární hranice", "ekosystém", "biodiverzita", "vymírání druhů",
        "šesté vymírání", "ztráta biodiverzity", "ekologická krize",
        "oceán", "kyselost oceánů", "tání ledovců", "permafrost",
        "Arktida", "Antarktida", "ledovec",
    ],

    # Adaptation
    "adaptation": [
        "adaptace", "adaptační", "přizpůsobení se", "odolnost vůči",
        "povodně", "sucho", "vlna veder", "extrémní počasí",
        "klimatické uprchlíky", "klimatická migrace",
    ],

    # Justice / social framing
    "climate_justice": [
        "klimatická spravedlnost", "climate justice", "spravedlivá transformace",
        "just transition", "zranitelné země", "rozvojové země",
        "globální jih", "klimatičtí uprchlíci",
    ],
}


def count_keywords(text: str, keywords: list[str]) -> int:
    if not isinstance(text, str):
        return 0
    text_l = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_l)


def run_frequency_analysis(corpus: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, doc in corpus.iterrows():
        year = int(str(doc["article_id"])[:4])
        row = {"article_id": doc["article_id"], "year": year}
        for group, kws in KEYWORD_GROUPS.items():
            row[group] = count_keywords(doc["text"], kws)
        rows.append(row)
    return pd.DataFrame(rows)


def make_charts(yearly: pd.DataFrame, doc_counts: pd.Series):
    # ── Chart 1: Urgency trends ────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    for col, label, color in [
        ("urgency_crisis", "Crisis/catastrophe framing", "#C44E52"),
        ("urgency_action",  "Urgent action calls",       "#DD8452"),
        ("adaptation",      "Adaptation coverage",       "#4C72B0"),
    ]:
        vals = yearly[col] / doc_counts * 100   # per 100 docs
        ax.plot(yearly.index, vals, marker='o', linewidth=2, label=label, color=color)
    ax.set_xlabel("Year"); ax.set_ylabel("Keyword hits per 100 docs")
    ax.set_title("Urgency framing in ČT climate coverage (2012–2022)", fontweight='bold')
    ax.legend(fontsize=9); ax.set_xticks(yearly.index)
    plt.tight_layout()
    plt.savefig(VIZ / "P3.1_urgency_trend.png", dpi=150, bbox_inches='tight')
    plt.close()

    # ── Chart 2: Mitigation vs fossil vs EU policy ─────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    for col, label, color in [
        ("mitigation_decarb",     "Decarbonisation",      "#55A868"),
        ("mitigation_renewables", "Renewables",           "#4C72B0"),
        ("mitigation_nuclear",    "Nuclear energy",       "#8172B2"),
        ("fossil_fuels",          "Fossil fuels",         "#C44E52"),
        ("eu_green_deal",         "EU Green Deal",        "#CCB974"),
    ]:
        vals = yearly[col] / doc_counts * 100
        ax.plot(yearly.index, vals, marker='o', linewidth=2, label=label, color=color)
    ax.set_xlabel("Year"); ax.set_ylabel("Keyword hits per 100 docs")
    ax.set_title("Mitigation discourse in ČT climate coverage (2012–2022)", fontweight='bold')
    ax.legend(fontsize=9); ax.set_xticks(yearly.index)
    plt.tight_layout()
    plt.savefig(VIZ / "P3.2_mitigation_trend.png", dpi=150, bbox_inches='tight')
    plt.close()

    print("Charts saved.")


def main():
    print("Loading corpus…")
    corpus = pd.read_csv(CORPUS, sep=";", low_memory=False)
    print(f"  {len(corpus):,} documents")

    print("Counting keyword groups…")
    df = run_frequency_analysis(corpus)

    # Per-year aggregation
    group_cols = list(KEYWORD_GROUPS.keys())
    yearly = df.groupby("year")[group_cols].sum()
    doc_counts = df.groupby("year").size()

    # Save outputs
    df.to_csv(OUT / "frequency_all_docs.csv", index=False)

    urgency_cols = ["urgency_crisis","urgency_action","adaptation","climate_justice"]
    mitigation_cols = ["mitigation_decarb","mitigation_renewables","mitigation_nuclear",
                       "fossil_fuels","eu_green_deal","planetary_limits"]

    yearly_out = yearly.copy()
    yearly_out["n_docs"] = doc_counts
    for col in group_cols:
        yearly_out[f"{col}_per100"] = (yearly[col] / doc_counts * 100).round(1)
    yearly_out.to_csv(OUT / "frequency_combined.csv")

    print("\n=== Yearly totals (absolute) ===")
    print(yearly[urgency_cols + mitigation_cols].to_string())

    print("\n=== Per 100 docs ===")
    per100 = yearly[group_cols].div(doc_counts, axis=0) * 100
    print(per100[urgency_cols + mitigation_cols].round(1).to_string())

    make_charts(yearly, doc_counts)
    print(f"\nSaved to {OUT} and {VIZ}")


if __name__ == "__main__":
    main()
