"""Interne Verlinkung optimieren - Streamlit-Demo.

Anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im Vergleich) und wie
die Konzepte-Demos üblich zeigt diese Demo EIN Verfahren (PageRank-Budget-Optimierung) - aber mit
echten Daten statt eines wachsenden künstlichen Beispiels: der tatsächliche Verlinkungsgraph von
sebastianhanisch.net samt aller 300 Demos, Stand 2026-09-30.
"""

from __future__ import annotations

import itertools

import plotly.graph_objects as go
import streamlit as st

from graph import build_base_graph, load_snapshot, pagerank
from optimierung import exakt, greedy, groesste_seiten_pagerank_zuerst, target_score, zufaellig

st.set_page_config(page_title="Interne Verlinkung optimieren", page_icon="🔗", layout="wide")

SNAP = load_snapshot()
ALLE_LINIEN = sorted(p for p in SNAP.pages if p.startswith("konzepte-") and p != "konzepte.html")


@st.cache_data
def _ist_zustand_pagerank() -> dict[str, float]:
    return pagerank(build_base_graph(SNAP))


@st.cache_data
def _kandidatenpool_sortiert(target: str) -> list[str]:
    """Alle Demo-URLs, sortiert nach dem PageRank ihrer verweisenden Seite im Ist-Zustand - die
    Reihenfolge, in der die Referrer-Heuristik sie ohnehin durchgeht, hier für die Pool-Begrenzung
    der Suche wiederverwendet."""
    pr = _ist_zustand_pagerank()
    scored = []
    for url in SNAP.demo_urls:
        if url == target:
            continue
        best = max((pr.get(p, 0.0) for p in SNAP.demo_referrers.get(url, [])), default=0.0)
        scored.append((best, url))
    scored.sort(reverse=True)
    return [url for _, url in scored]


st.title("🔗 Interne Verlinkung optimieren")
st.caption(f"Echte Daten von sebastianhanisch.net, Stand {SNAP.stand} - kein künstliches Beispiel.")

st.markdown(
    "Alle 300 Demos verlinken heute einheitlich auf `sebastianhanisch.net/` und `/kontakt.html` "
    "zurück - unabhängig davon, zu welcher Konzepte-Linie oder Themenseite sie eigentlich gehören. "
    "Das Ergebnis: **66,9 % der internen Linkkraft der Website verschwindet an den 300 externen "
    "Demos** und ein Großteil davon fließt nur an zwei Seiten zurück, nie an die einzelne Linie "
    "selbst. Frage dieser Demo: Bei einem festen Budget, wie vielen Demos zusätzlich ein Rücklink "
    "zu einer bestimmten Zielseite eingefügt werden darf - welche Demos sollte man wählen?"
)

with st.sidebar:
    st.header("Einstellungen")
    ziel = st.selectbox("Zielseite", ALLE_LINIEN, index=ALLE_LINIEN.index("konzepte-lineare-programmierung.html")
                         if "konzepte-lineare-programmierung.html" in ALLE_LINIEN else 0,
                         format_func=lambda p: p.removeprefix("konzepte-").removesuffix(".html"))
    budget = st.slider("Budget (zusätzliche Rücklinks)", 1, 6, 3)
    pool_groesse = st.slider("Kandidatenpool (von 300 Demos, nach Referrer-Rang)", 10, 300, 60, step=10,
                              help="Begrenzt Zufällig/Referrer-Heuristik/Greedy auf die Top-N Demos nach "
                                   "PageRank ihrer verweisenden Seite - sonst dauert die Suche zu lange.")
    exakt_pool = st.slider("Kandidatenpool NUR für die exakte Referenz", 4, 14, 8,
                            help="Erschöpfende Suche über alle Teilmengen dieser Größe - wächst mit "
                                 "C(n, Budget), muss deshalb viel kleiner bleiben als der übrige Pool.")

pool_sortiert = _kandidatenpool_sortiert(ziel)
kandidaten = pool_sortiert[:pool_groesse]
kandidaten_exakt = pool_sortiert[:exakt_pool]

ist_pr = _ist_zustand_pagerank()[ziel]

with st.spinner("Rechne Zufällig, Referrer-Heuristik, Greedy und Exakt durch..."):
    auswahl = {
        "Ist-Zustand (kein Zusatz-Rücklink)": frozenset(),
        "Zufällig": zufaellig(SNAP, ziel, budget, kandidaten),
        "Referrer-Heuristik": groesste_seiten_pagerank_zuerst(SNAP, ziel, budget, kandidaten),
        "Greedy": greedy(SNAP, ziel, budget, kandidaten),
        f"Exakt (Pool {exakt_pool})": exakt(SNAP, ziel, min(budget, exakt_pool), kandidaten_exakt),
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
    st.metric("Ist-Zustand", f"{ist_pr:.5f}")
    bester = max((n for n in scores if n != "Ist-Zustand (kein Zusatz-Rücklink)"), key=lambda n: scores[n])
    zuwachs = (scores[bester] / ist_pr - 1) * 100
    st.metric(f"Bestes Verfahren: {bester}", f"{scores[bester]:.5f}", f"{zuwachs:+.1f} %")

st.subheader("Welche Demos wurden gewählt?")
for name in ("Referrer-Heuristik", "Greedy", f"Exakt (Pool {exakt_pool})"):
    gewaehlt = auswahl[name]
    titel = [SNAP.demo_title.get(u, u) for u in gewaehlt]
    st.markdown(f"**{name}:** {', '.join(titel) if titel else '–'}")

with st.expander("Warum ist Greedy hier eine gute Wahl, nicht nur bequem?"):
    st.markdown(
        "Der Grenzgewinn eines weiteren Rücklinks nimmt ab, je mehr schon gewählt sind - die "
        "zusätzliche Linkkraft überschneidet sich mit der schon vorhandenen. Das ist dieselbe "
        "Struktur wie bei Facility Location oder Einflussmaximierung in Netzwerken: eine "
        "(näherungsweise) submodulare Zielfunktion, bei der Greedy nachweislich nah am Optimum "
        "bleibt, ohne alle Teilmengen prüfen zu müssen. Die exakte Referenz hier läuft deshalb "
        "bewusst nur auf einem kleinen Kandidatenpool, wo eine erschöpfende Suche überhaupt "
        "zumutbar ist - bei 300 Demos und Budget 3 wären das über 4,4 Millionen Teilmengen."
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
