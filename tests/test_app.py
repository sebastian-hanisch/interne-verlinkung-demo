import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def test_app_startet_ohne_fehler():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert not at.exception


def test_app_zeigt_ist_zustand_und_bestes_verfahren():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    assert len(at.metric) == 2
    werte = [float(m.value) for m in at.metric]
    assert all(w > 0 for w in werte)


def test_zielseite_wechseln_aendert_die_metrik():
    at = AppTest.from_file(APP, default_timeout=60)
    at.run()
    erster_wert = at.metric[0].value
    at.selectbox[0].select("kuerzeste-wege").run()
    assert not at.exception
    assert at.metric[0].value != erster_wert
