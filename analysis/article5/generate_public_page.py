"""P5 — Generate static HTML public page for FAMU.

Produces a self-contained HTML file summarising the research project,
embedding charts as base64 images (no external dependencies at view time).

Output: public/index.html
"""

import base64
from pathlib import Path

REPO   = Path(__file__).parent.parent.parent
VIZ5   = REPO / 'visualizations/article5'
VIZ3   = REPO / 'visualizations/article3'
OUT    = REPO / 'docs'
OUT.mkdir(parents=True, exist_ok=True)


def b64img(path: Path) -> str:
    if not path.exists():
        return ''
    data = base64.b64encode(path.read_bytes()).decode()
    return f'data:image/png;base64,{data}'


def img_tag(path: Path, alt: str, caption: str = '') -> str:
    src = b64img(path)
    if not src:
        return f'<p class="missing">[chart not found: {path.name}]</p>'
    html = f'<figure><img src="{src}" alt="{alt}" loading="lazy">'
    if caption:
        html += f'<figcaption>{caption}</figcaption>'
    html += '</figure>'
    return html


CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: 'Georgia', serif;
    background: #FFFAF5;
    color: #2B2B2B;
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    line-height: 1.65;
}
h1 { font-size: 2rem; color: #8B1A1A; margin-bottom: 0.3rem; }
.subtitle { font-size: 1.1rem; color: #6B6B6B; margin-bottom: 0.5rem; }
.meta { font-size: 0.9rem; color: #8B8B8B; margin-bottom: 2.5rem; border-bottom: 1px solid #E0D8CF; padding-bottom: 1rem; }
h2 { font-size: 1.4rem; color: #8B1A1A; margin: 2.5rem 0 0.8rem; border-left: 4px solid #8B1A1A; padding-left: 0.7rem; }
h3 { font-size: 1.1rem; color: #3B3B3B; margin: 1.5rem 0 0.4rem; }
p  { margin-bottom: 0.9rem; }
ul { margin: 0.5rem 0 0.9rem 1.5rem; }
li { margin-bottom: 0.3rem; }
figure { margin: 1.5rem 0; text-align: center; }
figure img { max-width: 100%; border: 1px solid #E0D8CF; border-radius: 4px; }
figcaption { font-size: 0.85rem; color: #6B6B6B; margin-top: 0.4rem; font-style: italic; }
.finding-box {
    background: #FFF5F0;
    border-left: 4px solid #C44E52;
    padding: 0.8rem 1.2rem;
    margin: 1rem 0 1.5rem;
    border-radius: 0 4px 4px 0;
}
.finding-box strong { color: #8B1A1A; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.92rem; }
th { background: #8B1A1A; color: #FFF; padding: 0.5rem 0.8rem; text-align: left; }
td { padding: 0.4rem 0.8rem; border-bottom: 1px solid #E0D8CF; }
tr:nth-child(even) td { background: #FFF5F0; }
.score-good  { color: #2E6B3E; font-weight: bold; }
.score-mid   { color: #E07B39; font-weight: bold; }
.score-bad   { color: #8B1A1A; font-weight: bold; }
footer { margin-top: 4rem; font-size: 0.85rem; color: #8B8B8B; border-top: 1px solid #E0D8CF; padding-top: 1rem; }
.missing { color: #aaa; font-style: italic; font-size: 0.85rem; }
"""

def html_body(charts: dict) -> str:
    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Klimatický rozvrat a média veřejné služby</title>
<style>{CSS}</style>
</head>
<body>

<h1>Klimatický rozvrat a média veřejné služby</h1>
<p class="subtitle">Climate breakdown and public service media — Česká televize 2012–2022</p>
<p class="meta">
    <strong>Výzkumný tým:</strong> Andrea Culková (PI), Michal Škop (analýza dat) &nbsp;|&nbsp;
    <strong>Instituce:</strong> FAMU &nbsp;|&nbsp;
    <strong>Korpus:</strong> 2 914 dokumentů z celkových 531 593 přepisů zpravodajství ČT
</p>

<h2>O výzkumu</h2>
<p>
Výzkumný projekt analyzuje, jak Česká televize pokrývala klimatickou změnu v letech 2012–2022.
Pomocí korpusové analýzy, strojového učení a kvalitativní diskurzivní analýzy jsme zkoumali
geografické pokrytí, hlasy mluvčích, postoje (stanoviska) a témata v 2 914 klimaticky relevantních
dokumentech – 0,55 % z celého korpusu ČT zpravodajství.
</p>
<p>
Klíčová otázka: splňuje ČT kritéria <em>transformativní žurnalistiky</em> v oblasti klimatu –
tedy žurnalistiky, která nejen informuje, ale také mobilizuje, dává hlas marginalizovaným hlasům
a propojuje urgentnost s konkrétními řešeními?
</p>

<h2>Nalezení č. 1 — Geografické pokrytí: bohatý sever dominuje</h2>
<p>
75,6 % všech zmínek zemí pochází z dokumentů o zemích s <em>vysokým příjmem</em>. Země s nízkým
příjmem – tedy regiony nejohroženější klimatickou změnou – tvoří pouze 2,5 %. Více než
101 zemí se za 10 let objevilo v méně než 10 dokumentech.
</p>

{charts.get('worldmap', '')}

{charts.get('gni', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> Toto není specifické pro klima – analýza pěti podkorpusů ukazuje,
že jde o strukturální vlastnost ČT zpravodajství. Klimatické pokrytí je mírně méně eurocentrické
než ostatní témata (75,6 % vs. 83–87 %), ale mezera zůstává zásadní.
</div>

<h2>Nalezení č. 2 — Objem: reaktivní, nikoli proaktivní</h2>
<p>
Objem klimatického zpravodajství zhruba zdvojnásobil po roce 2019, poté zůstal zvýšený
přes COP26 (2021). V roce 2022 dominovala geopolitika (válka na Ukrajině): 46,8 % klimatických
dokumentů tohoto roku bylo primárně o energetické bezpečnosti, nikoli o klimatu.
</p>

{charts.get('annual', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> Píky v klimatickém zpravodajství odrážejí globální události
(Greta Thunberg, COP26, válka na Ukrajině), nikoli editorskou iniciativu ČT.
</div>

<h2>Nalezení č. 3 — Mluvčí: elity dominují, občané na okraji</h2>
<p>
Z 56 613 zmínek mluvčích tvoří novináři/moderátoři (M1) 54,8 %, politici (M6) 22,6 %,
zainteresované strany (M5) 11,0 %, vědci (M3) 8,6 % a <strong>občané (M2) jen 2,0 %</strong>.
Pseudovědci (M4) jsou prakticky nepřítomní (0,2 % – 87 zmínek za 10 let).
</p>

{charts.get('speakers', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> Vědci jsou v poměru 2,6:1 přečísleni politiky.
Klima je pokryto primárně jako politické téma, nikoli vědecké.
Žádný vědec (M3) nebyl nikdy klasifikován jako popírač (S1).
</div>

<h2>Nalezení č. 4 — Gender: systematická mezera v expertních hlasech</h2>

{charts.get('gender', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> Ženy tvoří celkově 27,6 % mluvčích.
U vědkyň (M3) je to 12,0 % – pod skutečným podílem žen v české vědě (35–40 %).
Selekční zkreslení je viditelné: pozvaní experti jsou méně genderově vyvážení
než skutečný pool expertů.
</div>

<h2>Nalezení č. 5 — Postoje: zodpovědné, nikoli transformativní</h2>
<p>
Z nápravných segmentů (2 103 bez S0) tvoří <em>informátoři</em> (S6) 82,2 %.
Popírači (S1) jsou vzácní (2,3 %), ale problematické postoje (S1+S2+S3 dohromady)
tvoří 13,5 %. Politici (M6) jsou primárními nositeli popírání a zpomalování.
</p>

{charts.get('stance', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> 10,2 % článků s nestranným postojem obsahuje
současně problematický hlas (S1/S2/S3) a informátora (S6) – forma falešné rovnováhy.
Spike v roce 2017 (18,6 %).
</div>

<h2>Nalezení č. 6 — Urgentnost bez jednání</h2>
<p>
Krizový jazyk se více než zdvojnásobil (40 → 104 výskytů na 100 dokumentů, 2012→2022).
Výzvy k jednání stagnovaly (10 → 12). Poměr klesl z 0,26 (2012) na 0,11 (2022).
</p>

{charts.get('urgency', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> ČT komunikuje krizi, ale ne jednání. Klimatická spravedlnost
je prakticky nepřítomná (méně než 2 výskyty na 100 dokumentů po celé sledované období).
</div>

<h2>Nalezení č. 7 — Témata: geopolitika vytlačuje vědu</h2>

{charts.get('topics', '')}

<div class="finding-box">
<strong>Klíčový závěr:</strong> Vědecky orientované pokrytí kleslo z 33 % (2012) na 13 % (2022).
V roce 2022 obsadila geopolitika (Ukrajina/energie) 46,8 % klimatických dokumentů.
</div>

<h2>Celkové hodnocení: transformativní žurnalistika</h2>
<p>
Tři kritéria transformativní žurnalistiky – de-polarizace, urgentnost a spravedlivá transformace
– jsou hodnocena na škále 0–10 na základě 11 empirických indikátorů.
</p>

{charts.get('radar', '')}

<table>
<tr><th>Kritérium</th><th>Skóre</th><th>Verdikt</th></tr>
<tr><td>De-polarizace</td><td class="score-good">7 / 10</td><td>ČT vyhýbá popírání a pseudovědě — skutečný úspěch</td></tr>
<tr><td>Urgentnost a řešení</td><td class="score-mid">3 / 10</td><td>Krize bez jednání; procedurální přístup</td></tr>
<tr><td>Spravedlivá transformace</td><td class="score-bad">1,5 / 10</td><td>Pouze elity; klimatická spravedlnost chybí; globální Jih neviditelný</td></tr>
</table>

<h2>Případové studie (P4)</h2>

<h3>CS1: Jaderná energie a obnovitelné zdroje (88 dokumentů, 3,0 %)</h3>
<p>Pokrytí je zarámováno jako energetická politika, nikoli klimatická věda.
Politici dominují (221 z ~295 segmentů); vědci jen 5. Postoj "zpomalování" (S3) je
zde nejvíce proporcionálně zastoupený ze všech tří případových studií.
Debata o taxonomii EU (2022) strukturovala pokrytí kolem českého národního zájmu.</p>

<h3>CS2: Sucho a záplavy (586 dokumentů, 20,1 %)</h3>
<p>Největší a nejdomestičtější případová studie. Vrchol v 2018–2019 odráží českou
sucho/kůrovce krizi. Občané jsou nejvíce zastoupeni zde (172 segmentů).
Klimatická atribuce přítomna, ale v pozadí; adaptace dominuje nad mitigací.</p>

<h3>CS3: Zdravotní dopady — ticho (17 dokumentů, 0,6 %)</h3>
<p>Pouze 17 z 2 914 klimatických dokumentů explicitně propojuje klimatickou změnu
se zdravím lidí. Tisíce dokumentů o vlnách veder (CS2) a téměř žádný nezmíní
zdravotní důsledky – stejné události jsou pokryty jako meteorologický
a zemědělský problém, nikoli jako krize veřejného zdraví.</p>

<div class="finding-box">
<strong>Klíčový závěr:</strong> ČT pokrývá klima zodpovědně, ale ne transformativně.
Vyhýbá se amplifikaci popírání a pseudovědy. Ale selhává ve všech dimenzích
transformativní žurnalistiky: urgentnost bez řešení, marginalisation občanů
a globálního jihu, genderová nerovnost a neviditelná klimatická spravedlnost.
</div>

<h2>Metodologie</h2>
<ul>
<li><strong>Korpus:</strong> 531 593 přepisů zpravodajství ČT (2012–2022); klimatický podkorpus: 2 914 dokumentů</li>
<li><strong>Extrakce mluvčích:</strong> Regex + dvoustupňová klasifikace (pravidla + LLM Claude Haiku)</li>
<li><strong>Klasifikace stanovisek (S0–S6):</strong> Segmenty projevů mluvčích → LLM (Claude Haiku, 5 928 segmentů)</li>
<li><strong>Tématické modelování:</strong> NMF (sklearn), k=20, 5 000 vlastností TF-IDF; bez lemmatizace</li>
<li><strong>Geografická detekce:</strong> Tříprůchodový regex (tokeny, víceslovné fráze, adjektivní kmeny)</li>
<li><strong>Genderová klasifikace:</strong> Koncovka příjmení (-á → F) + korekce cizích mužských jmen</li>
</ul>

<footer>
<p>SGS projekt &ldquo;Klimatický rozvrat a média veřejné služby&rdquo; &mdash; FAMU &mdash; 2025–2026</p>
<p>Data: Česká televize (přepisy zpravodajství) | Analýza: Python (pandas, sklearn, anthropic) |
Vizualizace: matplotlib | Kód: <a href="https://github.com/michalskop/ct-climate-media">github.com/michalskop/ct-climate-media</a></p>
</footer>

</body>
</html>"""


def main():
    charts = {
        'gni':      img_tag(VIZ5 / 'P1.11b_gni_comparison_v2.png',
                            'Income group coverage cross-subcorpus',
                            'Podíl zmínek zemí dle příjmové skupiny napříč podkorpusy ČT'),
        'annual':   img_tag(VIZ5 / 'P1.14_annual_docs_v2.png',
                            'Annual document count',
                            'Roční počet klimatických dokumentů (2012–2022)'),
        'speakers': img_tag(VIZ5 / 'P2.1_speaker_types_by_year_v2.png',
                            'Speaker types by year',
                            'Typy mluvčích dle roku'),
        'gender':   img_tag(VIZ5 / 'P2.2_gender_by_type_v2.png',
                            'Female speaker share by type',
                            'Podíl žen u jednotlivých typů mluvčích'),
        'stance':   img_tag(VIZ5 / 'P3.4_stance_overall_v2.png',
                            'Stance distribution',
                            'Distribuce stanovisek (všechny klasifikované segmenty)'),
        'urgency':  img_tag(VIZ5 / 'P3.1_urgency_trend_v2.png',
                            'Crisis language vs action calls over time',
                            'Krizový jazyk vs. výzvy k jednání (výskyty na 100 dokumentů)'),
        'topics':   img_tag(VIZ5 / 'P3.8_topic_categories_v2.png',
                            'Topic categories by year',
                            'Kategorie témat dle roku (NMF k=20)'),
        'radar':    img_tag(VIZ5 / 'P3.9_tj_radar_v2.png',
                            'Transformative journalism radar',
                            'Hodnocení transformativní žurnalistiky (0–10)'),
        'worldmap': img_tag(VIZ5 / 'P1.11_world_map_climate_v2.png',
                            'World map of country mentions in ČT climate coverage',
                            'Počet dokumentů zmiňujících danou zemi (logaritmická škála, 2012–2022)'),
    }

    html = html_body(charts)
    out_path = OUT / 'index.html'
    out_path.write_text(html, encoding='utf-8')
    size_kb = out_path.stat().st_size // 1024
    print(f"Public page written: {out_path} ({size_kb} KB)")


if __name__ == "__main__":
    main()
