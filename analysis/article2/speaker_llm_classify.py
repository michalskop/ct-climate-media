"""P2.4 — LLM classification of unresolved speaker (name, role) pairs.

Sends batches of 30 pairs to Claude Haiku with M1–M6 definitions.
Merges results back into speakers_unique.csv.

Usage:
  python speaker_llm_classify.py [--dry-run]

Outputs:
  data/speakers_llm_results.csv  — LLM classifications
  data/speakers_final.csv        — merged final table
"""

import argparse
import json
import os
import time
from pathlib import Path

import anthropic
import pandas as pd
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

REPO     = Path(__file__).parent.parent.parent
LLM_FILE = REPO / "data/speakers_for_llm.csv"
UNI_FILE = REPO / "data/speakers_unique.csv"
OUT_LLM  = REPO / "data/speakers_llm_results.csv"
OUT_FINAL = REPO / "data/speakers_final.csv"

BATCH_SIZE = 30
MODEL      = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You classify Czech Television news speakers into types based on name and role label.
Return ONLY a JSON array — no prose, no explanation.

Types:
M1 = Moderátor/journalist (anchor, reporter, editor, correspondent, commentator, press spokesperson)
M2 = Ordinary citizen (resident, farmer, student, patient, pensioner, driver, consumer, actor/celebrity guest)
M3 = Scientist/academic expert (researcher, professor, climatologist, meteorologist, biologist, historian, sociologist, geologist, any -log/-log* discipline)
M4 = Science communicator or pseudoscientist (populariser, wellness coach, lifestyle guru, alternative medicine)
M5 = Stakeholder (NGO/business director, CEO, manager, activist, lobbyist, rector, dean, founder, analyst working outside government)
M6 = Politician/official (minister, premier, president, MP, senator, MEP, governor, mayor, ambassador, party leader, UN/EU official, chancellor, envoy)
SKIP = Not a real speaker role (fragment, verb phrase, noise)"""

USER_TEMPLATE = """Classify these {n} Czech Television speakers. For each item return {{"id": <id>, "type": "<M1|M2|M3|M4|M5|M6|SKIP>"}}.

{items}"""


def format_items(batch: list[dict]) -> str:
    lines = []
    for i, row in enumerate(batch):
        lines.append(f'{i}. Name: {row["name"]} | Role: {row["role_raw"]}')
    return "\n".join(lines)


def classify_batch(client: anthropic.Anthropic, batch: list[dict], dry_run: bool) -> list[dict]:
    if dry_run:
        return [{"id": i, "type": "M5"} for i in range(len(batch))]

    prompt = USER_TEMPLATE.format(n=len(batch), items=format_items(batch))
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    # Strip markdown fences if present
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:-1])
    return json.loads(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="No API calls; assign M5 to all")
    args = parser.parse_args()

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    df = pd.read_csv(LLM_FILE)
    print(f"Loaded {len(df)} pairs to classify")

    records = df.to_dict("records")
    results = []
    batches = [records[i:i+BATCH_SIZE] for i in range(0, len(records), BATCH_SIZE)]
    total_batches = len(batches)

    for b_idx, batch in enumerate(batches):
        print(f"  Batch {b_idx+1}/{total_batches} ({len(batch)} items)…", end=" ", flush=True)
        try:
            raw = classify_batch(client, batch, args.dry_run)
            for item in raw:
                idx = item["id"]
                results.append({
                    "name":     batch[idx]["name"],
                    "role_raw": batch[idx]["role_raw"],
                    "type_llm": item["type"],
                })
            print(f"ok")
        except Exception as e:
            print(f"ERROR: {e}")
            for row in batch:
                results.append({"name": row["name"], "role_raw": row["role_raw"], "type_llm": "?"})
        if not args.dry_run and b_idx < total_batches - 1:
            time.sleep(0.5)

    llm_df = pd.DataFrame(results)
    llm_df.to_csv(OUT_LLM, index=False)
    print(f"\nLLM results: {len(llm_df)} rows → {OUT_LLM}")
    print(llm_df["type_llm"].value_counts().to_string())

    # Merge back with unique speakers
    unique = pd.read_csv(UNI_FILE)
    # Start from rule-based types; override with LLM where rule said '?'
    llm_map = {(r["name"], r["role_raw"]): r["type_llm"] for _, r in llm_df.iterrows()}
    def resolve(row):
        if row["type"] != "?":
            return row["type"], "rule"
        llm = llm_map.get((row["name"], row["role_raw"]), "?")
        return (llm if llm != "SKIP" else "?"), "llm" if llm != "?" else "unresolved"

    unique[["type_final","source"]] = unique.apply(resolve, axis=1, result_type="expand")
    unique.to_csv(OUT_FINAL, index=False)
    print(f"\nFinal speakers table: {len(unique)} rows → {OUT_FINAL}")
    print(unique["type_final"].value_counts().to_string())
    skipped = (llm_df["type_llm"] == "SKIP").sum()
    print(f"\nSKIP (false positives filtered): {skipped}")


if __name__ == "__main__":
    main()
