"""Das eigentliche Optimierungsproblem dieser Demo: Bei festem Budget B, welche B Demos sollten
zusätzlich zu ihrem bestehenden Rücklink (Startseite + Kontakt) auch auf eine gewählte Zielseite
(z. B. eine Konzepte-Linie) zurückverlinken, um deren PageRank möglichst stark zu erhöhen?

Das ist ein Submodulares-Optimierungs-Problem im selben Sinne wie Facility Location oder
Einflussmaximierung in Netzwerken (siehe die Konzepte-Linien Standortplanung und Graphen und
Netzwerke dieser Website): der Grenzgewinn einer weiteren Demo nimmt ab, je mehr schon gewählt
sind, weil sich die zusätzliche Linkkraft mit der schon vorhandenen überschneidet. Deshalb ist
Greedy hier eine gute Wahl, nicht nur eine bequeme.
"""

from __future__ import annotations

import itertools
import random

from graph import Graph, Snapshot, build_base_graph, pagerank


def target_score(snap: Snapshot, target: str, chosen: frozenset[str]) -> float:
    extra = {url: target for url in chosen}
    g = build_base_graph(snap, extra_backlinks=extra)
    return pagerank(g)[target]


def zufaellig(snap: Snapshot, target: str, budget: int, candidates: list[str], seed: int = 0) -> frozenset[str]:
    rng = random.Random(seed)
    pool = [c for c in candidates if c != target]
    return frozenset(rng.sample(pool, min(budget, len(pool))))


def groesste_seiten_pagerank_zuerst(snap: Snapshot, target: str, budget: int, candidates: list[str]) -> frozenset[str]:
    """Heuristik ohne Rückkopplung: wähle die Demos, deren VERWEISENDE Seiten schon jetzt den
    höchsten PageRank haben - in der Annahme, "wichtige Seiten verlinken wichtige Demos". Bewusst
    naiv (rechnet nicht mit, wie sich die Wahl selbst auf den PageRank auswirkt), als Kontrast zu
    Greedy."""
    base_pr = pagerank(build_base_graph(snap))
    scored = []
    for url in candidates:
        if url == target:
            continue
        referrer_pr = max((base_pr.get(p, 0.0) for p in snap.demo_referrers.get(url, [])), default=0.0)
        scored.append((referrer_pr, url))
    scored.sort(reverse=True)
    return frozenset(url for _, url in scored[:budget])


def greedy(snap: Snapshot, target: str, budget: int, candidates: list[str]) -> frozenset[str]:
    """Iterativ: wähle in jedem Schritt die eine Demo, die den PageRank der Zielseite JETZT am
    stärksten erhöht, und rechne für den nächsten Schritt mit dieser Wahl weiter (Grenzgewinn wird
    neu bewertet, nicht nur einmal vorab geschätzt wie bei der Referrer-Heuristik)."""
    chosen: set[str] = set()
    pool = [c for c in candidates if c != target]
    for _ in range(min(budget, len(pool))):
        best_gain, best_url = -1.0, None
        for url in pool:
            if url in chosen:
                continue
            score = target_score(snap, target, frozenset(chosen | {url}))
            if score > best_gain:
                best_gain, best_url = score, url
        if best_url is None:
            break
        chosen.add(best_url)
    return frozenset(chosen)


def exakt(snap: Snapshot, target: str, budget: int, candidates: list[str]) -> frozenset[str]:
    """Erschöpfende Suche über alle Teilmengen der Größe budget - nur für kleine Kandidatenmengen
    und kleines Budget zumutbar, dient als exakte Referenz für die Heuristiken."""
    pool = [c for c in candidates if c != target]
    best_score, best_subset = -1.0, frozenset()
    for combo in itertools.combinations(pool, min(budget, len(pool))):
        subset = frozenset(combo)
        score = target_score(snap, target, subset)
        if score > best_score:
            best_score, best_subset = score, subset
    return best_subset
