"""Interne Verlinkung: Diagnose und Wirkungsanalyse - Streamlit-Demo.

Anders als das übliche Konzepte-Demo-Muster (ein Verfahren an einem wachsenden künstlichen Beispiel)
und anders als eine Optimierung (mehrere Verfahren im Vergleich) ist das hier eine Netzwerkanalyse
am echten Fall: Wie fließt PageRank tatsächlich durch sebastianhanisch.net, und was ändert eine
konkrete, inhaltlich begründete Korrektur der Demo-Rücklinks daran? Passt zu den anderen
Analyse-Karten der Graphen-und-Netzwerke-Linie (Zentralität, Strukturkennzahlen) - eine Kennzahl
berechnen und interpretieren, nicht Verfahren gegeneinander optimieren.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from analyse import dag_vs_live_diagnose, groesste_gewinner, index_kontakt_anteil, konzepte_linien, linien_mittel
from graph import build_base_graph, build_mit_basis_fix, build_mit_vollem_fix, load_snapshot, pagerank

st.set_page_config(page_title="Interne Verlinkung: Diagnose und Wirkung", page_icon="🔗", layout="wide")

SNAP = load_snapshot()
LINIEN = konzepte_linien(SNAP)


@st.cache_data
def _pageranks() -> dict[str, dict[str, float]]:
    return {
        "Ist-Zustand": pagerank(build_base_graph(SNAP)),
        "Basis-Fix (eigene Linie)": pagerank(build_mit_basis_fix(SNAP)),
        "Voller Fix (+ verwandte Linien)": pagerank(build_mit_vollem_fix(SNAP)),
    }


PR = _pageranks()

st.title("🔗 Interne Verlinkung: Diagnose und Wirkungsanalyse")
st.caption(f"Echte Daten von sebastianhanisch.net, Stand {SNAP.stand} - kein künstliches Beispiel.")

st.markdown(
    "Diese Demo gehört zur **Graphen-und-Netzwerke-Linie** der Konzepte-Reihe von "
    "[sebastianhanisch.net](https://sebastianhanisch.net) - anders als die dortigen Verfahrens-Demos "
    "(ein Algorithmus an einem wachsenden, meist künstlichen Beispiel) ist das hier eine "
    "**Analyse-Karte**: eine Kennzahl an einem einzigen, aber echten Fall berechnen und interpretieren, "
    "kein Verfahrensvergleich. PageRank misst hier nicht an einem Lehrbuch-Graphen, sondern am "
    "tatsächlichen Verlinkungsgraphen der Website selbst, in dem diese Demo läuft - inklusive aller "
    "50 Seiten und 300 externen Demos."
)

st.header("1. Diagnose: wohin fließt die Linkkraft heute?")
st.markdown(
    "Alle 300 Demos der Website verlinken im laufenden `app.py`-Footer einheitlich auf "
    "`sebastianhanisch.net/` und `/kontakt.html` zurück - unabhängig davon, zu welcher Konzepte-Linie "
    "sie inhaltlich gehören. Dazu kommen 69 echte Demo-zu-Demo-Querverlinkungen in 35 Repos, die der "
    "Baureihenfolge der jeweiligen Linie folgen."
)

ist = PR["Ist-Zustand"]
ik_anteil = index_kontakt_anteil(ist)
linien_summe = linien_mittel(SNAP, ist) * len(LINIEN)
col1, col2, col3 = st.columns(3)
col1.metric("PageRank auf index.html + kontakt.html allein", f"{ik_anteil*100:.1f} %")
col2.metric("PageRank auf allen 26 Konzepte-Linien zusammen", f"{linien_summe*100:.1f} %")
col3.metric("Ø PageRank je Konzepte-Linie", f"{linien_mittel(SNAP, ist):.5f}")

fig_diag = go.Figure(go.Bar(
    x=[ist[p] for p in LINIEN],
    y=[p.removeprefix("konzepte-").removesuffix(".html") for p in LINIEN],
    orientation="h", marker_color="#8A96A6",
))
fig_diag.add_vline(x=ist["index.html"], line_dash="dash", line_color="#D68A2E",
                    annotation_text="index.html", annotation_position="top")
fig_diag.update_layout(title="PageRank der 26 Konzepte-Linien heute, zum Vergleich die Startseite",
                        xaxis_title="PageRank", height=560, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig_diag, width="stretch")
st.caption(
    f"index.html und kontakt.html halten zusammen **{ik_anteil*100:.1f} %** des gesamten PageRank "
    f"der Website - mehr als alle 26 Konzepte-Linien zusammen ({linien_summe*100:.1f} %), obwohl "
    "jede Linie eigene Demos hat, die inhaltlich genau zu ihr gehören. Die Linkkraft, die die Demos "
    "zurückgeben, landet fast vollständig bei den zwei generischen Seiten statt bei der Linie, die "
    "sie tatsächlich verdient hätte."
)

st.header("2. Wirkungsanalyse: was ändert eine Korrektur der Rücklinks?")
st.markdown(
    "Zwei feste Szenarien, keine Auswahl unter Alternativen - beides ist Korrektheit, keine "
    "Optimierung:\n\n"
    "- **Basis-Fix:** jede Demo verlinkt zusätzlich auf ihre eigene Heimatseite (Konzepte-Linie "
    "oder Themenseite) zurück - sie gehört ohnehin genau dorthin (`demo_registry.py`).\n"
    "- **Voller Fix:** zusätzlich verlinkt jede Demo auch auf die Linien, die laut den echten "
    "`crosslinks`-Feldern der Website mit ihrer eigenen Linie verwandt sind."
)

vergleich = {name: linien_mittel(SNAP, pr) for name, pr in PR.items()}
vergleich_ik = {name: index_kontakt_anteil(pr) for name, pr in PR.items()}

col1, col2 = st.columns(2)
with col1:
    fig1 = go.Figure(go.Bar(
        x=list(vergleich.values()), y=list(vergleich.keys()), orientation="h",
        text=[f"{v:.5f}" for v in vergleich.values()], textposition="outside",
        marker_color=["#8A96A6", "#3E8E86", "#14233B"],
    ))
    fig1.update_layout(title="Ø PageRank der 26 Konzepte-Linien je Szenario", xaxis_title="PageRank",
                        height=280, margin=dict(l=10, r=80, t=40, b=10))
    st.plotly_chart(fig1, width="stretch")
with col2:
    fig2 = go.Figure(go.Bar(
        x=[v * 100 for v in vergleich_ik.values()], y=list(vergleich_ik.keys()), orientation="h",
        text=[f"{v*100:.1f} %" for v in vergleich_ik.values()], textposition="outside",
        marker_color=["#8A96A6", "#3E8E86", "#14233B"],
    ))
    fig2.update_layout(title="Anteil des PageRank auf index.html + kontakt.html je Szenario", xaxis_title="Prozent",
                        height=280, margin=dict(l=10, r=80, t=40, b=10))
    st.plotly_chart(fig2, width="stretch")

basis_zuwachs = (vergleich["Basis-Fix (eigene Linie)"] / vergleich["Ist-Zustand"] - 1) * 100
voll_zuwachs = (vergleich["Voller Fix (+ verwandte Linien)"] / vergleich["Ist-Zustand"] - 1) * 100
ik_basis_delta = (vergleich_ik["Basis-Fix (eigene Linie)"] - vergleich_ik["Ist-Zustand"]) * 100
ik_voll_delta = (vergleich_ik["Voller Fix (+ verwandte Linien)"] - vergleich_ik["Ist-Zustand"]) * 100
st.markdown(
    f"Der Basis-Fix allein hebt den durchschnittlichen PageRank der Konzepte-Linien um "
    f"**{basis_zuwachs:+.1f} %**, der volle Fix um **{voll_zuwachs:+.1f} %** - während der Anteil "
    f"auf index.html + kontakt.html von {vergleich_ik['Ist-Zustand']*100:.1f} % auf "
    f"{vergleich_ik['Basis-Fix (eigene Linie)']*100:.1f} % ({ik_basis_delta:+.1f} Punkte) bzw. "
    f"{vergleich_ik['Voller Fix (+ verwandte Linien)']*100:.1f} % ({ik_voll_delta:+.1f} Punkte) "
    "sinkt - beides ohne dass irgendeine Demo einen inhaltlich unpassenden Rücklink bekommt."
)

st.subheader("Größte Gewinner (Ist-Zustand → voller Fix)")
gewinner = groesste_gewinner(SNAP, PR["Ist-Zustand"], PR["Voller Fix (+ verwandte Linien)"])
gewinner = [g for g in gewinner if g[0].startswith("konzepte-")][:8]
fig3 = go.Figure()
fig3.add_trace(go.Bar(name="Ist-Zustand", y=[g[0].removeprefix("konzepte-").removesuffix(".html") for g in gewinner],
                       x=[g[1] for g in gewinner], orientation="h", marker_color="#8A96A6"))
fig3.add_trace(go.Bar(name="Voller Fix", y=[g[0].removeprefix("konzepte-").removesuffix(".html") for g in gewinner],
                       x=[g[2] for g in gewinner], orientation="h", marker_color="#14233B"))
fig3.update_layout(barmode="group", height=380, xaxis_title="PageRank", margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig3, width="stretch")

with st.expander("Warum keine Auswahl/Optimierung unter den Demos?"):
    st.markdown(
        "Eine frühere Fassung dieser Demo hat versucht, unter allen 300 Demos die 'optimale' "
        "Teilmenge für einen Rücklink auszuwählen - das führte dazu, dass z. B. eine Dijkstra-Demo "
        "'optimal' auf eine völlig unverwandte Seite verlinken konnte, nur weil das irgendwo den "
        "PageRank erhöhte. Das wäre für Besucher irreführend und liest sich wie Linkmanipulation, "
        "nicht wie eine echte Empfehlung. Die beiden Szenarien hier sind deshalb keine Optimierung "
        "unter Alternativen, sondern feste, inhaltlich begründete Korrekturen: Jede Demo bekommt "
        "genau die Rücklinks, die zu ihrer bereits dokumentierten Position auf der Website passen "
        "(eigene Linie, echte Crosslink-Nachbarn) - nicht mehr und nicht weniger."
    )

st.header("3. Diagnose: hält die Baureihenfolge, was die Diagramme versprechen?")
st.markdown(
    "Jede Konzepte-Linie hat ein `*_dag.dot`-Diagramm, das die Baureihenfolge der Verfahren "
    "dokumentiert (z. B. Hill Climbing → Simulated Annealing → Tabu Search) - die Grundlage für die "
    "Querverlinkung zwischen den Demos derselben Linie. Hier wird verglichen, was diese Diagramme "
    "an Kanten vorsehen mit dem, was die Demos in ihrem `app.py` tatsächlich verlinken."
)

diag = dag_vs_live_diagnose(SNAP)
col1, col2, col3 = st.columns(3)
col1.metric("Dokumentierte Kanten (27 Diagramme)", diag["anzahl_dokumentiert"])
col2.metric("Tatsächliche Live-Querlinks", diag["anzahl_live"])
col3.metric("Davon deckungsgleich", diag["anzahl_treffer"])

fig_dag = go.Figure(go.Bar(
    x=["Dokumentiert, aber nicht live verlinkt", "Live verlinkt, aber nicht dokumentiert", "Deckungsgleich"],
    y=[diag["anzahl_fehlend"], diag["anzahl_undokumentiert"], diag["anzahl_treffer"]],
    marker_color=["#D68A2E", "#3E8E86", "#14233B"],
))
fig_dag.update_layout(title="Dokumentierte vs. tatsächliche Demo-zu-Demo-Kanten", yaxis_title="Anzahl Kanten",
                       height=380, margin=dict(l=10, r=10, t=40, b=10))
st.plotly_chart(fig_dag, width="stretch")

st.caption(
    f"Von {diag['anzahl_dokumentiert']} dokumentierten Kanten ist nur **{diag['anzahl_treffer']}** "
    f"tatsächlich live verlinkt - **{diag['anzahl_fehlend']}** dokumentierte Kanten fehlen live, und "
    f"umgekehrt gibt es **{diag['anzahl_undokumentiert']}** Live-Querlinks, die in keinem Diagramm "
    "dokumentiert sind. Die Diagramme sind die Planung, die Demos die Umsetzung - und beide laufen "
    "an den meisten Stellen auseinander."
)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Beispiele: dokumentiert, aber nicht live verlinkt**")
    for quelle, ziel in diag["beispiele_fehlend"]:
        st.markdown(f"- {quelle} → {ziel}")
with col2:
    st.markdown("**Beispiele: live verlinkt, aber nicht dokumentiert**")
    for quelle, ziel in diag["beispiele_undokumentiert"]:
        st.markdown(f"- {quelle} → {ziel}")

st.header("Zusammenhänge zu anderen Stücken der Graphen-und-Netzwerke-Linie")
st.markdown(
    "- **[Zentralität](https://sebastianhanisch-centrality-demo.streamlit.app/)** führt PageRank "
    "bereits als eines von vier Zentralitätsmaßen ein - dort an synthetischen Vehikeln (Raster, "
    "Betriebsnetz, skalenfreies Netz), mit einem ernüchternden Befund: Auf einem ungesperrten, "
    "regelmäßigen Raster ist PageRank mit einer Rangkorrelation von nur 0,26 der schwächste "
    "Vorhersager für Ausfallschäden, deutlich hinter Betweenness. Diese Demo hier nimmt genau dasselbe "
    "Verfahren und wendet es auf ein einzelnes, aber echtes Netz an - die Website selbst -, statt "
    "mehrere synthetische Vehikel zu vergleichen. Kein Widerspruch: Dass PageRank auf einem "
    "Lehrbuch-Raster schlecht vorhersagt, sagt nichts darüber, ob es auf einem echten, stark "
    "asymmetrischen Web-Graphen ein aussagekräftiges Bild liefert - und genau das zeigt Abschnitt 1 "
    "oben.\n"
    "- **[Strukturkennzahlen und Nullmodelle](https://sebastianhanisch-strukturkennzahlen-demo.streamlit.app/)** "
    "ist die andere Analyse-Karte der Linie: dieselbe Grundidee (eine Kennzahl berechnen und "
    "interpretieren, kein Verfahrensvergleich), aber an einem Nullmodell statt an einem realen Fall - "
    "und mit Clustering/Kleine-Welt/Assortativität andere Kennzahlen als PageRank.\n"
    "- Alle zwölf Stücke der Linie im Zusammenhang: "
    "**[Graphen und Netzwerke erklärt](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html)** "
    "auf der Website - dort auch der Abhängigkeitsgraph, der zeigt, wie Zentralität selbst ein "
    "Zusammenfluss aus BFS/DFS und Brücken ist und zu Strukturkennzahlen und weiter zu Robustheit führt."
)

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) - "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
