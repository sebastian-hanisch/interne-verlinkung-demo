"""Lädt den Verlinkungs-Schnappschuss von sebastianhanisch.net und baut daraus den PageRank-Graphen.

Der Schnappschuss (data/linkgraph_snapshot.json, Stand siehe Feld "stand") enthält drei echte,
am 2026-09-30 erhobene Bestandteile: die internen Links zwischen den 50 HTML-Seiten der Website,
welche Seiten auf welche der 300 Demo-URLs verweisen, und - durch Abruf aller 300 app.py-Dateien
auf GitHub - den tatsächlichen Rücklink-Fußzeilentext jeder Demo (einheitlich: Startseite + Kontakt)
sowie 69 echte Demo-zu-Demo-Querverlinkungen. Keine synthetischen Daten.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "linkgraph_snapshot.json"


@dataclass
class Snapshot:
    stand: str
    pages: list[str]
    page_edges: dict[str, list[str]]
    demo_referrers: dict[str, list[str]]
    demo_home_page: dict[str, str]
    demo_title: dict[str, str]
    demo_cross_links: dict[str, list[str]]
    demo_backlink_targets: list[str]
    crosslink_map: dict[str, list[str]]

    @property
    def demo_urls(self) -> list[str]:
        return sorted(self.demo_referrers)

    def demos_of(self, page: str) -> list[str]:
        """Alle Demo-URLs, deren Heimatseite (demo_registry) genau `page` ist."""
        return sorted(u for u, home in self.demo_home_page.items() if home == page)

    def relevant_candidates(self, target: str) -> tuple[list[str], list[str]]:
        """(eigene Demos der Ziel-Linie, Demos crosslink-verwandter Linien) - nur diese beiden
        Gruppen sind inhaltlich plausible Rücklink-Kandidaten fuer `target`, nicht beliebige Demos."""
        eigene = self.demos_of(target)
        nachbarn: list[str] = []
        for nachbar_linie in self.crosslink_map.get(target, []):
            nachbarn.extend(self.demos_of(nachbar_linie))
        return eigene, sorted(nachbarn)


def load_snapshot(path: Path = DATA_PATH) -> Snapshot:
    raw = json.loads(path.read_text(encoding="utf-8"))
    crosslink_map = json.loads((path.parent / "crosslink_map.json").read_text(encoding="utf-8"))
    return Snapshot(
        stand=raw["stand"],
        pages=raw["pages"],
        page_edges=raw["page_edges"],
        demo_referrers=raw["demo_referrers"],
        demo_home_page=raw["demo_home_page"],
        demo_title=raw["demo_title"],
        demo_cross_links=raw["demo_cross_links"],
        demo_backlink_targets=raw["demo_backlink_targets"],
        crosslink_map=crosslink_map,
    )


@dataclass
class Graph:
    """Gerichteter Graph für PageRank: Knoten sind Seitennamen und Demo-URLs, Kanten als Adjazenzliste."""

    nodes: list[str]
    out: dict[str, list[str]] = field(default_factory=dict)

    def add_edge(self, src: str, dst: str) -> None:
        self.out.setdefault(src, []).append(dst)

    def copy(self) -> "Graph":
        return Graph(nodes=list(self.nodes), out={k: list(v) for k, v in self.out.items()})


def build_base_graph(snap: Snapshot, extra_backlinks: dict[str, str] | None = None) -> Graph:
    """Baut den Graphen: interne Seiten-Links + Seite->Demo + Demo->Startseite/Kontakt (immer) +
    Demo->Demo-Querlinks (immer, echt erhoben) + optional zusätzliche Demo->Zielseite-Rücklinks
    (extra_backlinks: demo_url -> zusätzliche Zielseite), unabhängig vom bestehenden Rücklink."""
    g = Graph(nodes=list(snap.pages) + snap.demo_urls)
    for src, targets in snap.page_edges.items():
        for t in targets:
            g.add_edge(src, t)
    for url, referrers in snap.demo_referrers.items():
        for r in referrers:
            g.add_edge(r, url)
        for target_page in snap.demo_backlink_targets:
            g.add_edge(url, target_page)
        for other in snap.demo_cross_links.get(url, []):
            g.add_edge(url, other)
    if extra_backlinks:
        for url, extra_target in extra_backlinks.items():
            g.add_edge(url, extra_target)
    return g


def build_graph_mit_fix(snap: Snapshot, target: str, gewaehlte_nachbarn: frozenset[str] = frozenset()) -> Graph:
    """Baugrundlage fuer alle Vergleiche ab dem Basis-Fix: JEDE Demo der Ziel-Linie selbst bekommt
    automatisch den (aktuell fehlenden) Rücklink auf ihre eigene Linie - das ist keine Optimierung,
    sondern schlicht Korrektheit, siehe relevant_candidates(). Die eigentliche Auswahlfrage betrifft
    nur `gewaehlte_nachbarn`: Demos crosslink-verwandter Linien, die zusätzlich auf `target`
    zurückverlinken."""
    eigene, _ = snap.relevant_candidates(target)
    extra = {url: target for url in eigene} | {url: target for url in gewaehlte_nachbarn}
    return build_base_graph(snap, extra_backlinks=extra)


def pagerank(g: Graph, damping: float = 0.85, iterations: int = 100) -> dict[str, float]:
    """Standard-Power-Iteration mit Dangling-Node-Behandlung (Senken verteilen ihren Rang gleichmäßig)."""
    nodes = g.nodes
    n = len(nodes)
    idx = {p: i for i, p in enumerate(nodes)}
    out_idx = [[idx[t] for t in g.out.get(p, [])] for p in nodes]
    outdeg = [len(o) for o in out_idx]

    pr = [1.0 / n] * n
    for _ in range(iterations):
        new_pr = [(1 - damping) / n] * n
        dangling_sum = sum(pr[i] for i in range(n) if outdeg[i] == 0)
        for i in range(n):
            new_pr[i] += damping * dangling_sum / n
        for i in range(n):
            if outdeg[i] == 0:
                continue
            share = pr[i] / outdeg[i]
            for j in out_idx[i]:
                new_pr[j] += damping * share
        pr = new_pr
    return dict(zip(nodes, pr))
