"""P2.2/P2.3/P2.5 — Speaker extraction, gender, and M1–M6 rule-based classification.

Extracts all `Jméno PŘÍJMENÍ role` patterns from the climate subcorpus,
classifies gender (Czech surname suffix rule) and speaker type (M1–M6 keyword lookup).
Unresolved cases are saved separately for LLM review (P2.4).

Outputs:
  data/speakers_all.csv        — every mention (article_id, name, role, gender, type)
  data/speakers_unique.csv     — deduplicated (name, role) with counts
  data/speakers_for_llm.csv   — unresolved unique pairs → send to LLM
"""

import re
from pathlib import Path
import pandas as pd

REPO = Path(__file__).parent.parent.parent
BASE = REPO / "Climate change TV/BackupClimateChangeData/2.data_transformations/data"
OUT  = REPO / "data"

CORPUS = BASE / "climate_sub_corpus/climate_corpus_v4_2023.csv"

# ── Regex ──────────────────────────────────────────────────────────────────────
U = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]'
L = r'[a-záčďéěíňóřšťúůýž]'
W = r'[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽa-záčďéěíňóřšťúůýž]'

SPEAKER_RE = re.compile(
    rf'({U}{L}{{1,11}})\s+({U}{{2,20}}(?:\s{U}{{2,15}})?)\s+({L}{W}*(?:\s{L}{W}*){{0,4}})',
    re.UNICODE,
)

# ── Gender rule ────────────────────────────────────────────────────────────────
def infer_gender(firstname: str, surname: str) -> str:
    """F = clearly female; F? = probable female (first name); ? = ambiguous; M = male."""
    if surname.upper().endswith('Á'):   # -ová, -ská, -ná, -lá, all adjective-form surnames
        return 'F'
    if surname.upper().endswith('Ů'):   # Janů, Matoušů — both genders
        return '?'
    if firstname.endswith('a') or firstname.endswith('e'):  # Zuzana, Marcela, Hana…
        return 'F?'
    return 'M'

# ── M1–M6 lookup ──────────────────────────────────────────────────────────────
M1 = {  # anchor, journalist, reporter
    'moderátor','moderátorka','redaktor','redaktorka','zpravodaj','zpravodajka',
    'komentátor','komentátorka','reportér','reportérka','hlasatel','hlasatelka',
    'korespondent','korespondentka','editor','editorka','publicista','publicistka',
    'novinář','novinářka','mluvčí',
}
M3 = {  # scientist, academic expert
    'klimatolog','klimatoložka','meteorolog','meteoroložka','vědec','vědkyně',
    'profesor','profesorka','docent','docentka','fyzik','fyzička','biolog','bioložka',
    'ekolog','ekoložka','geograf','geografka','chemik','chemička','hydrolog',
    'výzkumník','výzkumnice','astronom','astronomka','glaciolog','oceánograf',
    'politolog','politoložka','geolog','geoložka','filozof','filozofka',
    'sociolog','socioložka','historik','historička','egyptolog','egyptoložka',
    'bioklimatolog','přírodovědec','přírodovědkyně','neurolog','neuroložka',
    'ornitolog','virolog','viroložka','epidemiolog','epidemioložka',
    'imunolog','matematik','matematička','statistik','statistička',
    'antropolog','antropoložka','psycholog','psycholožka','archeolog','archeoložka',
    'parazitolog','primář','primářka','odborník','odbornice','vědecký','vědecká',
    'glaciolog','hydrobiolog','toxikolog','endokrinolog','kardiolog',
    'onkolog','psychiatr','psychiatrka','genetik','genetička','polární','katedra',
}
M6 = {  # politician, official
    'ministr','ministryně','premiér','premiérka','prezident','prezidentka',
    'viceprezident','viceprezidentka','poslanec','poslankyně','senátor','senátorka',
    'europoslanec','europoslankyně','hejtman','hejtmanka','starosta','starostka',
    'primátor','primátorka','vicepremiér','vicepremiérka','guvernér','guvernérka',
    'předseda','předsedkyně','místopředseda','místopředsedkyně','velvyslanec',
    'velvyslankyně','diplomat','diplomatka','lídr','lídryně',
    'kandidát','kandidátka','politik','politička','tajemník','tajemnice',
    'radní','zastupitel','zastupitelka','komisař','komisařka','člen','členka',
    'náčelník','náčelnice',
}
M5 = {  # stakeholder: NGO, business, institution
    'ředitel','ředitelka','náměstek','náměstkyně','vedoucí','šéf','šéfová',
    'manažer','manažerka','analytik','analytička','ekonom','ekonomka',
    'expert','expertka','specialista','specialistka','poradce','poradkyně',
    'koordinátor','koordinátorka','zástupce','zástupkyně',
    'šéfredaktor','šéfredaktorka','aktivista','aktivistka','lobbista','lobbistka',
    'rektor','rektorka','děkan','děkanka','zakladatel','zakladatelka',
    'spoluzakladatel','spoluzakladatelka','majitel','majitelka',
    'jednatel','jednatelka','provozovatel','provozovatelka',
}
M2 = {  # ordinary citizen
    'obyvatel','obyvatelka','občan','občanka','důchodce','důchodkyně',
    'student','studentka','dělník','dělnice','farmář','farmářka',
    'zemědělec','zemědělkyně','rodič','matka','otec','babička','dědeček',
    'živnostník','živnostnice','řidič','řidička','zákazník','zákaznice',
    'pacient','pacientka','herec','herečka',
}
# Adjective/contextual modifiers stripped before lookup
MODIFIERS = {
    'bývalý','bývalá','současný','současná','hlavní','první','nový','nová',
    'výkonný','výkonná','místní','krajský','krajská','zvláštní','vládní',
    'politický','politická','ekonomický','ekonomická','ekologický','ekologická',
    'nezávislý','nezávislá','mezinárodní','evropský','evropská','národní',
    'státní','veřejný','veřejná','regionální','zahraniční','soukromý','soukromá',
    'tehdejší','navržený','navržená','jmenovaný','jmenovaná',
    'sociální','agrární','přírodní','technický','technická',
    'lesnický','lesnická','bezpečnostní','inženýrský','inženýrská',
    'programový','programová','pražský','pražská','brněnský','brněnská',
    # nationality adjectives preceding role noun
    'americký','americká','britský','britská','německý','německá','francouzský','francouzská',
    'ruský','ruská','čínský','čínská','australský','australská','kanadský','kanadská',
    'japonský','polský','polská','slovenský','slovenská','rakouský','rakouská',
    'izraelský','izraelská','italský','italská','švédský','švédská',
    'švýcarský','švýcarská','španělský','španělská','maďarský','maďarská',
    'turecký','turecká','indický','indická','íránský','íránská','egyptský','egyptská',
    'syrský','syrská','irácký','irácká',
}

def classify_type(role_raw: str) -> str:
    words = role_raw.lower().split()
    clean = [w for w in words if w not in MODIFIERS]
    first = clean[0] if clean else (words[0] if words else '')
    if first in M1: return 'M1'
    if first in M3: return 'M3'
    if first in M6: return 'M6'
    if first in M5: return 'M5'
    if first in M2: return 'M2'
    return '?'

# ── Extract ────────────────────────────────────────────────────────────────────

def extract(corpus_path: Path) -> pd.DataFrame:
    df = pd.read_csv(corpus_path, sep=";", low_memory=False)
    rows = []
    for _, doc in df.iterrows():
        for m in SPEAKER_RE.finditer(doc["text"]):
            fn, sn, role = m.group(1), m.group(2), m.group(3).strip()
            if len(role) < 4:
                continue
            rows.append({
                "article_id": doc["article_id"],
                "year":       int(str(doc["article_id"])[:4]),
                "firstname":  fn,
                "surname":    sn,
                "name":       f"{fn} {sn}",
                "role_raw":   role,
                "gender":     infer_gender(fn, sn),
                "type":       classify_type(role),
            })
    return pd.DataFrame(rows)

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    OUT.mkdir(exist_ok=True)
    print("Extracting speakers from climate subcorpus…")
    all_mentions = extract(CORPUS)
    print(f"  {len(all_mentions):,} mentions, {all_mentions['name'].nunique()} unique names")

    resolved = (all_mentions["type"] != "?").mean() * 100
    print(f"  Rule-based resolution: {resolved:.1f}%")
    print(f"\nType distribution:\n{all_mentions['type'].value_counts()}")
    print(f"\nGender (unique names):\n{all_mentions.drop_duplicates('name')['gender'].value_counts()}")

    # All mentions
    all_mentions.to_csv(OUT / "speakers_all.csv", index=False)

    # Unique (name, role) summary
    unique = (all_mentions.groupby(["name","firstname","surname","role_raw","gender","type"])
                          .agg(n_mentions=("article_id","count"),
                               n_docs=("article_id","nunique"))
                          .reset_index()
                          .sort_values("n_mentions", ascending=False))
    unique.to_csv(OUT / "speakers_unique.csv", index=False)

    # Unresolved → LLM queue
    for_llm = unique[unique["type"] == "?"][["name","role_raw","n_mentions","n_docs"]]
    for_llm = for_llm.sort_values("n_mentions", ascending=False)
    for_llm.to_csv(OUT / "speakers_for_llm.csv", index=False)
    print(f"\nSaved:")
    print(f"  speakers_all.csv    — {len(all_mentions):,} rows")
    print(f"  speakers_unique.csv — {len(unique):,} rows")
    print(f"  speakers_for_llm.csv — {len(for_llm):,} rows (→ LLM)")

if __name__ == "__main__":
    main()
