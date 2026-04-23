"""P6.2 — LLM sentiment analysis: how does ČT frame EU climate policy?

Classifies each EU subcorpus document as:
  EU_POS  — EU climate policy framed as necessary, effective, correct direction
  EU_NEG  — EU policy framed as harmful, overreaching, economically damaging,
             ideologically driven; "diktát z Bruselu" framing
  EU_NEU  — Factual reporting; no clear editorial stance on EU policy merits
  SKIP    — EU terms appear incidentally; doc not substantively about EU climate policy

Document-level classification (not speaker-turn level) — 131 docs total.
Batch size 10, ~14 API calls. Estimated cost: <$0.05.

Output:
  data/eu_sentiment.csv  — article_id, year, matched_groups, sentiment, conf, rationale
"""

import json
import time
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import anthropic

REPO = Path(__file__).parent.parent.parent
load_dotenv(REPO / '.env')

OUT_FILE   = REPO / 'data/eu_sentiment.csv'
BATCH_SIZE = 5
MAX_WORDS  = 250   # words sent per document to LLM
MODEL      = 'claude-haiku-4-5-20251001'

PROMPT_SYSTEM = """You analyse Czech Television (ČT) news transcripts for a media research project.
Your task: classify how each document frames EU climate policy.

Labels:
  EU_POS  — EU climate policy (Green Deal, Fit for 55, ETS, combustion ban, etc.) is
             framed as necessary, scientifically grounded, a good direction, or beneficial
             for Czechia/Europe.
  EU_NEG  — EU policy is framed as harmful, ideologically driven, economically damaging,
             unrealistic, or an overreach ("diktát z Bruselu", "brusel zakazuje"). Includes
             framing that positions Czech interests against Brussels.
  EU_NEU  — Factual/procedural reporting: describes what EU policy does or decided without
             clear editorial stance on its merits. Most documents will be this.
  SKIP    — EU terms appear incidentally (e.g., a single mention of "Green Deal" in passing);
             document is not substantively about EU climate policy.

Confidence: 0 = uncertain, 1 = somewhat confident, 2 = confident, 3 = very confident.
Rationale: one short sentence (in English) explaining the key evidence.

Return ONLY a JSON array, one object per document:
[{"article_id": "...", "sentiment": "EU_POS|EU_NEG|EU_NEU|SKIP", "conf": 0-3, "rationale": "..."}]"""


def build_user_prompt(batch: list[dict]) -> str:
    parts = []
    for doc in batch:
        words = str(doc['text']).split()[:MAX_WORDS]
        snippet = ' '.join(words)
        parts.append(f'[DOC {doc["article_id"]} / {doc["year"]}]\n{snippet}')
    return '\n\n---\n\n'.join(parts)


def parse_response(text: str) -> list[dict]:
    import re
    text = text.strip()
    if text.startswith('```'):
        text = '\n'.join(text.split('\n')[1:-1])
    # Extract just the JSON array if surrounded by other text
    m = re.search(r'\[.*\]', text, re.DOTALL)
    if m:
        text = m.group(0)
    # Replace any unescaped double quotes inside string values (heuristic)
    # Strip non-ASCII from rationale strings to avoid encoding issues
    text = re.sub(r'("rationale"\s*:\s*")([^"]*?)(")',
                  lambda m: m.group(1) + m.group(2).encode('ascii','ignore').decode() + m.group(3),
                  text)
    return json.loads(text)


def load_done() -> set:
    if not OUT_FILE.exists():
        return set()
    return set(pd.read_csv(OUT_FILE)['article_id'].astype(str))


def main():
    sub = pd.read_csv(REPO / 'data/eu_subcorpus.csv')
    done = load_done()
    records = sub[~sub['article_id'].astype(str).isin(done)].to_dict('records')

    print(f"Documents to classify: {len(records)} (already done: {len(done)})")
    if not records:
        print("All done.")
        return

    client = anthropic.Anthropic()
    batches = [records[i:i+BATCH_SIZE] for i in range(0, len(records), BATCH_SIZE)]
    total_classified = 0

    for i, batch in enumerate(batches, 1):
        print(f"  Batch {i}/{len(batches)} ({len(batch)} docs)… ", end='', flush=True)
        try:
            resp = client.messages.create(
                model=MODEL,
                max_tokens=1024,
                system=PROMPT_SYSTEM,
                messages=[{'role': 'user', 'content': build_user_prompt(batch)}],
            )
            results = parse_response(resp.content[0].text)
        except Exception as e:
            print(f"ERROR: {e}")
            time.sleep(5)
            continue

        # Merge sentiment results back with metadata
        sent_map = {r['article_id']: r for r in results}
        rows = []
        for doc in batch:
            aid = str(doc['article_id'])
            s = sent_map.get(aid, {})
            rows.append({
                'article_id':     aid,
                'year':           doc['year'],
                'matched_groups': doc['matched_groups'],
                'sentiment':      s.get('sentiment', 'EU_NEU'),
                'conf':           s.get('conf', 0),
                'rationale':      s.get('rationale', ''),
            })

        write_header = not OUT_FILE.exists()
        pd.DataFrame(rows).to_csv(OUT_FILE, mode='a', header=write_header, index=False)
        total_classified += len(rows)
        print(f"ok ({', '.join(r['sentiment'] for r in rows)})")
        time.sleep(0.5)

    print(f"\nClassified {total_classified} documents → data/eu_sentiment.csv")


if __name__ == '__main__':
    main()
