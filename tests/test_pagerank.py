import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graph import build_base_graph, build_graph_mit_fix, load_snapshot, pagerank
from optimierung import exakt, greedy, groesste_seiten_pagerank_zuerst, target_score, zufaellig

SNAP = load_snapshot()
ZIEL = "konzepte-lineare-programmierung.html"


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


def test_relevante_kandidaten_sind_nur_eigene_und_crosslink_verwandte_demos():
    eigene, nachbarn = SNAP.relevant_candidates(ZIEL)
    assert eigene, "jede geprüfte Linie sollte eigene Demos haben"
    for url in eigene:
        assert SNAP.demo_home_page[url] == ZIEL
    nachbar_linien = set(SNAP.crosslink_map.get(ZIEL, []))
    for url in nachbarn:
        assert SNAP.demo_home_page[url] in nachbar_linien


def test_keine_beliebige_demo_landet_ungefragt_im_kandidatenpool():
    _, nachbarn = SNAP.relevant_candidates(ZIEL)
    irrelevante_demo = next(u for u, home in SNAP.demo_home_page.items()
                             if home != ZIEL and home not in SNAP.crosslink_map.get(ZIEL, []))
    assert irrelevante_demo not in nachbarn


def test_basis_fix_verlinkt_alle_eigenen_demos_ohne_wahl():
    eigene, _ = SNAP.relevant_candidates(ZIEL)
    g = build_graph_mit_fix(SNAP, ZIEL, frozenset())
    for url in eigene:
        assert ZIEL in g.out[url]


def test_basis_fix_erhoeht_den_pagerank_gegenueber_dem_ist_zustand():
    ist = pagerank(build_base_graph(SNAP))[ZIEL]
    mit_fix = target_score(SNAP, ZIEL, frozenset())
    assert mit_fix > ist


def test_zusaetzlicher_nachbar_ruecklink_erhoeht_den_pagerank_weiter():
    _, nachbarn = SNAP.relevant_candidates(ZIEL)
    ohne_nachbarn = target_score(SNAP, ZIEL, frozenset())
    mit_einem_nachbarn = target_score(SNAP, ZIEL, frozenset({nachbarn[0]}))
    assert mit_einem_nachbarn > ohne_nachbarn


def test_greedy_erreicht_mindestens_referrer_heuristik():
    _, nachbarn = SNAP.relevant_candidates(ZIEL)
    ist_pr = pagerank(build_base_graph(SNAP))
    budget = 2
    ref = groesste_seiten_pagerank_zuerst(SNAP, ZIEL, budget, nachbarn, ist_pr)
    gr = greedy(SNAP, ZIEL, budget, nachbarn)
    assert target_score(SNAP, ZIEL, frozenset(gr)) >= target_score(SNAP, ZIEL, frozenset(ref)) - 1e-12


def test_exakt_ist_nie_schlechter_als_greedy_auf_demselben_kleinen_pool():
    _, nachbarn = SNAP.relevant_candidates(ZIEL)
    pool = nachbarn[:10]
    budget = 2
    gr = greedy(SNAP, ZIEL, budget, pool)
    ex = exakt(SNAP, ZIEL, budget, pool)
    assert target_score(SNAP, ZIEL, frozenset(ex)) >= target_score(SNAP, ZIEL, frozenset(gr)) - 1e-12


def test_zufaellig_liefert_budget_viele_verschiedene_nachbarn():
    _, nachbarn = SNAP.relevant_candidates(ZIEL)
    ausgewaehlt = zufaellig(nachbarn, min(5, len(nachbarn)), seed=1)
    assert len(ausgewaehlt) == min(5, len(nachbarn))
    assert ausgewaehlt <= set(nachbarn)


def test_ist_zustand_heute_zeigt_das_bekannte_ungleichgewicht():
    """Regressionstest gegen den am 2026-09-30 erhobenen Ist-Zustand: die Konzepte-Linien liegen im
    Schnitt deutlich unter Start-/Kontaktseite, weil alle 300 Demos einheitlich dorthin zurueckverlinken."""
    pr = pagerank(build_base_graph(SNAP))
    linien = [p for p in SNAP.pages if p.startswith("konzepte-") and p != "konzepte.html"]
    avg_linien = sum(pr[p] for p in linien) / len(linien)
    assert pr["index.html"] > avg_linien * 10
