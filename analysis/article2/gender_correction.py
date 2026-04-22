"""P2.5 — Gender correction pass on speakers_final.csv.

Fixes three known failure modes of the suffix-only rule:
  1. Foreign male names ending in -a/-e (Joe, Charlie, George…)
  2. -ů surnames resolved by first name (Zuzana → F, Jaromír → M)
  3. Obvious false-positive extractions kept as '?' (no change needed)

Overwrites speakers_final.csv in place (adds 'gender_final' column).
"""

from pathlib import Path
import pandas as pd

REPO = Path(__file__).parent.parent.parent
FINAL = REPO / "data/speakers_final.csv"

# Known male first names that end in -a or -e and trip the suffix rule
MALE_FIRST = {
    # English
    'joe','charlie','george','bruce','steve','jude','jesse','willie','willie',
    'mike','spike','lance','blake','jake','wade','kyle','clyde','wayne',
    # French / Romance
    'claude','stephane','francoise','guillaume','pierre','alexandre','baptiste',
    'jerome','maxime','antoine','philippe','christophe','dominique',
    # Italian / Spanish
    'luca','dante','andrea','mattia','nicola','simone','samuele','gabriele',
    # Finnish / Nordic
    'jukka','mika','pekka','vesa','timo','risto','ville','eero',
    # Czech / Slovak male names ending in -a or -e
    'ota','saša','miša','honza','ondra','láďa','fanda','jirka','franta',
    'zdeněk','rené','josé',
    # Other
    'bernie','leslie','jamie','lee','kim','jan',   # jan = male in Czech!
}

# First-name based resolution for -ů surnames (gender=='?')
FEMALE_FIRST_CZ = {
    'zuzana','miroslava','jana','marie','eva','anna','petra','lucie','tereza',
    'kateřina','monika','martina','lenka','alena','hana','ivana','dana',
    'markéta','veronika','michaela','barbora','jitka','věra','olga','helena',
}


def correct_gender(row: pd.Series) -> str:
    fn = row['firstname'].lower()
    g  = row['gender']

    if g == 'F?':
        if fn in MALE_FIRST:
            return 'M'
        return 'F'          # Czech/other female name ending in -a/-e → confirm F

    if g == '?':            # -ů surname: decide by first name
        if fn in FEMALE_FIRST_CZ:
            return 'F'
        return 'M'          # default: male (Matyáš, Jaromír, Radim…)

    return g                # F and M pass through unchanged


def main():
    df = pd.read_csv(FINAL)
    df['gender_final'] = df.apply(correct_gender, axis=1)

    print("=== Gender correction summary ===")
    before = df['gender'].value_counts()
    after  = df['gender_final'].value_counts()
    print(f"{'':12} {'before':>8} {'after':>8}")
    for g in ['F','F?','M','?']:
        print(f"  {g:10} {before.get(g,0):>8} {after.get(g,0):>8}")

    # Check what changed
    changed = df[df['gender'] != df['gender_final']][['name','firstname','surname','gender','gender_final']]
    print(f"\nChanged: {len(changed)} rows")
    print(changed.to_string(index=False))

    df.to_csv(FINAL, index=False)
    print(f"\nSaved → {FINAL}")


if __name__ == "__main__":
    main()
