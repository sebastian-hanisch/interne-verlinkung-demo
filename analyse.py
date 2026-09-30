"""Auswertungen für die Diagnose- und Wirkungsanalyse - keine Optimierung: die beiden Fix-Szenarien
in graph.py (Basis-Fix, voller Fix) sind feste, inhaltlich begründete Korrekturen ohne Auswahl unter
Alternativen. Dieses Modul fasst nur zusammen, was diese Korrekturen an der PageRank-Verteilung
ändern.
"""

from __future__ import annotations

from graph import Snapshot


def konzepte_linien(snap: Snapshot) -> list[str]:
    return sorted(p for p in snap.pages if p.startswith("konzepte-") and p != "konzepte.html")


def demo_anteil(snap: Snapshot, pr: dict[str, float]) -> float:
    """Anteil des gesamten PageRank, der auf den 300 externen Demo-Knoten liegt. Ändert sich durch
    die Fix-Szenarien kaum (leicht steigend sogar) - die Fixes ändern nicht, WIE VIEL PageRank an
    den Demos hängt (das hängt an den eingehenden Links der 50 Seiten, die die Fixes nicht anfassen),
    sondern WOHIN die von den Demos zurückfließende Kraft geht. Die eigentliche Kennzahl dafür ist
    index_kontakt_anteil(), nicht diese."""
    return sum(v for k, v in pr.items() if k in snap.demo_referrers)


def index_kontakt_anteil(pr: dict[str, float]) -> float:
    """Anteil des gesamten PageRank, der allein auf index.html und kontakt.html liegt - die beiden
    Seiten, auf die aktuell jede der 300 Demos zurückverlinkt, unabhängig von ihrer eigenen Linie."""
    return pr["index.html"] + pr["kontakt.html"]


def linien_mittel(snap: Snapshot, pr: dict[str, float]) -> float:
    """Durchschnittlicher PageRank der 26 Konzepte-Linien-Seiten."""
    linien = konzepte_linien(snap)
    return sum(pr[p] for p in linien) / len(linien)


def groesste_gewinner(snap: Snapshot, pr_vorher: dict[str, float], pr_nachher: dict[str, float], n: int = 8) -> list[tuple[str, float, float]]:
    """Die n Seiten mit dem größten absoluten PageRank-Zuwachs zwischen zwei Szenarien."""
    diffs = [(p, pr_vorher[p], pr_nachher[p]) for p in snap.pages]
    diffs.sort(key=lambda t: t[2] - t[1], reverse=True)
    return diffs[:n]


def dokumentierte_kanten(snap: Snapshot) -> set[tuple[str, str]]:
    """Die in den *_dag.dot-Dateien dokumentierten Demo-zu-Demo-Kanten als (Quelle, Ziel)-Paare -
    unabhängig von Kante-Art (fix/kontrast/idee) und ohne Duplikate."""
    return {(e["quelle_url"], e["ziel_url"]) for e in snap.dag_edges}


def live_kanten(snap: Snapshot) -> set[tuple[str, str]]:
    """Die tatsächlich im laufenden app.py jeder Demo verbauten Querlinks als (Quelle, Ziel)-Paare."""
    return {(src, dst) for src, ziele in snap.demo_cross_links.items() for dst in ziele}


def dag_vs_live_diagnose(snap: Snapshot) -> dict:
    """Vergleicht die dokumentierte Soll-Struktur (dag_edges) mit den tatsächlichen Live-Querlinks
    (demo_cross_links): wie viele Kanten stimmen überein, welche dokumentierten Kanten fehlen live,
    welche Live-Kanten sind nirgends dokumentiert. Reine Bestandsaufnahme, keine Bewertung, welche
    der beiden Quellen "richtig" ist - die Diagramme sind die Planung, die Live-Links die Umsetzung,
    und diese Diagnose zeigt, wie weit beide auseinanderlaufen."""
    dokumentiert = dokumentierte_kanten(snap)
    live = live_kanten(snap)
    treffer = dokumentiert & live
    fehlend = dokumentiert - live
    undokumentiert = live - dokumentiert

    def titel(url: str) -> str:
        return snap.demo_title.get(url, url)

    return {
        "anzahl_dokumentiert": len(dokumentiert),
        "anzahl_live": len(live),
        "anzahl_treffer": len(treffer),
        "anzahl_fehlend": len(fehlend),
        "anzahl_undokumentiert": len(undokumentiert),
        "beispiele_fehlend": [(titel(s), titel(z)) for s, z in sorted(fehlend)[:8]],
        "beispiele_undokumentiert": [(titel(s), titel(z)) for s, z in sorted(undokumentiert)[:8]],
    }
