# Projektplan: IFC-Diff Viewer ("ModellWandel")

**Modul:** TA.BA_DT_PROGR - Digital Twin Programmieren, HS26
**Modulverantwortlicher:** Michal Rontsinsky
**Autor:** Gian Blaser
**Repository:** https://github.com/GianBlaser/HSLU_GB_26_V2 (muss PUBLIC sein)
**Altes Repo:** HSLU_GB_26 bleibt unveraendert auf GitHub (nur Uebungen)
**Lokal:** `C:\HSLU_Programming\HSLU_GB_26`
**Kontext gemaess Merkblatt:** Datenauswertung + Daten-Visualisierung (Dashboard)
**Stand:** 2026-09-21 (SW2) - Etappen 0 bis 7 abgeschlossen (v1.0-abgabefaehig = E5), siehe Kap. 15

> Arbeitsanweisung fuer Claude Code. Etappenweise abarbeiten, nach jeder Etappe
> Tests, Commit, Ruecksprache. Abgeglichen mit Merkblatt Leistungsnachweis HS26,
> Semesterplan HS26, Skript SW1, Skript SW2 und den Uebungs-Notebooks.

---

## 0. SOFORTMASSNAHMEN (vor jeder Code-Zeile)

### 0.1 GitHub-Token ist kompromittiert - zuerst erledigen

In `.git/config` steht die Remote-URL mit eingebettetem Personal Access Token
im Klartext (`https://GianBlaser:ghp_...@github.com/...`). Das Skript SW2 zeigt
diese Methode zwar so, sie ist aber unsicher: der Token liegt unverschluesselt
auf der Platte, landet in jeder Fehlermeldung und in jedem Terminal-Log.
Dieser konkrete Token wurde ausserhalb deines Rechners sichtbar.

**To do:**
1. GitHub -> Settings -> Developer settings -> Personal access tokens ->
   diesen Token **revoke**
2. Remote ohne Token setzen:
   ```bash
   git remote set-url origin https://github.com/GianBlaser/HSLU_GB_26.git
   git remote remove upstream
   ```
   (`upstream` zeigt auf dasselbe Repo wie `origin` - doppelt und verwirrend.)
3. Authentifizierung ueber den Git Credential Manager (ist bei Git for Windows
   dabei). Beim ersten `git push` oeffnet sich ein Browser-Login, danach ist Ruhe.
   Falls doch ein Token noetig ist: neuen erstellen und bei der Passwortabfrage
   eingeben, **nicht** in die URL schreiben.

### 0.2 Branch aufraeumen

Aktiver Branch ist `my_test` (aus der Uebung). Das Semesterprojekt gehoert auf
`main`:
```bash
git checkout main
git pull origin main
```
`my_test` kann bleiben oder geloescht werden - fuer die Abgabe zaehlt `main`.

### 0.3 Repository-Sichtbarkeit pruefen

Merkblatt Kap. 5.5: "Das Repository mit dem Programm muss oeffentlich sein."
Pruefen unter Settings -> General -> Danger Zone -> Change visibility.

### 0.4 Python-Version pruefen - moegliches Problem

`myenv` laeuft auf **Python 3.13.14 aus dem Microsoft Store**
(`...WindowsApps\PythonSoftwareFoundation.Python.3.13...`). Zwei Risiken:
- Store-Python hat bekannte Eigenheiten bei Pfaden und Schreibrechten
- `ifcopenshell` und `pyvista` haben fuer 3.13 nicht zuverlaessig Wheels

**Erster Test in Etappe 0:**
```bash
myenv\Scripts\activate
pip install ifcopenshell
python -c "import ifcopenshell; print(ifcopenshell.version)"
```
Schlaegt das fehl: **Python 3.12 von python.org installieren** (nicht Store) und
`myenv` neu anlegen. Das ist kein Rueckschritt, sondern erspart tagelanges Suchen.

---

## 1. Zielsetzung

Programm, das **zwei IFC-Staende desselben Projekts vergleicht** und die
Unterschiede tabellarisch, statistisch und **im 3D-Viewer farbcodiert** anzeigt.

Praxisnutzen: "Was hat sich seit dem letzten Modellstand geaendert?" ist in der
BIM-Koordination eine taegliche Frage, die manuell kaum beantwortbar ist.

### Funktionsumfang

1. Zwei IFC-Dateien laden (Stand A = alt, Stand B = neu)
2. Elementweiser Vergleich ueber `GlobalId`:
   `ADDED` / `DELETED` / `MODIFIED` / `UNCHANGED`
3. Speicherung der Vergleichslaeufe in SQLite (Historie)
4. Auswertung mit Pandas: Aenderungen je Geschoss, je IfcClass, je Aenderungsart
5. Diagramme mit Matplotlib
6. 3D-Viewer: geaenderte Objekte opak farbig, Kontext transparent
7. Export: CSV + PDF-Report

---

## 2. Bewertung - was wirklich zaehlt

Semesterleistung 30% (ZP1 15% + ZP2 15%), MEP 70%.

**MEP-Aufteilung (Merkblatt Kap. 3.2):**

| Kriterium | Anteil | Konsequenz |
|---|---|---|
| **Funktionalitaet** | **30%** | Vollstaendige Kette + **modularer Aufbau: Hauptkomponente, Hilfsfunktionen, Klassen, UI** wird explizit benotet. Dazu IDE, Git, Module erlaeutern koennen. |
| **Dokumentation** | **20%** | Wird oft unterschaetzt. README + Doku-PDF sind ein Fuenftel der MEP-Note. Ab Etappe 0 mitschreiben. |
| Innovation/Selbstaendigkeit | 10% | Eigene Diff-Definition, Testdaten-Generator, Viewer-Kopplung |
| Praesentation | 10% | Aufbau, visuelle Aufbereitung, Vortrag |

**Dokumentation (20%) ist doppelt so stark gewichtet wie Innovation (10%).**

**Abgabe ueber ILIAS, Namenskonvention:**
`DT_PROGR_HS26_ZP1_GianBlaser_Praesentation`

---

## 3. Terminplan (Semesterplan HS26)

| Woche | Datum | Unterricht | Dein Stand |
|---|---|---|---|
| SW2 | 21.09. | Setup Werkzeuge, Python 1 | *heute* - Repo steht, Thema steht |
| SW3 | 28.09. | Setup Werkzeuge, Python 2 | **Etappe 0**: Sofortmassnahmen + Projektgeruest |
| SW4 | 05.10. | Einfuehrung Python Module | **Etappe 1**: Testdaten-Generator |
| SW5 | 12.10. | Ganzheitliche Anwendung 1 | **Etappe 2**: Diff-Engine laeuft |
| SW6 | 19.10. | Ganzheitliche Anwendung 2 | **Etappe 3**: SQLite |
| **SW7** | **26.10.** | **Zwischenpraesentation 1** | Konzeptfolien + schriftl. Vorabgabe |
| SW8 | 02.11. | Coaching | Etappe 4: Auswertung + Diagramme |
| SW9 | 09.11. | Coaching (Horw) | Etappe 5: Streamlit-UI |
| SW10 | 16.11. | Coaching | Etappe 6: Geometrie + Cache |
| SW11 | 23.11. | Coaching | Etappe 7: 3D-Viewer |
| SW12 | 30.11. | KI-Grundlagen | Puffer / Etappe 8 |
| SW13 | 07.12. | Machine Learning | Doku + ZP2-Folien |
| **SW14** | **14.12.** | **Zwischenpraesentation 2** | lauffaehiger Prototyp |
| MEP | tbd (Termin kommt in SW8) | muendlich, Horw | Doku + Praesentation final |

**ZP1 (26.10.):** max. 3 Min muendlich + ausfuehrliche schriftliche Vorabgabe.
Inhalt: Thema/Zielsetzung, Entwicklungsumgebung/Module/Werkzeuge,
Herausforderungen und naechste Schritte. Muss nicht abschliessend sein.

**ZP2 (14.12.):** "fast finaler Prototyp", **benutzbare und funktionierende
Variante**. Einzelne Features duerfen Arbeitsversion sein.
-> Etappe 5 muss vor dem 14.12. stehen.

---

## 4. Zeitbudget - Realitaetscheck

3 ECTS = 90 h: ca. 34 h Kontaktunterricht, ca. 44 h Selbststudium,
ca. 12 h MEP-Vorbereitung.

**Realistisch stehen ca. 40-45 h fuer die Entwicklung zur Verfuegung.**
Wenn eine Etappe ueberzieht: Umfang kuerzen, nicht Stunden draufpacken.
Etappe 8 und der Screencast sind die ersten Streichkandidaten.

---

## 5. Repository-Struktur

Das bestehende Repo `HSLU_GB_26` ist das Semester-Repo und bleibt es. Das
Semesterprojekt bekommt einen eigenen Unterordner, die Uebungen bleiben daneben.
**Eine gemeinsame venv (`myenv/`) im Repo-Root** - kein zweites Environment.

```
HSLU_GB_26/                          <- Repo-Root, hier liegt myenv
├── README.md                        <- Semester-README, verweist aufs Projekt
├── requirements.txt                 <- gemeinsam, nach jedem Install neu freezen
├── .gitignore                       <- erweitern (siehe unten)
├── myenv/                           <- nicht versioniert
├── help/                            <- bestehende Uebungen, bleibt
└── 02_Semesterprojekt/              <- ALLES Projektbezogene ab hier
    ├── PROJEKTPLAN.md               <- dieses Dokument
    ├── README.md                    <- Projekt-Doku (MEP-relevant, 20%!)
    ├── app.py                       <- Hauptskript (Streamlit)
    ├── src/
    │   ├── __init__.py
    │   ├── config.py                # Farben, Toleranzen, Pfade
    │   ├── ifc_loader.py            # Klasse IfcModel
    │   ├── diff_engine.py           # Klassen ElementChange, DiffResult
    │   ├── geometry.py              # Mesh-Erzeugung + Cache
    │   ├── database.py              # SQLite
    │   ├── analytics.py             # Pandas
    │   ├── charts.py                # Matplotlib
    │   ├── viewer.py                # PyVista
    │   └── report.py                # PDF/CSV-Export
    ├── tools/
    │   └── make_variant.py          # Testdaten-Generator
    ├── tests/
    │   ├── test_diff_engine.py
    │   ├── test_database.py
    │   └── test_geometry.py
    ├── docs/
    │   ├── architektur.png
    │   └── screenshots/
    ├── data/                        # kleine Test-IFCs (versioniert)
    ├── cache/                       # nicht versioniert
    └── output/                      # nicht versioniert
```

**Start des Programms** (aus dem Repo-Root, mit aktivierter venv):
```bash
streamlit run 02_Semesterprojekt/app.py
```

**`.gitignore` erweitern** (aktuell steht nur `myenv/` drin):
```
myenv/
__pycache__/
*.pyc
*.db
02_Semesterprojekt/cache/
02_Semesterprojekt/output/
.streamlit/secrets.toml
```

**requirements.txt** nach jeder Installation aktualisieren (Skript SW2, S. 9):
```bash
pip freeze > requirements.txt
```

---

## 6. Modul-Abdeckung (Nachweis fuer die MEP)

| Gefordertes Modul | Wo eingesetzt |
|---|---|
| IfcOpenShell | `ifc_loader.py`, `geometry.py` - **das externe Pflichtmodul** |
| Pandas | `analytics.py` (bereits in requirements.txt) |
| Matplotlib | `charts.py`, `report.py` |
| SQLite | `database.py` (stdlib, kein Install noetig) |
| Streamlit | `app.py` |

Zusatzmodule ausserhalb der Liste: `pyvista` + `stpyvista`, `numpy` (schon da).
Erlaubt, da die Pflicht "mindestens ein externes Modul" durch IfcOpenShell
erfuellt ist. **Bei ZP1 am 26.10. kurz mit Rontsinsky abklaeren**, bevor du in
Etappe 7 Zeit investierst.

Zu installieren in Etappe 0:
```bash
pip install ifcopenshell matplotlib streamlit pyvista stpyvista pytest
pip freeze > requirements.txt
```

---

## 7. Code-Stil - verbindlich

Der Code muss in der muendlichen Pruefung von dir Zeile fuer Zeile erklaerbar
sein. Bewertet wird zudem der **modulare Aufbau**: Hauptkomponente,
Hilfsfunktionen, Klassen, UI.

1. **Sprachniveau der Vorlesung.** Behandelt wurden: Variablen, Listen, Tuple,
   Dict, Kontrollstrukturen, Schleifen, Funktionen, Dateien, Klassen, Pandas,
   Matplotlib. Alles darueber hinaus nur, wenn es den Code *kuerzer und klarer*
   macht.
2. **Verboten:** Metaklassen, Dekoratoren ausser `@dataclass`, verschachtelte
   Comprehensions, `lambda` ausser als `key=`, `functools`-Akrobatik,
   Vererbungshierarchien, abstrakte Basisklassen, `*args/**kwargs` ohne Not.
3. **Funktionen:** eine Aufgabe, max. ca. 30 Zeilen, max. 4 Parameter,
   sprechende Namen, Docstring Pflicht.
4. **Klassen nur wo sie tragen.** Genau drei geplant:
   - `IfcModel` - gekapselte IFC-Datei (Elemente, Psets, Geometrie-Cache)
   - `ElementChange` - eine Aenderung (`@dataclass`)
   - `DiffResult` - Ergebnis eines Vergleichs (Liste + Kennzahlen + DataFrame)
   Mehr nur nach Ruecksprache.
5. **Keine Magic Numbers.** Toleranzen, Farben, Pfade in `config.py`.
6. **Docstrings und Kommentare auf Deutsch** (Schweizer Standarddeutsch, kein
   Eszett). Bezeichner im Code auf Englisch.
7. **Typ-Hints ja**, aber einfach: `str`, `int`, `list[str]`, `dict`,
   `pd.DataFrame`. Kein `Optional[Union[...]]`-Dickicht.
8. **Effizienz da, wo sie zaehlt:** Dict-Lookup statt Listen-Durchsuchen beim
   GUID-Matching, Geometrie-Cache. Sonst Lesbarkeit vor Mikro-Optimierung.
9. **Fehlerbehandlung je Element**, nicht global - eine kaputte Geometrie darf
   nicht den ganzen Durchlauf abbrechen.
10. **Kein Code ohne Zweck.** Keine Platzhalter, keine
    "koennte man spaeter brauchen"-Funktionen.

**IfcOpenShell-Stil wie im Unterricht** (Notebook `ArbeitMitIfcOpenShell`):
```python
import ifcopenshell
import ifcopenshell.util.element

f = ifcopenshell.open(pfad)
elemente = f.by_type("IfcProduct")
psets = ifcopenshell.util.element.get_psets(obj)
```
Fuer das Geschoss zeigt das Notebook `f.get_inverse(obj)` +
`IfcRelContainedInSpatialStructure`. Im Projekt wird
`ifcopenshell.util.element.get_container(obj)` verwendet - dasselbe Ergebnis,
eine Zeile statt acht. **Diese Abweichung im Code kommentieren**, damit du sie
in der Pruefung begruenden kannst.

---

## 8. Testdaten - wichtiger Befund

Vorhanden unter
`05_SEMESTER 5\02_PROG\02_Uebungen\IFC Testfiles\Certification-datasets-main\`:
buildingSMART Certification-Datasets, Szene "Simple-Scene", je einmal in
IFC 2x3, IFC4 ADD2 und IFC4.3 ADD2. 70 KB bis 2.3 MB. Erzeugt mit SketchUp
IFC-Manager 5.6.0.

**Problem:** Keine zwei Projektstaende, sondern dieselbe Szene in verschiedenen
Schema-Versionen. Stichprobe `Building-Architecture.ifc`: IFC4 hat 94 GUIDs,
IFC4.3 hat 92, davon 63 gemeinsam. Ein Diff darauf zeigt Schema-Unterschiede,
keine Planungsaenderungen.

**Loesung (Etappe 1):** `tools/make_variant.py` erzeugt aus einer IFC-Datei
kontrolliert einen "Stand B": n Elemente loeschen, n verschieben (Placement-
Offset), n Property-Werte aendern, n duplizieren mit neuer GUID. Dazu
`ground_truth.json` mit den tatsaechlich gemachten Aenderungen.
**Damit ist die Diff-Engine automatisiert testbar** - starkes Argument in der
MEP und Beleg fuer "Selbstaendigkeit".

In Etappe 0 zwei bis drei kleine IFCs nach `02_Semesterprojekt/data/` kopieren
(nur kleine, damit das Repo schlank bleibt):
- Entwicklung: `IFC 4.0.2.1 .../Simple-Scene/Building-Architecture.ifc` (142 KB)
- Performance-Test: `.../Simple-Scene/Infra-Landscaping.ifc` (2.3 MB) -
  **nicht** ins Repo, nur lokal referenzieren

---

## 9. Datenmodell (SQLite)

Datei: `02_Semesterprojekt/output/ifc_diff.db` (nicht versioniert)

```sql
CREATE TABLE comparison (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    file_a       TEXT NOT NULL,
    file_b       TEXT NOT NULL,
    schema_a     TEXT,
    schema_b     TEXT,
    n_added      INTEGER,
    n_deleted    INTEGER,
    n_modified   INTEGER,
    n_unchanged  INTEGER,
    duration_s   REAL
);

CREATE TABLE element_change (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id  INTEGER NOT NULL REFERENCES comparison(id),
    global_id      TEXT NOT NULL,
    ifc_class      TEXT,
    name           TEXT,
    storey         TEXT,
    change_type    TEXT NOT NULL,   -- ADDED | DELETED | MODIFIED | UNCHANGED
    n_attr_changes INTEGER DEFAULT 0
);
CREATE INDEX idx_ec_comp ON element_change(comparison_id);
CREATE INDEX idx_ec_type ON element_change(change_type);

CREATE TABLE attribute_change (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    element_change_id INTEGER NOT NULL REFERENCES element_change(id),
    source            TEXT,          -- ATTRIBUTE | PSET | GEOMETRY
    pset_name         TEXT,
    property_name     TEXT NOT NULL,
    value_a           TEXT,
    value_b           TEXT
);
```

---

## 10. Kernlogik: Was gilt als "geaendert"?

Zentrale Eigenleistung - dokumentieren und in der Praesentation erklaeren.

**Schluessel:** `GlobalId`. Dict-basiertes Matching (`{guid: element}`), keine
verschachtelten Schleifen.

**Drei Vergleichsebenen je Element:**

1. **Direkte Attribute:** `Name`, `Description`, `ObjectType`, `Tag`,
   `PredefinedType`
2. **Property Sets:** via `get_psets()`, flach als `{"Pset_X.PropY": wert}`.
   Zahlen mit Toleranz `1e-6`, nicht mit `==`.
3. **Geometrie (bewusst vereinfacht):**
   - Schwerpunkt Bounding-Box (Toleranz 1 mm)
   - Abmessungen Bounding-Box (Toleranz 1 mm)
   - Dreiecksanzahl des Meshes

   Kein Mesh-Topologie-Vergleich. **Dokumentierte Abgrenzung, keine Luecke** -
   in der Praesentation offensiv benennen.

**Ausgeschlossen:** `OwnerHistory`, Zeitstempel, `IfcApplication`,
Entity-Nummern.

**Schema-Unterschied A/B:** Warnung in der UI, Vergleich moeglich, aber als
unsicher markieren.

---

## 11. Viewer-Spezifikation

Farben zentral in `config.py`:

| Zustand | Farbe | Hex | Opazitaet |
|---|---|---|---|
| ADDED | Gruen | `#2E9E5B` | 1.0 |
| DELETED | Rot | `#D1434A` | 1.0 |
| MODIFIED | Orange | `#E08A1E` | 1.0 |
| UNCHANGED | Grau | `#9AA0A6` | 0.07 |

- `DELETED` aus Modell **A** rendern, alles andere aus **B**
- Kontext umschaltbar: `aus` / `transparent` / `nur Kanten`
- Filter (IfcClass, Geschoss, Aenderungsart) wirken auf Tabelle **und** Viewer
- Klick auf Tabellenzeile -> Kamera zoomt auf Element
- Legende immer sichtbar

Performance:
- Mesh-Cache als `.npz` unter `02_Semesterprojekt/cache/<sha1>.npz`
- `ifcopenshell.geom.iterator` mit mehreren Threads
- `USE_WORLD_COORDS = True`
- Elemente ohne Geometrie einzeln ueberspringen
- Bei > 20'000 Elementen: Warnung + Option "nur Aenderungen rendern"

---

## 12. Etappenplan

Jede Etappe: lauffaehiger Code, Tests gruen, Commit auf `main`, Meldung,
Freigabe abwarten. Nach jeder Etappe **zwei bis drei Saetze ins Projekt-README**
(Doku = 20% der MEP).

Commit-Konvention: `[E2] Diff-Engine: Attributvergleich implementiert`

### Etappe 0 - Sofortmassnahmen + Geruest (3 h) | bis SW3, 28.09.
Kap. 0 abarbeiten (Token, Branch, Sichtbarkeit, Python-Test), Ordner
`02_Semesterprojekt/` anlegen, `.gitignore` erweitern, Module installieren,
`requirements.txt` freezen, `config.py`, README-Geruest, Testdaten kopieren.
Smoke-Test: IFC oeffnen, Elementanzahl ausgeben.
**Abnahme:** `import ifcopenshell` laeuft, Push auf `main` erfolgreich.

### Etappe 1 - Testdaten-Generator (4 h) | bis SW4, 05.10.
`tools/make_variant.py` + `ground_truth.json`.
**Abnahme:** Variante oeffnet fehlerfrei in einem IFC-Viewer.

### Etappe 2 - Loader + Diff-Engine (8 h) | bis SW5, 12.10.
`IfcModel`, `ElementChange`, `DiffResult`, Vergleich nach Kap. 10.
`tests/test_diff_engine.py` gegen `ground_truth.json`.
**Abnahme:** Alle gesetzten Aenderungen gefunden, Datei-gegen-sich-selbst = 0.

### Etappe 3 - SQLite (3 h) | bis SW6, 19.10.
`database.py`, Schema, Speichern, Historie lesen.
**Abnahme:** Zwei Laeufe gespeichert und wieder auslesbar.

### >>> ZP1 am 26.10. <<<
Konzeptfolien (max. 3 Min) + schriftliche Vorabgabe ueber ILIAS.
Stand Etappe 3 reicht voellig - lieber wenig Fertiges sauber zeigen.
Datei: `DT_PROGR_HS26_ZP1_GianBlaser_Praesentation.pdf`
Bei dieser Gelegenheit PyVista mit Rontsinsky abklaeren.

### Etappe 4 - Auswertung + Diagramme (5 h) | SW8
`analytics.py` (Pivot je Geschoss/Klasse/Art), `charts.py` (gestapelte Balken
je Geschoss, Top-10 geaenderte Properties).
**Abnahme:** PNGs erzeugt und plausibel.

### Etappe 5 - Streamlit-UI ohne 3D (6 h) | SW9
Dateiauswahl A/B, Button "Vergleichen", KPI-Zeile, filterbare Tabelle,
Detailansicht alt/neu, Diagramme, CSV-Export.
**ABGABE-MEILENSTEIN. Git-Tag `v1.0-abgabefaehig`.**

### Etappe 6 - Geometrie + Cache (5 h) | SW10
`geometry.py`, npz-Cache, Bounding-Box-Werte zurueck in die Diff-Engine.
**Abnahme:** Zweiter Ladevorgang deutlich schneller.

### Etappe 7 - 3D-Viewer (7 h) | SW11
`viewer.py` nach Kap. 11, Einbettung via `stpyvista`, Kontext-Umschalter,
Legende, Filterkopplung.
**Abnahme:** Aenderungen im transparenten Kontext klar erkennbar.

### Etappe 8 - Interaktion + Report (4 h) | SW12, optional
Zeilen-Klick -> Kamera-Zoom, `report.py` (PDF mit KPIs, Diagrammen, Tabelle).

### >>> ZP2 am 14.12. <<<
"Benutzbare und funktionierende Variante" - Etappe 5 genuegt formal,
Etappe 7 ist das Ziel.

### Etappe 9 - Doku + Praesentation (8 h) | bis MEP
Projekt-README final (Installation, Nutzung, Screenshots, Architekturdiagramm,
Abgrenzungen), Code aufraeumen, Docstrings pruefen, Praesentations-PDF
(10-15 Min: Problem, Ansatz, Demo, Abgrenzungen, Ausblick).
Optional: Screencast.

**Summe ca. 53 h inkl. Doku und Praesentation.**

---

## 13. Risiken

| Risiko | Gegenmassnahme |
|---|---|
| Python 3.13 (Store) inkompatibel | Python 3.12 von python.org, venv neu - in Etappe 0 testen |
| `stpyvista` zickt in Streamlit | Fallback: PyVista in eigenem Fenster, Screenshot in Streamlit |
| Transparenz-Rendering matschig | Alpha auf 0.05 oder Kantenmodus als Standard |
| Geometrie zu langsam | Cache (Etappe 6) + "nur Aenderungen rendern" |
| IFC2x3 vs IFC4 | Nur gleiche Schemata vergleichen, sonst Warnung |
| Repo versehentlich privat | Vor ZP1 und vor MEP pruefen |
| Zeitnot | Etappe 5 ist der Abgabe-Meilenstein |
| Doku bleibt liegen | Nach jeder Etappe zwei Saetze ins README |

---

## 14. Arbeitsanweisungen fuer Claude Code

1. **Alles unter `02_Semesterprojekt/`.** Repo-Root und `help/` nicht anfassen,
   ausser `.gitignore`, `requirements.txt` und das Semester-README.
2. **Etappenweise.** Nicht mehrere Etappen in einem Zug. Nach jeder Etappe:
   Tests, Commit auf `main`, Ergebnis melden, Freigabe abwarten.
3. **Vor dem Schreiben einer Datei** Aufbau kurz skizzieren und abnicken lassen.
4. **Code-Stil aus Kapitel 7 ist verbindlich.** Im Zweifel die einfachere Loesung.
5. **Keine ungefragten Zusatzfeatures.** Der Etappenplan ist der Umfang.
6. **Nach jeder Etappe zwei bis drei Saetze ins Projekt-README.**
7. **Nie Tokens oder Passwoerter in Dateien schreiben**, auch nicht als Beispiel.
8. Ich muss jede Zeile in der MEP erklaeren koennen. Lieber eine verstaendliche
   Schleife als ein cleverer Einzeiler.
9. Bei Unklarheit fragen statt annehmen.

---

## 15. AKTUELLER STAND (fuer Fortsetzung in neuem Chat)

**Datum:** 2026-09-21. Lokales Repo: `C:\HSLU_Programming\HSLU_GB_26`, Branch `main`.
`origin` zeigt bereits auf das neue Repo `HSLU_GB_26_V2`. Das alte GitHub-Repo
`HSLU_GB_26` wird nicht mehr angefasst.

### Erledigt

- **Etappe 0** (Commit `c412aca`): Remote ohne Token, `upstream` entfernt,
  Branch `main`, Module installiert, `requirements.txt` eingefroren,
  `.gitignore`, Ordnerstruktur, `src/config.py`, `smoke_test.py`,
  README-Geruest, Testdaten in `data/`.
  Befund: IfcOpenShell 0.8.5 laeuft mit Python 3.13 (Store) - **kein
  Wechsel auf 3.12 noetig**. Kap. 0.4 ist damit erledigt.
- **Etappe 1** (Commit `7bec972`): `tools/make_variant.py` + Ground Truth.
  `data/Building-Architecture_B.ifc` und `_ground_truth.json` (Seed 42,
  je 2x delete/move/modify/add) sind versioniert. Abnahme bestanden
  (alle Aenderungen nachgewiesen, 9/9 Geometrien tesselierbar).
  Verwendet `ifcopenshell.api` fuer `root.remove_product` und
  `root.copy_class` - Begruendung im Modul-Docstring.

### Offen / Befunde

- **Push erfolgt** (Commit `cb34cb9`, Merge mit dem Initial commit von
  HSLU_GB_26_V2). `credential.helper manager` ist global gesetzt, Push
  funktioniert. Noch pruefen: Repo `HSLU_GB_26_V2` auf github.com public?
- `stpyvista` 0.2.1 laesst sich ausserhalb einer laufenden Streamlit-App
  nicht importieren (Components-v2-API). Relevanz erst in Etappe 7,
  Fallback laut Kap. 13.
- Die Test-IFC hat nur 20 IfcProduct / 13 IfcElement - fuer Entwicklung
  ausreichend, Performance-Test spaeter mit `Infra-Landscaping.ifc`.

- **Etappe 2**: `src/ifc_loader.py` (`IfcModel`), `src/diff_engine.py`
  (`ElementChange`, `DiffResult`, `compare_models`), `tests/test_diff_engine.py`
  + `tests/conftest.py`. 8 Tests gruen. Geometrie-Ebene vorerst nur als
  Placement-Vergleich (source GEOMETRY, property "Placement"); Bounding-Box
  in Etappe 6. attribute_changes sind Dicts (keine vierte Klasse).

- **Etappe 3**: `src/database.py` (Funktionen, keine Klasse: connect,
  save_result, save_element_change, load_history, load_changes,
  load_attribute_changes), `tests/test_database.py`. 14 Tests gruen.
  Befund: numpy.int64 als sqlite3-Parameter liefert 0 Zeilen -> int().

- **Minimal-app.py** (vorgezogen aus Etappe 5): Auswahl A/B, Vergleichen,
  KPIs, Tabelle, Historie. Laeuft, im Browser getestet.
- **Etappe 4**: `src/analytics.py` (only_changes, pivot_by, changes_by_storey,
  changes_by_class, top_changed_properties, filter_changes), `src/charts.py`
  (plot_stacked_bars, plot_changes_by_storey/class, plot_top_properties,
  save_figure; Backend Agg), `tests/test_analytics.py`. 20 Tests gruen.

- **Etappe 5**: `app.py` vollstaendig (select_file mit Upload, run_comparison,
  show_kpis, show_filters, show_table mit on_select, show_details,
  show_charts, show_export, show_history; Tabs Tabelle/Diagramme/Historie).
  Uploads landen in `output/uploads/`. Tag `v1.0-abgabefaehig`.

- **ZP1-Unterlagen** erstellt: `docs/ZP1/DT_PROGR_HS26_ZP1_GianBlaser_Praesentation.pptx/.pdf`
  (10 Folien, ausfuehrliche Form), `docs/ZP1/Sprechnotizen_ZP1.md` (3-Min-Skript,
  Folien 1/2/4/8/10, Rueckfragen), Generator `docs/ZP1/build/build_slides.js`.
  Offen: App-Screenshot einfuegen (optional), Abgabe ueber ILIAS bis 26.10.,
  PyVista-Frage an Rontsinsky stellen.

- **Etappe 6**: `src/geometry.py` (file_hash, cache_path, create_meshes,
  save_cache, load_cache, load_meshes, mesh_summary), `IfcModel.load_geometry()`
  + `get_geometry_summary()`, `diff_engine.compare_geometry()` (center, size,
  n_triangles als GEOMETRY-Quelle), Haekchen in app.py, `tests/test_geometry.py`.
  Meshes: verts float32 (n,3), faces int32 (m,3), Meter, Weltkoordinaten,
  npz-Schluessel "guid|verts" (GUIDs koennen auf _ enden). Cache-Faktor ~30.

- **Etappe 7**: `src/viewer.py` (make_polydata, collect_meshes, add_group,
  build_plotter, focus_on_changes, render_image), CONTEXT_*/VIEWER_* in
  config.py, Tab "3D-Ansicht" in app.py (Kontext-Radio, Filterkopplung,
  Render-Cache im Session-State), `tests/test_viewer.py`. 31 Tests gruen.
  Offscreen-Rendering als Bild - **kein stpyvista noetig**. Interaktive
  Einbettung bleibt optional, falls Rontsinsky PyVista freigibt.
  Befund: copy_class kopiert Representation nicht -> make_variant teilt sie,
  Testdaten B neu erzeugt (neue GUIDs in ground_truth.json).
  Hinweis: nach Aenderungen in src/ Streamlit neu starten (kein Hot-Reload).

### Naechster Schritt

**Etappe 8 - Interaktion + Report** (optional, Kap. 12): Zeilen-Klick in der
Tabelle -> Kamera auf das Element (Viewer mit nur diesem Mesh + Kontext),
`src/report.py` (PDF mit KPIs, Diagrammen, Tabelle; matplotlib PdfPages,
kein neues Modul). Danach **Etappe 9 - Doku + Praesentation** (README final,
Architekturdiagramm, Screenshots, ZP2-Folien via docs/ZP1/build/build_slides.js).
