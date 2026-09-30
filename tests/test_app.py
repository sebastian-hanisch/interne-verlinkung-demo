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
    assert len(at.metric) == 3
    werte = [m.value for m in at.metric]
    assert all(w for w in werte)


def test_app_hat_zwei_ueberschriften_fuer_diagnose_und_wirkungsanalyse():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    header_texte = " ".join(h.value for h in at.header)
    assert "Diagnose" in header_texte
    assert "Wirkungsanalyse" in header_texte
