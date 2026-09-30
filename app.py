"""Interne Verlinkung optimieren - Streamlit-Demo.

Anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im Vergleich) und wie
die Konzepte-Demos üblich zeigt diese Demo EIN Verfahren (PageRank-Budget-Optimierung) - aber mit
echten Daten statt eines wachsenden künstlichen Beispiels: der tatsächliche Verlinkungsgraph von
sebastianhanisch.net samt aller 300 Demos, Stand 2026-09-30.

Wichtig: Kandidaten für einen zusätzlichen Rücklink sind NIE beliebige Demos, sondern nur die der
Ziel-Linie selbst (bekommen den Rücklink immer - das ist Korrektheit, keine Wahl) und Demos aus
Linien, die laut den echten Crosslink-Angaben der Website inhaltlich mit der Zielseite verbunden
sind. Ein Rücklink ohne inhaltlichen Bezug wäre irreführend, nicht nur suboptimal.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from graph import build_base_graph, build_graph_mit_fix, load_snapshot, pagerank
from optimierung import exakt, greedy, groesste_seiten_pagerank_zuerst, target_score, zufaellig

st.set_page_config(page_title="Interne Verlinkung optimieren", page_icon="🔗", layout="wide")

SNAP = load_snapshot()
ALLE_LINIEN = sorted(p for p in SNAP.pages if p.startswith("konzepte-") and p != "konzepte.html")


@st.cache_data
def _ist_zustand_pagerank() -> dict[str, float]:
    return pagerank(build_base_graph(SNAP))


st.title("🔗 Interne Verlinkung optimieren")
st.caption(f"Echte Daten von sebastianhanisch.net, Stand {SNAP.stand} - kein künstliches Beispiel.")

st.markdown(
    "Alle 300 Demos verlinken heute einheitlich auf `sebastianhanisch.net/` und `/kontakt.html` "
    "zurück - unabhängig davon, zu welcher Konzepte-Linie sie eigentlich gehören. Ergebnis: "
    "**66,9 % der internen Linkkraft der Website verschwindet an den 300 externen Demos**, und der "
    "zurückfließende Teil landet fast nur bei Startseite und Kontakt, nie bei der einzelnen Linie.\n\n"
    "**Kandidaten für einen zusätzlichen Rücklink sind hier nie beliebige Demos** - nur die der "
    "Ziel-Linie selbst (bekommen ihn immer, das ist schlicht Korrektheit) und Demos aus Linien, die "
    "laut den echten Crosslink-Angaben der Website inhaltlich verwandt sind. Offene Frage: Wenn ein "
    "Budget verhindert, dass jede verwandte Demo jede Nachbarlinie erwähnt - welche sollten Vorrang "
    "bekommen?"
)

with st.sidebar:
    st.header("Einstellungen")
    ziel = st.selectbox("Zielseite", ALLE_LINIEN, index=ALLE_LINIEN.index("konzepte-lineare-programmierung.html")
                         if "konzepte-lineare-programmierung.html" in ALLE_LINIEN else 0,
                         format_func=lambda p: p.removeprefix("konzepte-").removesuffix(".html"))

eigene, nachbarn = SNAP.relevant_candidates(ziel)

with st.sidebar:
    st.caption(f"{len(eigene)} eigene Demos, {len(nachbarn)} Demos in crosslink-verwandten Linien.")
    budget = st.slider("Budget (Nachbar-Demos mit Zusatz-Rücklink)", 0, min(8, len(nachbarn) or 1),
                        min(3, len(nachbarn) or 0))
    exakt_pool_groesse = st.slider("Kandidatenpool NUR für die exakte Referenz", 2, min(16, max(len(nachbarn), 2)),
                                    min(10, max(len(nachbarn), 2)),
                                    help="Erschöpfende Suche über alle Teilmengen wächst mit C(n, Budget) - "
                                         "muss deshalb auf die vielversprechendsten Nachbar-Demos begrenzt "
                                         "bleiben, sonst dauert sie bei großen Linien zu lange.")

ist_pr = _ist_zustand_pagerank()[ziel]
basis_fix_pr = target_score(SNAP, ziel, frozenset())  # nur der Basis-Fix (eigene Demos), keine Nachbarn

if not nachbarn:
    st.info(f"{ziel} hat laut Crosslink-Angaben keine verwandte Linie - hier gibt es keine "
            "Nachbar-Demos, unter denen man wählen könnte.")
    kandidaten_exakt = []
else:
    ist_zustand_pr_alle = _ist_zustand_pagerank()
    kandidaten_exakt_sortiert = groesste_seiten_pagerank_zuerst(
        SNAP, ziel, len(nachbarn), nachbarn, ist_zustand_pr_alle)
    kandidaten_exakt = list(kandidaten_exakt_sortiert)[:exakt_pool_groesse]

    with st.spinner("Rechne Zufällig, Referrer-Heuristik, Greedy und Exakt durch..."):
        auswahl = {
            "Ist-Zustand (nur bestehender Rücklink)": frozenset(),
            "Zufällig": zufaellig(nachbarn, budget),
            "Referrer-Heuristik": groesste_seiten_pagerank_zuerst(SNAP, ziel, budget, nachbarn, ist_zustand_pr_alle),
            "Greedy": greedy(SNAP, ziel, budget, nachbarn),
            f"Exakt (Pool {len(kandidaten_exakt)})": exakt(SNAP, ziel, budget, kandidaten_exakt),
        }
        scores = {name: target_score(SNAP, ziel, wahl) for name, wahl in auswahl.items()}

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure(go.Bar(
            x=list(scores.values()), y=list(scores.keys()), orientation="h",
            text=[f"{v:.5f}" for v in scores.values()], textposition="outside",
            marker_color=["#8A96A6", "#B7BEC7", "#D68A2E", "#3E8E86", "#14233B"],
        ))
        fig.update_layout(title=f"PageRank von {ziel} je Verfahren", xaxis_title="PageRank",
                           height=320, margin=dict(l=10, r=80, t=40, b=10))
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.metric("Ist-Zustand (heute)", f"{ist_pr:.5f}")
        st.metric("Nach Basis-Fix (nur eigene Demos)", f"{basis_fix_pr:.5f}",
                  f"{(basis_fix_pr/ist_pr-1)*100:+.1f} %")
        bester = max((n for n in scores if not n.startswith("Ist-Zustand")), key=lambda n: scores[n])
        st.metric(f"+ Nachbarn, bestes Verfahren: {bester}", f"{scores[bester]:.5f}",
                  f"{(scores[bester]/basis_fix_pr-1)*100:+.1f} % ggü. Basis-Fix")

    st.subheader("Welche Nachbar-Demos wurden gewählt?")
    for name in ("Referrer-Heuristik", "Greedy", f"Exakt (Pool {len(kandidaten_exakt)})"):
        gewaehlt = auswahl[name]
        titel = [SNAP.demo_title.get(u, u) for u in gewaehlt]
        st.markdown(f"**{name}:** {', '.join(titel) if titel else '–'}")

st.subheader(f"Eigene Demos von {ziel.removeprefix('konzepte-').removesuffix('.html')} (immer verlinkt)")
st.markdown(", ".join(SNAP.demo_title.get(u, u) for u in eigene) or "–")

with st.expander("Warum ist Greedy hier eine gute Wahl, nicht nur bequem?"):
    st.markdown(
        "Der Grenzgewinn einer weiteren Nachbar-Demo nimmt ab, je mehr schon gewählt sind - die "
        "zusätzliche Linkkraft überschneidet sich mit der schon vorhandenen. Das ist dieselbe "
        "Struktur wie bei Facility Location oder Einflussmaximierung in Netzwerken: eine "
        "(näherungsweise) submodulare Zielfunktion, bei der Greedy nachweislich nah am Optimum "
        "bleibt, ohne alle Teilmengen prüfen zu müssen. Die exakte Referenz läuft deshalb bewusst "
        "nur auf den vielversprechendsten Nachbar-Demos, nicht auf allen - bei großen Linien mit "
        "80+ verwandten Demos wäre eine erschöpfende Suche über alle sonst nicht zumutbar."
    )

with st.expander("Warum nur eigene und crosslink-verwandte Demos, nicht alle 300?"):
    st.markdown(
        "Ein Rücklink ohne inhaltlichen Bezug (z. B. eine Dijkstra-Demo, die zusätzlich auf die "
        "Standortplanung-Seite verlinkt, nur weil das irgendwo den PageRank erhöht) wäre für "
        "Besucher irreführend und liest sich wie Linkmanipulation, nicht wie eine echte Empfehlung. "
        "Deshalb sind Kandidaten hier immer auf inhaltlich bereits dokumentierte Beziehungen "
        "beschränkt: die eigene Linie einer Demo, oder Linien, die im Beziehungsgraphen der "
        "Konzepte-Seite als verwandt markiert sind."
    )

with st.expander("Gesamtbild: wie viel Linkkraft fließt insgesamt an die 300 Demos?"):
    demo_pr = sum(v for k, v in _ist_zustand_pagerank().items() if k in SNAP.demo_urls)
    st.markdown(
        f"Im Ist-Zustand liegen **{demo_pr*100:.1f} %** des gesamten PageRank auf den 300 externen "
        f"Demo-Knoten (Stand {SNAP.stand}) - ohne dass eine einzelne Konzepte-Linie oder Themenseite "
        "davon gezielt profitiert, weil alle Demos einheitlich auf Startseite und Kontakt zurückzeigen."
    )

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) - "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
