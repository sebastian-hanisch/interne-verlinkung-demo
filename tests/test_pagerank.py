import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analyse import groesste_gewinner, index_kontakt_anteil, konzepte_linien, linien_mittel
from graph import build_base_graph, build_mit_basis_fix, build_mit_vollem_fix, load_snapshot, pagerank

SNAP = load_snapshot()


def test_pagerank_summe_ist_eins_in_allen_drei_szenarien():
    for builder in (build_base_graph, build_mit_basis_fix, build_mit_vollem_fix):
        g = builder(SNAP)
        pr = pagerank(g)
        assert abs(sum(pr.values()) - 1.0) < 1e-6


def test_alle_knoten_haben_einen_rang():
    g = build_base_graph(SNAP)
    pr = pagerank(g)
    assert set(pr) == set(g.nodes)
    assert all(v > 0 for v in pr.values())


def test_ist_zustand_rueckl_sind_nur_startseite_und_kontakt():
    g = build_base_graph(SNAP)
    for url in SNAP.demo_urls:
        assert set(SNAP.demo_backlink_targets) <= set(g.out[url])


def test_basis_fix_verlinkt_jede_demo_auf_ihre_eigene_heimatseite():
    g = build_mit_basis_fix(SNAP)
    for url, home in SNAP.demo_home_page.items():
        assert home in g.out[url]


def test_voller_fix_verlinkt_zusaetzlich_auf_dokumentierte_crosslink_nachbarn():
    g = build_mit_vollem_fix(SNAP)
    ziel = "konzepte-lineare-programmierung.html"
    nachbar_linien = set(SNAP.crosslink_map.get(ziel, []))
    demos_anderer_linien_mit_ziel_als_nachbar = [
        u for u, home in SNAP.demo_home_page.items()
        if ziel in SNAP.crosslink_map.get(home, [])
    ]
    assert demos_anderer_linien_mit_ziel_als_nachbar, "Testvoraussetzung: es muss mind. eine Nachbar-Demo geben"
    for url in demos_anderer_linien_mit_ziel_als_nachbar:
        assert ziel in g.out[url]


def test_relevante_kandidaten_sind_nur_eigene_und_crosslink_verwandte_demos():
    ziel = "konzepte-lineare-programmierung.html"
    eigene, nachbarn = SNAP.relevant_candidates(ziel)
    assert eigene
    for url in eigene:
        assert SNAP.demo_home_page[url] == ziel
    nachbar_linien = set(SNAP.crosslink_map.get(ziel, []))
    for url in nachbarn:
        assert SNAP.demo_home_page[url] in nachbar_linien


def test_basis_fix_erhoeht_den_pagerank_der_konzepte_linien_im_schnitt():
    ist = pagerank(build_base_graph(SNAP))
    mit_fix = pagerank(build_mit_basis_fix(SNAP))
    assert linien_mittel(SNAP, mit_fix) > linien_mittel(SNAP, ist)


def test_voller_fix_erhoeht_den_pagerank_mindestens_so_stark_wie_basis_fix():
    mit_basis = pagerank(build_mit_basis_fix(SNAP))
    mit_voll = pagerank(build_mit_vollem_fix(SNAP))
    assert linien_mittel(SNAP, mit_voll) >= linien_mittel(SNAP, mit_basis)


def test_index_kontakt_anteil_sinkt_mit_jedem_fix_schritt():
    """Die Fixes ändern nicht, wie viel PageRank insgesamt an den Demo-Knoten hängt (das hängt an den
    eingehenden Links, die unangetastet bleiben), sondern WOHIN die zurückfließende Kraft geht -
    weg von den zwei generischen Seiten, hin zu den einzelnen Konzepte-Linien."""
    ist = index_kontakt_anteil(pagerank(build_base_graph(SNAP)))
    basis = index_kontakt_anteil(pagerank(build_mit_basis_fix(SNAP)))
    voll = index_kontakt_anteil(pagerank(build_mit_vollem_fix(SNAP)))
    assert ist > basis > voll


def test_groesste_gewinner_liefert_n_eintraege_absteigend_sortiert():
    ist = pagerank(build_base_graph(SNAP))
    voll = pagerank(build_mit_vollem_fix(SNAP))
    top = groesste_gewinner(SNAP, ist, voll, n=5)
    assert len(top) == 5
    zuwaechse = [nachher - vorher for _, vorher, nachher in top]
    assert zuwaechse == sorted(zuwaechse, reverse=True)


def test_ist_zustand_heute_zeigt_das_bekannte_ungleichgewicht():
    """Regressionstest gegen den am 2026-09-30 erhobenen Ist-Zustand: die Konzepte-Linien liegen im
    Schnitt deutlich unter der Startseite, weil alle 300 Demos einheitlich dorthin zurueckverlinken."""
    pr = pagerank(build_base_graph(SNAP))
    assert pr["index.html"] > linien_mittel(SNAP, pr) * 10
