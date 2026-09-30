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

**Wichtige Einschränkung zuerst:** Kandidaten für einen zusätzlichen Rücklink sind nie beliebige
Demos. Ein Rücklink ohne inhaltlichen Bezug (z. B. eine Dijkstra-Demo, die zusätzlich auf die
Standortplanung-Seite verlinkt, nur weil das irgendwo den PageRank erhöht) wäre für Besucher
irreführend und liest sich wie Linkmanipulation, nicht wie eine echte Empfehlung. Die Demo
unterscheidet deshalb zwei Gruppen:

1. **Eigene Demos der Ziel-Linie** – bekommen den Rücklink auf ihre eigene Linie immer. Das ist
   schlicht Korrektheit (der aktuelle Zustand fehlt ihn schlicht), keine Wahl. Dieser "Basis-Fix"
   allein bringt den größten Effekt.
2. **Demos aus Linien, die laut den echten Crosslink-Angaben der Website mit der Zielseite
   verwandt sind** – hier bleibt eine echte Auswahlfrage: Wenn ein Budget verhindert, dass jede
   verwandte Demo jede Nachbarlinie erwähnt, welche sollten Vorrang bekommen?

Der Grenzgewinn einer weiteren Nachbar-Demo nimmt ab, je mehr schon gewählt sind (die zusätzliche
Linkkraft überschneidet sich mit der schon vorhandenen) – dieselbe Struktur wie bei Facility
Location oder Einflussmaximierung in Netzwerken. Vier Verfahren für die Nachbar-Auswahl im Vergleich:

| Verfahren | Idee |
|---|---|
| Zufällig | Baseline ohne jede Überlegung |
| Referrer-Heuristik | wählt Nachbar-Demos, deren verweisende Seite schon jetzt hohen PageRank hat – ohne Rückkopplung |
| **Greedy** | wählt iterativ die Nachbar-Demo mit dem größten Grenzgewinn, neu bewertet nach jeder Wahl |
| Exakt | erschöpfende Suche über alle Teilmengen – nur auf den vielversprechendsten Nachbar-Demos zumutbar (manche Linien haben über 80 crosslink-verwandte Demos) |

## Daten

`data/linkgraph_snapshot.json` enthält den vollständigen Schnappschuss: die internen Links
zwischen den 50 HTML-Seiten von sebastianhanisch.net, welche Seiten auf welche der 300 Demo-URLs
verweisen, und – durch Abruf aller 300 `app.py`-Dateien der Demo-Repos über die GitHub-API – den
tatsächlichen Rücklink-Fußzeilentext und die 69 echten Demo-zu-Demo-Querverlinkungen. Erhoben am
2026-09-30, nicht künstlich erzeugt. `data/crosslink_map.json` enthält zusätzlich die echten
Crosslink-Beziehungen zwischen den 26 Konzepte-Linien (aus den `crosslinks`-Feldern der
Linien-JSONs) – die Grundlage dafür, welche Demos überhaupt als Kandidaten infrage kommen.

## Was die Demo zeigt

Zielseite (eine der 26 Konzepte-Linien) und Budget für die Nachbar-Auswahl wählbar; Ist-Zustand,
Basis-Fix (eigene Demos) und die vier Nachbar-Auswahl-Verfahren werden live berechnet und als
Balkendiagramm verglichen, dazu die konkret gewählten Demos je Verfahren und eine kurze
Einordnung, warum Greedy hier eine begründete statt nur bequeme Wahl ist – und warum der
Kandidatenpool überhaupt inhaltlich beschränkt ist, statt alle 300 Demos zuzulassen.

## Dateien

- `graph.py` – lädt den Schnappschuss, baut den PageRank-Graphen, berechnet PageRank, bestimmt die inhaltlich relevanten Kandidaten (eigene + crosslink-verwandte Demos)
- `optimierung.py` – die vier Auswahlverfahren für die Nachbar-Demos (Zufällig, Referrer-Heuristik, Greedy, Exakt)
- `app.py` – die Streamlit-Oberfläche
- `tests/` – Korrektheitstests (PageRank-Summe, Kandidatenpool nur eigene+verwandte Demos, Greedy ≥ Referrer-Heuristik, Exakt ≥ Greedy, AppTest-Smoke-Tests)

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
