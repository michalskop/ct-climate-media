"""P0.4 — Verify all corpus files load correctly and report row counts."""

import os
import sys

import pandas as pd

BASE = os.path.join(
    os.path.dirname(__file__),
    "Climate change TV",
    "BackupClimateChangeData",
    "2.data_transformations",
    "data",
)

CORPORA = {
    "climate_v4":       os.path.join(BASE, "climate_sub_corpus", "climate_corpus_v4.csv"),
    "climate_v4_dup":   os.path.join(BASE, "..", "climate_corpus_v4.csv"),
    "climate_str_v2":   os.path.join(BASE, "climate_sub_corpus", "climate_articles_string_v2.csv"),
    "climate_v4_2023":  os.path.join(BASE, "climate_sub_corpus", "climate_corpus_v4_2023.csv"),
    "motorist":         os.path.join(BASE, "motor_sub_corpus", "motor_articles_v2_truncated.csv"),
    "covid":            os.path.join(BASE, "covid_sub_corpus", "covid_articles_v2_truncated.csv"),
    "sic_v1":           os.path.join(BASE, "sic_sub_corpus", "sic_articles_truncated.csv"),
    "sic_v2":           os.path.join(BASE, "sic_sub_corpus", "sic_articles_v2_truncated.csv"),
    "sic_labelled":     os.path.join(BASE, "sic_sub_corpus", "sic_corpus_v2_labelled.csv"),
    "execution":        os.path.join(BASE, "sic_sub_corpus", "execution_articles_truncated.csv"),
}

print(f"{'Corpus':<20} {'Rows':>8} {'Cols':>6}  Columns")
print("-" * 80)

ok = 0
missing = 0
errors = 0

for name, path in CORPORA.items():
    path = os.path.normpath(path)
    if not os.path.exists(path):
        print(f"{name:<20} {'MISSING':>8}  {path}")
        missing += 1
        continue
    try:
        df = pd.read_csv(path, nrows=5)
        if len(df.columns) == 1 and ";" in df.columns[0]:
            df = pd.read_csv(path, nrows=5, sep=";")
        total = sum(1 for _ in open(path, encoding="utf-8")) - 1  # fast line count
        cols = ", ".join(df.columns.tolist()[:6])
        if len(df.columns) > 6:
            cols += f" ... (+{len(df.columns)-6} more)"
        print(f"{name:<20} {total:>8,}  {len(df.columns):>4}   {cols}")
        ok += 1
    except Exception as e:
        print(f"{name:<20} {'ERROR':>8}  {e}")
        errors += 1

print("-" * 80)
print(f"OK: {ok}  |  Missing: {missing}  |  Errors: {errors}")
if missing or errors:
    sys.exit(1)
