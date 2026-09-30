import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_app_startet_ohne_fehler():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception


def test_app_zeigt_diagnose_metriken():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert len(at.metric) == 6
    werte = [m.value for m in at.metric]
    assert all(w for w in werte)


def test_app_hat_drei_ueberschriften_fuer_die_drei_abschnitte():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    header_texte = " ".join(h.value for h in at.header)
    assert "1. Diagnose" in header_texte
    assert "2." in header_texte and "Wirkungsanalyse" in header_texte
    assert "3." in header_texte and "Baureihenfolge" in header_texte
