# Interne Verlinkung: Diagnose und Wirkungsanalyse – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-interne-verlinkung-demo.streamlit.app/)**

Analyse-Karte der **Graphen-und-Netzwerke-Linie** der "Konzepte"-Reihe für die Website
"Sebastian Hanisch – Operations Research und Machine Learning": anders als eine Optimierung
(mehrere Verfahren im Vergleich) ist das hier eine Netzwerkanalyse am echten Fall – passend zu den
anderen Analyse-Karten der Linie (Zentralität, Strukturkennzahlen): eine Kennzahl berechnen und
interpretieren, keine Verfahren gegeneinander optimieren. Rechnet mit dem **echten**
Verlinkungsgraphen von sebastianhanisch.net selbst, nicht mit synthetischen Daten.

## Diagnose (Stand 2026-09-30, vollständig erhoben, keine Stichprobe)

Alle 300 Demos der Website verlinken im laufenden `app.py`-Footer einheitlich auf
`sebastianhanisch.net/` und `/kontakt.html` zurück – unabhängig davon, zu welcher Konzepte-Linie
sie inhaltlich gehören. Dazu kommen 69 echte Demo-zu-Demo-Querverlinkungen in 35 Repos, die der
Baureihenfolge der jeweiligen Linie folgen (z. B. Hill Climbing → Simulated Annealing → Tabu
Search).

Ergebnis: **index.html und kontakt.html halten zusammen 22,1 % des gesamten PageRank der Website –
mehr als alle 26 Konzepte-Linien zusammen (6,7 %)**, obwohl jede Linie eigene Demos hat, die
inhaltlich genau zu ihr gehören. Die Linkkraft, die die Demos zurückgeben, landet fast vollständig
bei zwei generischen Seiten statt bei der Linie, die sie tatsächlich verdient hätte.

## Wirkungsanalyse: zwei feste Szenarien, keine Optimierung

**Wichtig:** Das hier ist keine Auswahl unter beliebigen Alternativen. Eine frühere Fassung dieser
Demo hat versucht, unter allen 300 Demos die "optimale" Teilmenge für einen Rücklink auszuwählen –
das hätte z. B. dazu führen können, dass eine Dijkstra-Demo "optimal" auf eine völlig unverwandte
Seite verlinkt, nur weil das irgendwo den PageRank erhöht. Das wäre für Besucher irreführend und
liest sich wie Linkmanipulation, nicht wie eine echte Empfehlung.

Stattdessen zwei feste, inhaltlich begründete Korrekturen – reine Korrektheit, keine Wahl:

1. **Basis-Fix:** jede Demo verlinkt zusätzlich auf ihre eigene Heimatseite (Konzepte-Linie) zurück
   – sie gehört laut `demo_registry.py` ohnehin genau dorthin.
2. **Voller Fix:** zusätzlich verlinkt jede Demo auch auf die Linien, die laut den echten
   `crosslinks`-Feldern der Website mit ihrer eigenen Linie verwandt sind.

| Szenario | Ø PageRank je Konzepte-Linie | Anteil auf index.html + kontakt.html |
|---|---|---|
| Ist-Zustand | 0,00258 | 22,1 % |
| Basis-Fix | 0,00475 (+83,8 %) | 16,9 % |
| Voller Fix | 0,00766 (+196,6 %) | 12,4 % |

Der Gesamtanteil, der überhaupt an den 300 Demo-Knoten hängt, ändert sich dabei kaum (er hängt an
den eingehenden Links der 50 Website-Seiten, die die Fixes nicht anfassen) – die Fixes ändern nicht,
*wie viel* Linkkraft an den Demos hängt, sondern *wohin* sie von dort zurückfließt.

## Diagnose 2: hält die Baureihenfolge, was die Diagramme versprechen?

Jede Konzepte-Linie hat ein `*_dag.dot`-Diagramm, das die Baureihenfolge der Verfahren dokumentiert
(z. B. Hill Climbing → Simulated Annealing → Tabu Search) – die Grundlage für die Querverlinkung
zwischen den Demos derselben Linie. Ein Abgleich aller 27 Diagramme (255 dokumentierte Kanten,
254 ohne Duplikate) mit den tatsächlichen Live-Querlinks der 300 Demos (69 Kanten) zeigt eine große
Lücke:

| | Anzahl |
|---|---|
| Dokumentierte Kanten (Diagramme) | 254 |
| Tatsächliche Live-Querlinks | 69 |
| Davon deckungsgleich | 1 |
| Dokumentiert, aber nicht live verlinkt | 253 |
| Live verlinkt, aber nicht dokumentiert | 68 |

Die Diagramme sind die Planung, die Demos die Umsetzung – und beide laufen an fast allen Stellen
auseinander. Diese Demo zeigt das nur als Bestandsaufnahme; eine Bewertung, welche der beiden
Quellen korrigiert werden sollte, und die eigentliche Änderung an den 300 Demo-Repos sind bewusst
nicht Teil dieser Demo.

## Daten

`data/linkgraph_snapshot.json` enthält den vollständigen Schnappschuss: die internen Links
zwischen den 50 HTML-Seiten von sebastianhanisch.net, welche Seiten auf welche der 300 Demo-URLs
verweisen, und – durch Abruf aller 300 `app.py`-Dateien der Demo-Repos über die GitHub-API – den
tatsächlichen Rücklink-Fußzeilentext und die 69 echten Demo-zu-Demo-Querverlinkungen. Erhoben am
2026-09-30, nicht künstlich erzeugt. `data/crosslink_map.json` enthält zusätzlich die echten
Crosslink-Beziehungen zwischen den 26 Konzepte-Linien (aus den `crosslinks`-Feldern der
Linien-JSONs) – die Grundlage für den vollen Fix. `data/dag_edges.json` enthält die 255
dokumentierten Abhängigkeitskanten aus allen 27 `*_dag.dot`-Diagrammen der Website (Quelle, Ziel,
Kanten-Art) – die Grundlage für Diagnose 2.

## Was die Demo zeigt

**1. Diagnose:** PageRank je Konzepte-Linie im Ist-Zustand, zum Vergleich die Startseite; Kennzahlen
zur Konzentration auf index.html + kontakt.html.

**2. Wirkungsanalyse:** Ø PageRank der Linien und Anteil auf index.html + kontakt.html in allen drei
Szenarien nebeneinander; die größten Gewinner beim vollen Fix; eine Einordnung, warum das eine feste
Korrektur und keine Optimierung unter Alternativen ist.

**3. Diagnose (Diagramme vs. Live):** Abgleich der 254 dokumentierten Baureihenfolge-Kanten aus den
27 `*_dag.dot`-Diagrammen mit den 69 tatsächlichen Live-Querlinks der Demos – nur 1 Kante ist
deckungsgleich, mit Beispielen für beide Arten der Abweichung.

## Dateien

- `graph.py` – lädt den Schnappschuss, baut die drei Szenario-Graphen (Ist-Zustand, Basis-Fix, voller Fix), berechnet PageRank
- `analyse.py` – Kennzahlen für die Diagnose/Wirkungsanalyse (Konzentration auf index+kontakt, Ø PageRank je Linie, größte Gewinner, Diagramme-vs-Live-Abgleich)
- `app.py` – die Streamlit-Oberfläche
- `tests/` – Korrektheitstests (PageRank-Summe in allen drei Szenarien, Fix verlinkt tatsächlich die richtigen Seiten, Diagramme-vs-Live-Zahlen konsistent, AppTest-Smoke-Tests)

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
