"""P1.8 / P1.9 — Country detection on corpus using extended Czech lookup.

Approach: three-pass detection per document (all word-boundary safe):
  1. Tokenize text → word dict lookup  (single-word literals, O(words))
  2. Combined alternation regex         (multi-word phrase literals)
  3. Combined stem prefix regex         (adjective/inflected forms via stems)

Usage:
  python country_detection.py --corpus climate  # climate subcorpus v4 (P1.9)
  python country_detection.py --corpus social
  python country_detection.py --corpus motor
  python country_detection.py --corpus covid
  python country_detection.py --corpus terror

Outputs:
  data/country_counts_{corpus}.csv   — (year, Code, income, n_docs, n_mentions)
"""

import argparse
import re
import time
from pathlib import Path

import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO = Path(__file__).parent.parent.parent
DATA_BASE = REPO / "Climate change TV" / "BackupClimateChangeData"
CORPUS_BASE = DATA_BASE / "2.data_transformations" / "data"
WB_BASE = DATA_BASE / "4.data_analysis" / "world_data"

CORPORA = {
    "climate": CORPUS_BASE / "climate_sub_corpus" / "climate_corpus_v4_2023.csv",
    "social":  CORPUS_BASE / "sic_sub_corpus"     / "sic_articles_truncated.csv",
    "motor":   CORPUS_BASE / "motor_sub_corpus"   / "motor_articles_v2_truncated.csv",
    "covid":   CORPUS_BASE / "covid_sub_corpus"   / "covid_articles_v2_truncated.csv",
    "terror":  CORPUS_BASE / "sic_sub_corpus"     / "execution_articles_truncated.csv",
}

LOOKUP_PATH   = Path(__file__).parent / "country_variants.csv"
WB_CLASS_PATH = WB_BASE / "WB_Class2021.csv"
OUT_DIR       = REPO / "data"

_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)

# ── Lookup compilation ─────────────────────────────────────────────────────────

def compile_lookup():
    lk = pd.read_csv(LOOKUP_PATH, sep=";")
    lk = lk[lk["Code"].notna()]

    stems_df   = lk[lk["match_type"] == "stem"]
    literals   = lk[lk["match_type"] == "literal"]
    single_lit = literals[~literals["token"].str.contains(" ")]
    multi_lit  = literals[literals["token"].str.contains(" ")]

    # 1. Word dict: {word_lower → set of codes}
    word_dict: dict[str, set] = {}
    for _, row in single_lit.iterrows():
        word_dict.setdefault(row["token"].lower(), set()).add(row["Code"])

    # 2. Multi-word phrase regex + map
    multi_sorted = sorted(multi_lit["token"].tolist(), key=len, reverse=True)
    phrase_map: dict[str, str] = {r["token"].lower(): r["Code"] for _, r in multi_lit.iterrows()}
    multi_pat = re.compile(
        r"\b(?:" + "|".join(re.escape(p) for p in multi_sorted) + r")\b",
        re.IGNORECASE | re.UNICODE,
    )

    # 3. Stem regex + map (longest stems first to avoid partial matches)
    stems_sorted = sorted(stems_df["token"].tolist(), key=len, reverse=True)
    stem_map: dict[str, str] = {r["token"]: r["Code"] for _, r in stems_df.iterrows()}
    stem_pat = re.compile(
        r"\b(" + "|".join(re.escape(s) for s in stems_sorted) + r")\w*\b",
        re.IGNORECASE | re.UNICODE,
    )

    return word_dict, multi_pat, phrase_map, stem_pat, stem_map


def detect_countries(text: str, word_dict, multi_pat, phrase_map, stem_pat, stem_map) -> set:
    found: set = set()
    text_lower = text.lower()
    # Pass 1: single-word literals
    for word in _WORD_RE.findall(text_lower):
        if word in word_dict:
            found.update(word_dict[word])
    # Pass 2: multi-word phrases
    for m in multi_pat.finditer(text):
        code = phrase_map.get(m.group().lower())
        if code:
            found.add(code)
    # Pass 3: adjective stems
    for m in stem_pat.finditer(text):
        code = stem_map.get(m.group(1).lower())
        if code:
            found.add(code)
    return found

# ── Corpus loading ─────────────────────────────────────────────────────────────

def load_corpus(name: str) -> pd.DataFrame:
    path = CORPORA[name]
    want = {"article_id", "text", "date", "year"}
    for sep in (",", ";"):
        try:
            df = pd.read_csv(path, sep=sep,
                             usecols=lambda c: c in want,
                             low_memory=False, on_bad_lines="skip")
            if "text" in df.columns and len(df.columns) > 1:
                break
        except Exception:
            continue
    if "year" not in df.columns:
        if "date" in df.columns:
            df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year
        else:
            df["year"] = df["article_id"].str[:4].astype(int, errors="ignore")
    df = df.dropna(subset=["text", "year"])
    df["year"] = df["year"].astype(int)
    return df[["article_id", "text", "year"]]

# ── Main ───────────────────────────────────────────────────────────────────────

def run(corpus_name: str) -> pd.DataFrame:
    print(f"Loading corpus: {corpus_name}")
    df = load_corpus(corpus_name)
    print(f"  {len(df):,} docs, {df['year'].min()}–{df['year'].max()}")

    lk_args = compile_lookup()
    print(f"  Lookup compiled")

    wb = pd.read_csv(WB_CLASS_PATH, sep=";")[["Code", "Income group"]].dropna()
    income_map = dict(zip(wb["Code"], wb["Income group"]))

    t0 = time.time()
    rows = []
    for i, (_, doc) in enumerate(df.iterrows()):
        if i % 5_000 == 0:
            print(f"  {i:,}/{len(df):,}", end="\r")
        for code in detect_countries(doc["text"], *lk_args):
            rows.append({
                "article_id": doc["article_id"],
                "year":       doc["year"],
                "Code":       code,
                "income":     income_map.get(code, "Unknown"),
            })

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s — {len(rows):,} country-mention rows")

    mentions = pd.DataFrame(rows)
    agg = (mentions.groupby(["year", "Code", "income"])
                   .agg(n_docs=("article_id", "nunique"),
                        n_mentions=("article_id", "count"))
                   .reset_index()
                   .sort_values(["year", "n_docs"], ascending=[True, False]))
    return agg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", choices=list(CORPORA.keys()), default="climate")
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    result = run(args.corpus)

    out_path = OUT_DIR / f"country_counts_{args.corpus}.csv"
    result.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    print(result.groupby("Code")["n_docs"].sum().sort_values(ascending=False).head(20))


if __name__ == "__main__":
    main()
