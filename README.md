# Interne Verlinkung optimieren – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-interne-verlinkung-demo.streamlit.app/)**

Konzepte-Demo der **Graphen-und-Netzwerke-Linie** der "Konzepte"-Reihe für die Website
"Sebastian Hanisch – Operations Research und Machine Learning": anders als das übliche Muster
der Linie (ein wachsendes künstliches Beispiel) rechnet diese Demo mit dem **echten**
Verlinkungsgraphen von sebastianhanisch.net selbst – keine synthetischen Daten.

## Ausgangsbefund (Stand 2026-09-30, vollständig erhoben, keine Stichprobe)

Alle 300 Demos der Website verlinken im laufenden `app.py`-Footer einheitlich auf
`sebastianhanisch.net/` und `/kontakt.html` zurück – unabhängig davon, zu welcher Konzepte-Linie
oder Themenseite sie inhaltlich gehören. Zusätzlich gibt es 69 echte Demo-zu-Demo-Querverlinkungen
in 35 Repos, die der Baureihenfolge der jeweiligen Linie folgen (z. B. Hill Climbing → Simulated
Annealing → Tabu Search).

Ergebnis: **66,9 % des gesamten PageRank der Website hängt an den 300 externen Demo-Knoten**, und
der zurückfließende Teil konzentriert sich fast vollständig auf zwei Seiten (Startseite, Kontakt)
statt auf die einzelne Konzepte-Linie, zu der die Demo eigentlich gehört – eine Dijkstra-Demo
schickt keine Linkkraft zurück zur Kürzeste-Wege-Seite.

## Das Optimierungsproblem

Bei einem festen Budget B, wie vielen Demos zusätzlich zum bestehenden Rücklink auch einer
gewählten Zielseite (z. B. einer Konzepte-Linie) verlinken darf – welche B Demos sollte man wählen,
um deren PageRank möglichst stark zu erhöhen?

Der Grenzgewinn einer weiteren Demo nimmt ab, je mehr schon gewählt sind (die zusätzliche
Linkkraft überschneidet sich mit der schon vorhandenen) – dieselbe Struktur wie bei Facility
Location oder Einflussmaximierung in Netzwerken. Vier Verfahren im Vergleich:

| Verfahren | Idee |
|---|---|
| Zufällig | Baseline ohne jede Überlegung |
| Referrer-Heuristik | wählt Demos, deren verweisende Seite schon jetzt hohen PageRank hat – ohne Rückkopplung |
| **Greedy** | wählt iterativ die Demo mit dem größten Grenzgewinn, neu bewertet nach jeder Wahl |
| Exakt | erschöpfende Suche über alle Teilmengen – nur auf einem kleinen Kandidatenpool zumutbar (bei 300 Demos und Budget 3 wären es über 4,4 Millionen Teilmengen) |

## Daten

`data/linkgraph_snapshot.json` enthält den vollständigen Schnappschuss: die internen Links
zwischen den 50 HTML-Seiten von sebastianhanisch.net, welche Seiten auf welche der 300 Demo-URLs
verweisen, und – durch Abruf aller 300 `app.py`-Dateien der Demo-Repos über die GitHub-API – den
tatsächlichen Rücklink-Fußzeilentext und die 69 echten Demo-zu-Demo-Querverlinkungen. Erhoben am
2026-09-30, nicht künstlich erzeugt.

## Was die Demo zeigt

Zielseite (eine der 26 Konzepte-Linien), Budget und Kandidatenpool-Größe wählbar; die vier
Verfahren werden live berechnet und als Balkendiagramm verglichen, dazu die konkret gewählten
Demos je Verfahren und eine kurze Einordnung, warum Greedy hier eine begründete statt nur bequeme
Wahl ist.

## Dateien

- `graph.py` – lädt den Schnappschuss, baut den PageRank-Graphen, berechnet PageRank
- `optimierung.py` – die vier Auswahlverfahren (Zufällig, Referrer-Heuristik, Greedy, Exakt)
- `app.py` – die Streamlit-Oberfläche
- `tests/` – Korrektheitstests (PageRank-Summe, Greedy ≥ Referrer-Heuristik, Exakt ≥ Greedy, AppTest-Smoke-Tests)

## Lokal ausführen

```
pip install -r requirements.txt
streamlit run app.py
```

## Verifikation

```
pip install pytest
pytest
```

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) –
Operations Research und Machine Learning.
