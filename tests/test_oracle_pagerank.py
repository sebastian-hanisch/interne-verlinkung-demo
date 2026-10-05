"""Unabhängiges Orakel für PageRank und die Diagnose-Zahlen: PageRank per direktem Lösen des linearen Gleichungssystems (I - d*M) x = (1-d)/n * 1 (anderer Rechenweg als die Power-Iteration;
Senken verteilen gleichmäßig) und gegen networkx.pagerank; Diagramm-gegen-Live-Zählung direkt aus den Rohdaten (JSON) statt über analyse.py."""

import json
import random

import numpy as np
import pytest

import analyse as AN
import graph as G


def _solve(g, d=0.85):
    nodes = g.nodes
    idx = {p: i for i, p in enumerate(nodes)}
    n = len(nodes)
    m = np.zeros((n, n))
    for s, ts in g.out.items():
        for t in ts:
            m[idx[t], idx[s]] += 1.0
    col = m.sum(axis=0)
    for j in range(n):
        if col[j] == 0:
            m[:, j] = 1.0 / n                        # Senke: gleichmäßig auf alle Knoten
        else:
            m[:, j] /= col[j]
    x = np.linalg.solve(np.eye(n) - d * m, np.full(n, (1 - d) / n))
    return {p: x[idx[p]] for p in nodes}


def test_pagerank_matches_linear_solve_on_random_small_graphs_with_sinks():
    rng = random.Random(4)
    for _ in range(200):
        n = rng.randint(1, 12)
        nodes = [f"v{i}" for i in range(n)]
        g = G.Graph(nodes=nodes)
        for u in nodes:
            if rng.random() < 0.8:                  # mit Wahrscheinlichkeit 0.2 eine Senke
                for v in rng.sample(nodes, rng.randint(0, min(n, 4))):
                    if v != u:
                        g.add_edge(u, v)
        got, want = G.pagerank(g), _solve(g)
        assert sum(got.values()) == pytest.approx(1.0, abs=1e-12)
        assert max(abs(got[p] - want[p]) for p in nodes) < 1e-6


def test_pagerank_on_the_three_scenario_graphs_matches_linear_solve_and_networkx():
    snap = G.load_snapshot()
    for g in (G.build_base_graph(snap), G.build_mit_basis_fix(snap), G.build_mit_vollem_fix(snap)):
        got, want = G.pagerank(g), _solve(g)
        assert max(abs(got[p] - want[p]) for p in g.nodes) < 1e-9
    nx = pytest.importorskip("networkx")
    g = G.build_base_graph(snap)
    mg = nx.MultiDiGraph()
    mg.add_nodes_from(g.nodes)
    for s, ts in g.out.items():
        for t in ts:
            mg.add_edge(s, t)
    ref = nx.pagerank(mg, alpha=0.85, tol=1e-13, max_iter=1000)
    got = G.pagerank(g)
    assert max(abs(got[p] - ref[p]) for p in g.nodes) < 1e-9


def test_diagnose_counts_and_readme_numbers_from_raw_data():
    base = G.DATA_PATH.parent
    raw = json.loads(G.DATA_PATH.read_text(encoding="utf-8"))
    dag = json.loads((base / "dag_edges.json").read_text(encoding="utf-8"))
    doc = {(e["quelle_url"], e["ziel_url"]) for e in dag}
    live = {(s, t) for s, ts in raw["demo_cross_links"].items() for t in ts}
    d = AN.dag_vs_live_diagnose(G.load_snapshot())
    assert (d["anzahl_dokumentiert"], d["anzahl_live"], d["anzahl_treffer"], d["anzahl_fehlend"], d["anzahl_undokumentiert"]) == (len(doc), len(live), len(doc & live), len(doc - live), len(live - doc))
    snap = G.load_snapshot()
    pr = G.pagerank(G.build_base_graph(snap))
    linien = [p for p in raw["pages"] if p.startswith("konzepte-") and p != "konzepte.html"]
    assert len(linien) == 26
    assert (pr["index.html"] + pr["kontakt.html"]) == pytest.approx(0.2211, abs=5e-5)
    assert sum(pr[p] for p in linien) == pytest.approx(0.0671, abs=5e-5)
    assert sum(pr[p] for p in linien) / 26 == pytest.approx(0.00258, abs=5e-6)
