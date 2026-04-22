"""P3.3 — Stance validation sample.

Draws a stratified random sample of 150 classified segments (25 per stance category,
or fewer if category has <25 items). Exports for manual review.

Usage:
  python stance_validation.py

Output:
  data/stance_validation_sample.csv  — fill in 'correct_stance' and 'notes' columns
"""

from pathlib import Path
import pandas as pd

REPO    = Path(__file__).parent.parent.parent
RESULTS = REPO / "data/stance_results.csv"
OUT     = REPO / "data/stance_validation_sample.csv"

TARGET_PER_STANCE = 25
STANCES = ['S1','S2','S3','S4','S5','S6','S0','SKIP']


def main():
    df = pd.read_csv(RESULTS)
    print(f"Loaded {len(df):,} classified segments")
    print(f"\nStance distribution:")
    print(df['stance'].value_counts().to_string())

    frames = []
    for s in STANCES:
        sub = df[df['stance'] == s]
        n = min(TARGET_PER_STANCE, len(sub))
        if n == 0:
            continue
        samp = sub.sample(n, random_state=42)
        frames.append(samp)

    sample = pd.concat(frames).sample(frac=1, random_state=42).reset_index(drop=True)
    sample = sample[['article_id','name','role_raw','type_final','gender_final',
                     'stance','conf','segment']]
    sample['correct_stance'] = ''   # reviewer fills in: S0-S6, SKIP, or = (agree)
    sample['notes'] = ''

    sample.to_csv(OUT, index=True, index_label='id')
    print(f"\nValidation sample: {len(sample)} rows → {OUT}")
    print(sample['stance'].value_counts().to_string())
    print("\nInstructions:")
    print("  correct_stance: fill with S0–S6, SKIP, or '=' if you agree with the LLM")
    print("  notes: any observations about why the classification is right/wrong")


if __name__ == "__main__":
    main()
