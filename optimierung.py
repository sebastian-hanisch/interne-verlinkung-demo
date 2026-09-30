"""Das eigentliche Optimierungsproblem dieser Demo - inhaltlich eingeschränkt, nicht auf beliebige
Demos: Jede Demo der Ziel-Linie selbst bekommt immer einen Rücklink auf ihre eigene Linie (das ist
Korrektheit, keine Wahl). Offen ist nur, welche Demos aus CROSSLINK-VERWANDTEN Linien - also
inhaltlich schon dokumentiert verbundenen Themen - zusätzlich einen Rücklink auf die Zielseite
bekommen sollten, wenn ein Budget verhindert, dass jede verwandte Demo jede Nachbarlinie erwähnt.

Eine Demo, die inhaltlich nichts mit der Zielseite zu tun hat, gehört NIE zum Kandidatenpool -
ein Rücklink ohne inhaltlichen Bezug wäre für Besucher irreführend und liest sich wie
Linkmanipulation, nicht wie eine echte Empfehlung.

Die verbleibende Auswahl unter den relevanten Nachbar-Demos ist trotzdem ein Optimierungsproblem:
der Grenzgewinn einer weiteren Demo nimmt ab, je mehr schon gewählt sind (dieselbe submodulare
Struktur wie bei Facility Location oder Einflussmaximierung in Netzwerken), deshalb lohnt sich
Greedy gegenüber einer erschöpfenden Suche.
"""

from __future__ import annotations

import itertools
import random

from graph import Snapshot, build_graph_mit_fix, pagerank


def target_score(snap: Snapshot, target: str, gewaehlte_nachbarn: frozenset[str]) -> float:
    g = build_graph_mit_fix(snap, target, gewaehlte_nachbarn)
    return pagerank(g)[target]


def zufaellig(nachbarn: list[str], budget: int, seed: int = 0) -> frozenset[str]:
    rng = random.Random(seed)
    return frozenset(rng.sample(nachbarn, min(budget, len(nachbarn))))


def groesste_seiten_pagerank_zuerst(snap: Snapshot, target: str, budget: int, nachbarn: list[str],
                                     ist_pagerank: dict[str, float]) -> frozenset[str]:
    """Heuristik ohne Rückkopplung: wähle die Nachbar-Demos, deren verweisende Seite schon jetzt den
    höchsten PageRank hat - ohne mitzurechnen, wie sich die Wahl selbst auswirkt. Kontrast zu Greedy."""
    scored = []
    for url in nachbarn:
        referrer_pr = max((ist_pagerank.get(p, 0.0) for p in snap.demo_referrers.get(url, [])), default=0.0)
        scored.append((referrer_pr, url))
    scored.sort(reverse=True)
    return frozenset(url for _, url in scored[:budget])


def greedy(snap: Snapshot, target: str, budget: int, nachbarn: list[str]) -> frozenset[str]:
    """Iterativ: wähle in jedem Schritt die eine Nachbar-Demo, die den PageRank der Zielseite JETZT
    am stärksten erhöht, und rechne für den nächsten Schritt mit dieser Wahl weiter."""
    chosen: set[str] = set()
    for _ in range(min(budget, len(nachbarn))):
        best_gain, best_url = -1.0, None
        for url in nachbarn:
            if url in chosen:
                continue
            score = target_score(snap, target, frozenset(chosen | {url}))
            if score > best_gain:
                best_gain, best_url = score, url
        if best_url is None:
            break
        chosen.add(best_url)
    return frozenset(chosen)


def exakt(snap: Snapshot, target: str, budget: int, nachbarn: list[str]) -> frozenset[str]:
    """Erschöpfende Suche über alle Teilmengen der Größe budget aus den Nachbar-Demos - dank der
    inhaltlichen Einschränkung ist dieser Pool von vornherein klein genug (typischerweise unter 20
    Demos je Linie), keine künstliche Pool-Begrenzung mehr nötig."""
    best_score, best_subset = -1.0, frozenset()
    for combo in itertools.combinations(nachbarn, min(budget, len(nachbarn))):
        subset = frozenset(combo)
        score = target_score(snap, target, subset)
        if score > best_score:
            best_score, best_subset = score, subset
    return best_subset
