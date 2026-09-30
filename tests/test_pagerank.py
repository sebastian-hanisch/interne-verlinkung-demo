import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graph import build_base_graph, load_snapshot, pagerank
from optimierung import exakt, greedy, groesste_seiten_pagerank_zuerst, target_score, zufaellig

SNAP = load_snapshot()


def test_pagerank_summe_ist_eins():
    g = build_base_graph(SNAP)
    pr = pagerank(g)
    assert abs(sum(pr.values()) - 1.0) < 1e-6


def test_alle_knoten_haben_einen_rang():
    g = build_base_graph(SNAP)
    pr = pagerank(g)
    assert set(pr) == set(g.nodes)
    assert all(v > 0 for v in pr.values())


def test_jede_demo_hat_genau_die_erhobenen_rueckl_und_querlinks():
    g = build_base_graph(SNAP)
    for url in SNAP.demo_urls:
        targets = set(g.out[url])
        assert set(SNAP.demo_backlink_targets) <= targets
        assert set(SNAP.demo_cross_links.get(url, [])) <= targets


def test_zusaetzlicher_ruecklink_erhoeht_den_pagerank_der_zielseite():
    ziel = "konzepte-lineare-programmierung.html"
    ohne = target_score(SNAP, ziel, frozenset())
    irgendeine_demo = SNAP.demo_urls[0]
    mit = target_score(SNAP, ziel, frozenset({irgendeine_demo}))
    assert mit > ohne


def test_greedy_erreicht_mindestens_referrer_heuristik_auf_kleinem_kandidatenpool():
    ziel = "konzepte-lineare-programmierung.html"
    kandidaten = SNAP.demo_urls[:20]
    budget = 2
    ref = groesste_seiten_pagerank_zuerst(SNAP, ziel, budget, kandidaten)
    gr = greedy(SNAP, ziel, budget, kandidaten)
    assert target_score(SNAP, ziel, frozenset(gr)) >= target_score(SNAP, ziel, frozenset(ref)) - 1e-12


def test_exakt_ist_nie_schlechter_als_greedy_auf_demselben_kleinen_pool():
    ziel = "konzepte-lineare-programmierung.html"
    kandidaten = SNAP.demo_urls[:10]
    budget = 2
    gr = greedy(SNAP, ziel, budget, kandidaten)
    ex = exakt(SNAP, ziel, budget, kandidaten)
    assert target_score(SNAP, ziel, frozenset(ex)) >= target_score(SNAP, ziel, frozenset(gr)) - 1e-12


def test_zufaellig_liefert_budget_viele_verschiedene_demos():
    ziel = "konzepte-lineare-programmierung.html"
    kandidaten = SNAP.demo_urls[:30]
    ausgewaehlt = zufaellig(SNAP, ziel, 5, kandidaten, seed=1)
    assert len(ausgewaehlt) == 5
    assert ziel not in ausgewaehlt


def test_ist_zustand_heute_zeigt_das_bekannte_ungleichgewicht():
    """Regressionstest gegen den am 2026-09-30 erhobenen Ist-Zustand: die Konzepte-Linien liegen im
    Schnitt deutlich unter Start-/Kontaktseite, weil alle 300 Demos einheitlich dorthin zurueckverlinken."""
    g = build_base_graph(SNAP)
    pr = pagerank(g)
    linien = [p for p in SNAP.pages if p.startswith("konzepte-") and p != "konzepte.html"]
    avg_linien = sum(pr[p] for p in linien) / len(linien)
    assert pr["index.html"] > avg_linien * 10
