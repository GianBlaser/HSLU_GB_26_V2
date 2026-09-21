# IFC-Diff Viewer ("ModellWandel")

Vergleicht zwei Staende desselben IFC-Modells und zeigt die Unterschiede
tabellarisch, statistisch und im 3D-Viewer farbcodiert an.

## Kontext

Semesterprojekt im Modul **TA.BA_DT_PROGR - Digital Twin Programmieren**,
Hochschule Luzern, HS26. Autor: Gian Blaser.
Themenfeld gemaess Merkblatt: Datenauswertung und Daten-Visualisierung.

## Zielsetzung

"Was hat sich seit dem letzten Modellstand geaendert?" ist in der
BIM-Koordination eine taegliche Frage, die von Hand kaum beantwortbar ist.
Das Programm

1. laedt zwei IFC-Dateien (Stand A = alt, Stand B = neu),
2. vergleicht die Elemente ueber ihre `GlobalId` und klassiert sie als
   `ADDED`, `DELETED`, `MODIFIED` oder `UNCHANGED`,
3. speichert jeden Vergleichslauf in SQLite,
4. wertet die Aenderungen mit Pandas aus (je Geschoss, je IfcClass, je Art),
5. zeichnet Diagramme mit Matplotlib,
6. zeigt die Aenderungen im 3D-Viewer (geaendert = opak farbig, Kontext transparent),
7. exportiert CSV und PDF-Report.

## Entwicklungsumgebung

| Werkzeug | Version / Bemerkung |
|---|---|
| Python | 3.13 (venv `myenv/` im Repo-Root) |
| IfcOpenShell | 0.8.5 - IFC lesen, Geometrie |
| Pandas | 3.0 - Auswertung |
| Matplotlib | 3.11 - Diagramme |
| SQLite | Standardbibliothek - Historie |
| Streamlit | 1.64 - Benutzeroberflaeche |
| PyVista / stpyvista | 0.49 / 0.2.1 - 3D-Viewer |
| pytest | Tests |
| Git / GitHub | Versionierung, Repo ist public |

## Installation

```bash
git clone https://github.com/GianBlaser/HSLU_GB_26_V2.git
cd HSLU_GB_26_V2
python -m venv myenv
myenv\Scripts\activate
pip install -r requirements.txt
```

## Nutzung

```bash
# Smoke-Test (Etappe 0)
python 02_Semesterprojekt/smoke_test.py

# Anwendung
streamlit run 02_Semesterprojekt/app.py

# Tests
pytest 02_Semesterprojekt/tests
```

In der Anwendung: Stand A und Stand B waehlen (aus `data/` oder per Upload),
**Vergleichen** klicken. Danach Kennzahlen, Tab *Tabelle* (Filter nach
IfcClass / Geschoss / Aenderungsart, Zeile anklicken fuer die Detailansicht
alt/neu, CSV-Export), Tab *Diagramme*, Tab *Historie* (alle bisherigen Laeufe
aus SQLite).

## Projektstruktur

```
02_Semesterprojekt/
├── README.md          Projekt-Dokumentation
├── PROJEKTPLAN.md     Etappenplan
├── app.py             Hauptskript (Streamlit)
├── src/               Module (config, ifc_loader, diff_engine, ...)
├── tools/             Testdaten-Generator (make_variant.py)
├── tests/             pytest-Tests
├── docs/              Architekturdiagramm, Screenshots
├── data/              kleine Test-IFCs (versioniert)
├── cache/             Geometrie-Cache (nicht versioniert)
└── output/            Datenbank, Exporte (nicht versioniert)
```

## Stand der Entwicklung

### Etappe 0 - Projektgeruest (21.09.2026)

Repository bereinigt (Remote ohne Token, Arbeit auf `main`), Module
installiert und in `requirements.txt` eingefroren. IfcOpenShell 0.8.5 laeuft
mit Python 3.13, ein Wechsel auf 3.12 war nicht noetig. Ordnerstruktur,
`config.py` (Farben, Toleranzen, Pfade) und Smoke-Test stehen; der Test
liest `data/Building-Architecture.ifc` (IFC4, 20 IfcProduct-Elemente).
Offen: `stpyvista` laesst sich ausserhalb einer laufenden Streamlit-App
nicht importieren - Relevanz wird in Etappe 7 geprueft (Fallback laut Plan:
PyVista im eigenen Fenster).

### Etappe 1 - Testdaten-Generator (21.09.2026)

`tools/make_variant.py` erzeugt aus einer IFC-Datei reproduzierbar (Seed) einen
Stand B: Bauteile werden geloescht, verschoben, umbenannt inkl. Mengenwert
geaendert oder mit neuer GlobalId dupliziert. Die gemachten Aenderungen landen
in einer `*_ground_truth.json`, gegen die die Diff-Engine ab Etappe 2 getestet
wird. `data/Building-Architecture_B.ifc` (Seed 42, je 2 Aenderungen pro Art)
ist versioniert; Kontrolle: alle 9 Bauteile mit Geometrie lassen sich mit
`ifcopenshell.geom` tesselieren, Kopien haengen korrekt im Geschoss/Site.

```bash
python 02_Semesterprojekt/tools/make_variant.py 02_Semesterprojekt/data/Building-Architecture.ifc --seed 42
```

### Etappe 2 - Loader und Diff-Engine (21.09.2026)

`src/ifc_loader.py` kapselt eine IFC-Datei als `IfcModel` mit einem
GUID-Dict fuer schnelles Matching. `src/diff_engine.py` vergleicht zwei
Staende auf drei Ebenen (Direktattribute, Property Sets mit Zahlentoleranz,
Einfuegekoordinaten) und liefert ein `DiffResult` mit `ElementChange`-Liste,
Kennzahlen und DataFrame. `tests/test_diff_engine.py` prueft gegen die
Ground Truth aus Etappe 1: alle 8 Tests gruen, Datei-gegen-sich-selbst ergibt
0 Aenderungen. Bounding-Box-Vergleich folgt in Etappe 6.

```bash
pytest 02_Semesterprojekt/tests
```

### Etappe 3 - SQLite-Historie (21.09.2026)

`src/database.py` legt die Datenbank `output/ifc_diff.db` mit den drei
Tabellen `comparison`, `element_change` und `attribute_change` an, speichert
ein `DiffResult` komplett (`save_result`) und liest Historie, Elemente eines
Laufs und Attributdetails als DataFrames zurueck. Abnahme: zwei Laeufe
gespeichert und wieder ausgelesen, 14 Tests gruen. Befund dabei: IDs aus
einem DataFrame sind `numpy.int64`, die sqlite3 stillschweigend falsch bindet -
die Lesefunktionen wandeln deshalb mit `int()` um (eigener Regressionstest).

### Vorabversion Streamlit-UI (21.09.2026)

`app.py` als Minimalversion (Dateiauswahl A/B aus `data/`, Button
"Vergleichen", Kennzahlen, Tabelle, Speicherung in SQLite, Historie), damit die
Kette Loader -> Diff -> DB im Browser testbar ist. Wird in Etappe 5 zur
vollstaendigen UI ausgebaut.

### Etappe 4 - Auswertung und Diagramme (21.09.2026)

`src/analytics.py` wertet die Vergleichstabelle mit Pandas aus: Pivot der
Aenderungen je Geschoss und je IfcClass (`pd.crosstab`), Top-10 der am
haeufigsten geaenderten Properties, kombinierbarer Filter fuer die UI.
`src/charts.py` zeichnet daraus mit Matplotlib gestapelte Balken (Farben aus
`config.py`) und ein Balkendiagramm der Top-Properties; `save_figure` schreibt
PNGs. Abnahme: drei PNGs in `output/` erzeugt und plausibel, 20 Tests gruen.

### Etappe 5 - Streamlit-UI ohne 3D (21.09.2026) - Abgabe-Meilenstein

`app.py` ist die vollstaendige Oberflaeche ohne 3D: Upload oder Auswahl aus
`data/`, Vergleich mit Speicherung in SQLite, Kennzahlen, Filter (IfcClass,
Geschoss, Aenderungsart, nur Aenderungen), Tabelle mit Zeilenauswahl und
Detailansicht alt/neu, drei Diagramme, CSV-Download, Historie. Jeder
Seitenbereich ist eine eigene Funktion; das Ergebnis liegt im
`st.session_state`, damit es Filter- und Tab-Wechsel ueberlebt. Getestet im
Browser, Git-Tag `v1.0-abgabefaehig`.
