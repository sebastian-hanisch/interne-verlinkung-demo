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
