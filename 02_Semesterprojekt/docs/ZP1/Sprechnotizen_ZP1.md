# ZP1 - Sprechnotizen (max. 3 Minuten)

Kurzpraesentation mit **5 Folien**: 1, 2, 4, 8, 10. Die uebrigen Folien sind
der ausfuehrliche schriftliche Teil (Vorabgabe) und werden nur bei Rueckfragen
gezeigt.

Abgabe ueber ILIAS: `DT_PROGR_HS26_ZP1_GianBlaser_Praesentation.pdf`

---

## Folie 1 - Titel (10 s)

Ich stelle den IFC-Diff Viewer vor: ein Programm, das zwei Staende desselben
IFC-Modells vergleicht und die Frage beantwortet, was sich seit dem letzten
Modellstand geaendert hat.

## Folie 2 - Ausgangslage (30 s)

In der BIM-Koordination kommen laufend neue Modellstaende. Was neu ist, was
fehlt und was verschoben wurde, wird heute per Sichtvergleich oder Excel-Export
beantwortet - fehleranfaellig und nicht reproduzierbar. Mein Programm macht das
Element fuer Element ueber die GlobalId. Kontext gemaess Merkblatt:
Datenauswertung und Daten-Visualisierung.

## Folie 4 - Kernlogik (50 s)

Das Herz ist eine eigene Diff-Definition. Jedes Element bekommt einen von vier
Zustaenden: ADDED, DELETED, MODIFIED, UNCHANGED. Fuer MODIFIED werden drei
Ebenen verglichen: direkte Attribute wie Name, Property Sets mit Zahlentoleranz,
und die Geometrie - heute ueber den Einfuegepunkt, spaeter ueber Bounding-Box
und Dreiecksanzahl. Bewusst kein Mesh-Vergleich; das ist eine dokumentierte
Abgrenzung.

Dazu die Werkzeuge in einem Satz: IfcOpenShell zum Lesen, Pandas fuer die
Auswertung, Matplotlib fuer Diagramme, SQLite fuer die Historie, Streamlit als
Oberflaeche - Git und GitHub, VS Code, venv.

## Folie 8 - Stand heute (50 s)

Die Kette laeuft bereits durchgehend: Dateien waehlen, vergleichen, Kennzahlen,
filterbare Tabelle mit Detailansicht alt/neu, Diagramme, CSV-Export, Historie.
20 automatisierte Tests sind gruen.

Eine Besonderheit: Es gibt keine oeffentlichen Testdaten mit zwei echten
Planungsstaenden. Ich habe deshalb einen Generator geschrieben, der aus einem
Modell kontrolliert einen Stand B erzeugt und die gemachten Aenderungen als
Ground Truth speichert. Damit ist die Diff-Engine beweisbar korrekt.

## Folie 10 - Naechste Schritte (30 s)

Bis ZP2: Geometrie mit Cache, dann der 3D-Viewer, in dem geaenderte Elemente
farbig und der Rest transparent dargestellt wird. Herausforderung ist die
Einbettung von PyVista in Streamlit - dazu meine Frage: Ist PyVista als
Zusatzmodul ausserhalb der Liste in Ordnung? IfcOpenShell erfuellt die Pflicht
des externen Moduls bereits.

---

## Moegliche Rueckfragen

- **Warum GlobalId und nicht Name?** GlobalId ist im IFC-Standard eindeutig
  und stabil ueber Exporte; Namen koennen doppelt sein oder sich aendern.
- **Was, wenn ein Werkzeug beim Export neue GUIDs vergibt?** Dann erscheint
  alles als DELETED + ADDED. Das ist ein bekanntes Limit und wird in der UI
  als Warnung sichtbar (hoher Anteil ADDED/DELETED).
- **Warum drei Klassen und nicht mehr?** IfcModel (Datei), ElementChange (eine
  Aenderung), DiffResult (Ergebnis). Alles andere sind Funktionen - so bleibt
  jede Zeile erklaerbar.
- **Wie gross duerfen die Modelle sein?** Der Attributvergleich ist schnell
  (Dict-Lookup). Die Geometrie ist der Engpass, deshalb Cache und die Option
  "nur Aenderungen rendern" ab 20'000 Elementen.
- **Warum ifcopenshell.api im Generator?** Ein blosses file.remove() laesst
  Verweise haengen und macht die Datei unbrauchbar; die API entfernt sauber.
