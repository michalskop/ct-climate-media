"""P1.6 — Subcorpus size comparison table."""

import pandas as pd

WHOLE_CORPUS = 531_593

SUBCORPORA = {
    "Climate v4":        ("climate", 2_914),
    "Social/poverty":    ("social",  4_853),
    "Motorist":          ("motor",   63_496),
    "COVID":             ("covid",   33_284),
    "Terrorism":         ("terror",  3_379),
}

rows = []
for name, (tag, n) in SUBCORPORA.items():
    rows.append({
        "Subcorpus":   name,
        "Documents":   n,
        "% of corpus": round(n / WHOLE_CORPUS * 100, 2),
    })

df = pd.DataFrame(rows).sort_values("Documents", ascending=False)
df["Documents"] = df["Documents"].apply(lambda x: f"{x:,}")

print("Subcorpus size comparison — Czech Television news corpus (Jan 2012 – Apr 2022)")
print(f"Whole corpus: {WHOLE_CORPUS:,} documents\n")
print(df.to_string(index=False))
print(f"\nSource: data_check.py verified row counts + Newton Media Archive metadata.")
