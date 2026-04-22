"""P3.1/P3.2 — Extract speaker speech segments and classify stance (S1–S6).

For each unique (non-journalist speaker, article) pair, extracts the speaker's
words from the transcript and classifies stance using Claude Haiku.

Stance categories (Discourses of Climate Delay framework):
  S1 = Denier         — denies climate change or human causation
  S2 = Manipulator    — accepts climate but misleads (false balance, cherry-picks)
  S3 = Delayer        — accepts climate but argues against urgent action
  S4 = Techno-optimist — believes technology will solve it without systemic change
  S5 = Market-only    — believes market mechanisms alone will solve it
  S6 = Informer       — accurately informs about climate science and urgency
  S0 = Neutral/Other  — does not express a clear climate stance (procedural, off-topic)
  SKIP = Cannot classify (too short, garbled, non-climate context)

Outputs:
  data/stance_segments.csv    — extracted speech segments per (speaker, article)
  data/stance_results.csv     — LLM classifications
  data/stance_final.csv       — merged with speaker metadata
"""

import re
import time
import json
import os
import argparse
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

REPO   = Path(__file__).parent.parent.parent
BASE   = REPO / "Climate change TV/BackupClimateChangeData/2.data_transformations/data"
CORPUS = BASE / "climate_sub_corpus/climate_corpus_v4_2023.csv"

SPEAKERS_ALL   = REPO / "data/speakers_all.csv"
SPEAKERS_FINAL = REPO / "data/speakers_final.csv"
OUT_SEGMENTS   = REPO / "data/stance_segments.csv"
OUT_RESULTS    = REPO / "data/stance_results.csv"
OUT_FINAL      = REPO / "data/stance_final.csv"

MODEL      = "claude-haiku-4-5-20251001"
BATCH_SIZE = 20
MAX_WORDS  = 200   # max words of context per speaker turn

# ── Regex to find next speaker boundary ───────────────────────────────────────
U = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]'
L = r'[a-záčďéěíňóřšťúůýž]'
W = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]'
SPEAKER_BOUNDARY = re.compile(
    rf'{U}{L}{{1,11}}\s+{U}{{2,20}}(?:\s{U}{{2,15}})?\s+{L}{W}*',
    re.UNICODE,
)


def extract_segment(text: str, match_start: int, match_end: int) -> str:
    """Return up to MAX_WORDS words of text starting at match_end (the speech)."""
    # Find next speaker boundary after match_end
    next_m = SPEAKER_BOUNDARY.search(text, match_end + 1)
    end = next_m.start() if next_m else len(text)
    segment = text[match_end:end].strip()
    words = segment.split()
    return ' '.join(words[:MAX_WORDS])


def build_segments(corpus_path: Path) -> pd.DataFrame:
    """Extract one speech segment per (speaker, article) for non-M1 speakers."""
    corpus = pd.read_csv(corpus_path, sep=";", low_memory=False)
    all_m  = pd.read_csv(SPEAKERS_ALL)
    final  = pd.read_csv(SPEAKERS_FINAL)

    # Non-journalist speakers only
    non_m1 = final[final['type_final'].isin(['M2','M3','M4','M5','M6'])]
    target  = all_m.merge(non_m1[['name','role_raw','type_final','gender_final']],
                          on=['name','role_raw'], how='inner')
    # One row per (speaker, article)
    pairs = target.drop_duplicates(['name','article_id'])[['name','article_id','role_raw','type_final','gender_final']]

    corpus_dict = corpus.set_index('article_id')['text'].to_dict()

    rows = []
    for _, row in pairs.iterrows():
        text = corpus_dict.get(row['article_id'], '')
        if not isinstance(text, str):
            continue
        # Find the speaker's first occurrence in this article
        fn, sn = row['name'].split(' ', 1)
        pattern = re.compile(
            rf'\b{re.escape(fn)}\s+{re.escape(sn)}\s+{L}{W}*',
            re.UNICODE,
        )
        m = pattern.search(text)
        if not m:
            continue
        segment = extract_segment(text, m.start(), m.end())
        if len(segment.split()) < 5:
            continue
        rows.append({
            'article_id':   row['article_id'],
            'name':         row['name'],
            'role_raw':     row['role_raw'],
            'type_final':   row['type_final'],
            'gender_final': row['gender_final'],
            'segment':      segment,
        })

    return pd.DataFrame(rows)


# ── LLM stance classification ──────────────────────────────────────────────────
SYSTEM_PROMPT = """You classify the stance expressed by a Czech Television news speaker toward climate change and climate action.
Return ONLY a JSON array — no prose, no explanation.

Stance categories:
S1 = Denier         — explicitly denies climate change is real or human-caused
S2 = Manipulator    — accepts climate change but misleads: false balance, cherry-picks uncertainty, downplays urgency
S3 = Delayer        — accepts climate change but argues against urgent action ("too expensive", "not yet", "other countries first")
S4 = Techno-optimist — believes technology alone (nuclear, CCS, geo-engineering) will solve it without systemic change
S5 = Market-only    — believes market mechanisms alone (carbon markets, no regulation) will solve it
S6 = Informer       — accurately describes climate science, impacts, and/or urgency of action
S0 = Neutral/Other  — no clear climate stance (procedural statement, off-topic, administrative)
SKIP = Cannot classify — segment too short, garbled, or clearly not about climate"""

USER_TEMPLATE = """Classify the climate stance of these {n} Czech Television speakers based on their name, role, and speech segment.
For each return {{"id": <id>, "type": "<S0|S1|S2|S3|S4|S5|S6|SKIP>", "conf": <0-3>}}
where conf = 0 (uncertain) to 3 (certain).

{items}"""


def format_items(batch: list[dict]) -> str:
    lines = []
    for i, row in enumerate(batch):
        lines.append(
            f'{i}. Name: {row["name"]} | Role: {row["role_raw"]} | Type: {row["type_final"]}\n'
            f'   Speech: {row["segment"][:400]}'
        )
    return "\n\n".join(lines)


def classify_batch(client: anthropic.Anthropic, batch: list[dict], dry_run: bool) -> list[dict]:
    if dry_run:
        return [{"id": i, "type": "S6", "conf": 1} for i in range(len(batch))]
    prompt = USER_TEMPLATE.format(n=len(batch), items=format_items(batch))
    response = client.messages.create(
        model=MODEL, max_tokens=800, system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:-1])
    return json.loads(text)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--sample", type=int, default=0,
                        help="Classify only first N segments (0 = all)")
    args = parser.parse_args()

    # Step 1: extract segments
    if OUT_SEGMENTS.exists():
        print(f"Loading existing segments from {OUT_SEGMENTS}")
        segments = pd.read_csv(OUT_SEGMENTS)
    else:
        print("Extracting speaker segments from corpus…")
        segments = build_segments(CORPUS)
        segments.to_csv(OUT_SEGMENTS, index=False)
        print(f"  {len(segments):,} segments extracted → {OUT_SEGMENTS}")

    records = segments.to_dict("records")
    if args.sample:
        records = records[:args.sample]

    # Resume: skip already-classified segments
    done_keys: set = set()
    if OUT_RESULTS.exists():
        done = pd.read_csv(OUT_RESULTS)
        done_keys = set(zip(done["article_id"], done["name"]))
        print(f"Resuming — {len(done_keys):,} segments already done")

    records = [r for r in records if (r["article_id"], r["name"]) not in done_keys]
    print(f"Classifying {len(records):,} remaining segments…")

    # Step 2: LLM classification — append results incrementally
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    batches = [records[i:i+BATCH_SIZE] for i in range(0, len(records), BATCH_SIZE)]
    write_header = not OUT_RESULTS.exists()

    for b_idx, batch in enumerate(batches):
        print(f"  Batch {b_idx+1}/{len(batches)} ({len(batch)} items)…", end=" ", flush=True)
        rows = []
        try:
            raw = classify_batch(client, batch, args.dry_run)
            for item in raw:
                idx = item["id"]
                rows.append({
                    "article_id":   batch[idx]["article_id"],
                    "name":         batch[idx]["name"],
                    "role_raw":     batch[idx]["role_raw"],
                    "type_final":   batch[idx]["type_final"],
                    "gender_final": batch[idx]["gender_final"],
                    "stance":       item["type"],
                    "conf":         item.get("conf", -1),
                    "segment":      batch[idx]["segment"],
                })
            print("ok")
        except Exception as e:
            print(f"ERROR: {e}")
            for row in batch:
                rows.append({**{k: row[k] for k in ['article_id','name','role_raw','type_final','gender_final','segment']},
                             "stance": "?", "conf": -1})
        # Append to CSV immediately so progress is saved
        pd.DataFrame(rows).to_csv(OUT_RESULTS, mode='a', header=write_header, index=False)
        write_header = False
        if not args.dry_run and b_idx < len(batches) - 1:
            time.sleep(0.5)

    results_df = pd.read_csv(OUT_RESULTS)
    print(f"\nResults: {len(results_df):,} rows → {OUT_RESULTS}")
    print(results_df["stance"].value_counts().to_string())

    # Step 3: merge and save final
    # For speakers appearing in multiple docs, aggregate stance
    stance_map = (results_df[results_df["stance"] != "SKIP"]
                  .groupby(["name","role_raw"])
                  .agg(
                      stance_primary=("stance", lambda x: x.value_counts().index[0]),
                      stance_docs=("article_id", "nunique"),
                      conf_mean=("conf", "mean"),
                  ).reset_index())
    final = pd.read_csv(SPEAKERS_FINAL)
    merged = final.merge(stance_map, on=["name","role_raw"], how="left")
    merged.to_csv(OUT_FINAL, index=False)
    print(f"\nFinal table with stance: {len(merged):,} rows → {OUT_FINAL}")
    skipped = (results_df["stance"] == "SKIP").sum()
    neutral = (results_df["stance"] == "S0").sum()
    print(f"SKIP: {skipped} | S0 (neutral): {neutral}")


if __name__ == "__main__":
    main()
