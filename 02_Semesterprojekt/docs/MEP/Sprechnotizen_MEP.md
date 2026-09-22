# MEP - Sprechnotizen (10-15 Minuten Praesentation, 5-10 Minuten Fragen)

Datei zur Abgabe: `DT_PROGR_HS26_MEP_GianBlaser_Praesentation.pdf`
Abgabe ueber ILIAS inkl. Link zum Repository, Pruefung in Horw.

Richtzeit je Folie in Klammern. Bei der Demo lieber weniger zeigen und
ruhig sprechen als durchhetzen.

---

## Folie 1 - Titel (20 s)

Ich stelle den IFC-Diff Viewer vor. Das Programm beantwortet eine Frage, die
in der BIM-Koordination taeglich vorkommt: Was hat sich seit dem letzten
Modellstand geaendert?

## Folie 2 - Problem (60 s)

In einem Projekt kommen laufend neue IFC-Staende aus verschiedenen Fachplanungen.
Heute wird der Vergleich per Auge im Viewer oder ueber Excel-Exporte gemacht -
das ist fehleranfaellig, nicht reproduzierbar und hinterher nicht nachvollziehbar.
Kommerzielle Werkzeuge koennen das, sind aber teuer und in ihrer Logik
nicht einsehbar. Mein Programm vergleicht Element fuer Element ueber die
GlobalId und legt offen, nach welchen Regeln es das tut.

## Folie 3 - Loesung (60 s)

Die Kette laeuft durchgehend: zwei Dateien laden, vergleichen, den Lauf in
SQLite speichern, mit Pandas auswerten, Diagramme zeichnen, im 3D darstellen,
als CSV oder PDF exportieren. Alle geforderten Module sind dabei im Einsatz -
IfcOpenShell als externes Pflichtmodul, dazu Pandas, Matplotlib, SQLite und
Streamlit.

## Folie 4 - Architektur (90 s)

Der Aufbau ist bewusst modular. `app.py` ist die Hauptkomponente mit der
Oberflaeche und ruft die Module auf; jeder Bereich der Seite ist eine eigene
Funktion. Darunter liegen neun Module mit je einer Aufgabe: Laden, Geometrie,
Vergleich, Datenbank, Auswertung, Diagramme, 3D, Report.

Es gibt genau drei Klassen: `IfcModel` fuer eine geladene Datei,
`ElementChange` fuer eine einzelne Aenderung und `DiffResult` fuer das Ergebnis
eines Vergleichs. Alles andere sind Funktionen - eine Aufgabe, hoechstens
30 Zeilen, Docstring. Farben, Toleranzen und Pfade stehen zentral in
`config.py`, damit keine Magic Numbers im Code stehen.

## Folie 5 - Werkzeuge (60 s)

Entwickelt in Visual Studio Code, Python 3.13 in einer venv, Versionskontrolle
mit Git und GitHub. Ich habe je Etappe einen Commit gemacht, mit der Konvention
`[E2] ...`, und nach der lauffaehigen Oberflaeche einen Tag `v1.0-abgabefaehig`
gesetzt. Die requirements.txt ist eingefroren, das Repository ist oeffentlich.

## Folie 6 - Kernlogik (120 s)

Das ist der Kern. Schluessel ist die GlobalId, weil sie im IFC-Standard
eindeutig und ueber Exporte stabil ist. Jedes Element bekommt einen von vier
Zustaenden.

Fuer MODIFIED vergleiche ich drei Ebenen: die direkten Attribute, die
Property Sets und die Geometrie. Zwei Details, die wichtig sind: Zahlen
vergleiche ich mit einer Toleranz, nicht mit `==`, weil Fliesskommawerte je
Export minimal abweichen. Und das Matching laeuft ueber ein Dictionary -
bei zwei Dateien mit je n Elementen kostet das O(n) statt O(n²) bei
verschachtelten Schleifen.

Bewusst ausgeschlossen sind OwnerHistory, Zeitstempel und Entity-Nummern -
die aendern sich bei jedem Export, ohne dass sich an der Planung etwas aendert.

## Folie 7 - Testdaten (90 s)

Hier lag die groesste Huerde: Es gibt keine oeffentlichen IFC-Daten mit zwei
echten Planungsstaenden. Die buildingSMART-Testdaten liegen nur in
verschiedenen Schema-Versionen vor - ein Diff darauf zeigt Schema-Unterschiede,
keine Planungsaenderungen.

Deshalb habe ich einen Generator geschrieben, der aus einem Modell
reproduzierbar einen zweiten Stand erzeugt und die gemachten Aenderungen als
Ground Truth ablegt. Damit ist die Diff-Engine automatisiert pruefbar: jede
gesetzte Aenderung muss gefunden werden, und eine Datei gegen sich selbst muss
null ergeben. 35 Tests laufen gruen.

## Folie 8 und 9 - Demo (150 s)

*Wenn moeglich live vorfuehren, sonst die Bilder zeigen.*

Dateien waehlen, Vergleichen klicken. Oben die Kennzahlen, darunter die
filterbare Tabelle. Ein Klick auf eine Zeile zeigt die Detailansicht mit Wert
alt und Wert neu - hier zum Beispiel der geaenderte Name und das Volumen.

Im Tab 3D-Ansicht dasselbe raeumlich: neu gruen, geloescht rot, geaendert
orange, der unveraenderte Kontext transparent. Der Kontext ist umschaltbar,
und die Filter der Tabelle wirken auch hier. Zum Schluss der PDF-Report mit
Kennzahlen, Diagrammen, 3D-Bild und Tabelle.

## Folie 10 - Abgrenzungen (90 s)

Diese Grenzen sind bewusst gesetzt. Ich vergleiche die Geometrie ueber
Einfuegepunkt, Bounding-Box und Dreiecksanzahl - kein Mesh-Topologie-Vergleich.
Ein Bauteil, das bei gleicher Bounding-Box intern anders aufgebaut ist, gilt
als unveraendert. Verschiedene Schemata erzeugen eine Warnung. Und wenn ein
Werkzeug beim Export neue GlobalIds vergibt, erscheint alles als geloescht und
neu - ein hoher Anteil dieser beiden Arten ist genau der Hinweis darauf.

Dafuer ist die Performance geloest: Dict-Matching und ein Geometrie-Cache,
der das zweite Laden von knapp einer Sekunde auf drei Hundertstel bringt.

## Folie 11 - Entwicklung und Befunde (90 s)

Entwickelt habe ich in zehn Etappen, jede mit lauffaehigem Code, gruenen Tests
und einem Commit.

Drei Befunde haben Zeit gekostet und stehen im Code kommentiert: Eine ID aus
einem DataFrame ist ein `numpy.int64`, und SQLite liefert damit stillschweigend
null Zeilen - ohne Fehlermeldung. IFC-GlobalIds koennen auf einen Unterstrich
enden, was meine Cache-Schluessel zerlegt hat - der Test hat es gefunden. Und
`copy_class` aus der IfcOpenShell-API kopiert die Representation nicht, meine
duplizierten Testelemente hatten also keine Geometrie.

## Folie 12 - Fazit und Ausblick (60 s)

Entstanden ist ein lauffaehiges Werkzeug fuer eine taegliche Frage der
BIM-Koordination - mit einer Diff-Logik, die gegen eine selbst erzeugte
Ground Truth abgesichert ist. Ausbaubar waere der Viewer als interaktive
Einbettung, eine Regelpruefung mit Schwellenwerten, der Vergleich ueber mehr
als zwei Staende und eine Mengenauswertung als Kostenhinweis.

---

## Vorbereitung auf Fragen

**Zur Entwicklungsumgebung**

- *Wie richten Sie eine venv ein?* `python -m venv myenv`, aktivieren mit
  `myenv\Scripts\activate`, Module mit pip, danach `pip freeze > requirements.txt`.
- *Wie arbeiten Sie mit Git?* Je Etappe ein Commit mit sprechender Meldung,
  Arbeit auf `main`, Push auf GitHub, ein Tag fuer den abgabefaehigen Stand.
  Der Token gehoert nicht in die Remote-URL, sondern in den Credential Manager.
- *Warum Streamlit und nicht TkInter?* Streamlit ist fuer datenlastige
  Oberflaechen gebaut: Tabelle, Filter, Diagramme und Download sind je eine
  Zeile. TkInter waere fuer dieselbe Oberflaeche ein Vielfaches an Code.

**Zum Code**

- *Warum genau drei Klassen?* Eine Klasse lohnt sich, wo Daten und Verhalten
  zusammengehoeren: die Datei, die einzelne Aenderung, das Ergebnis. Alles
  andere sind Funktionen ohne Zustand.
- *Was macht `@dataclass`?* Erzeugt automatisch `__init__` und `__repr__` fuer
  reine Datenklassen - spart Code, den ich sonst selbst schreiben muesste.
- *Warum `get_container()` statt `get_inverse()` wie im Unterricht?* Dasselbe
  Ergebnis in einer Zeile statt acht; die Abweichung ist im Code kommentiert.
- *Wie gehen Sie mit Fehlern um?* Je Element, nicht global: eine kaputte
  Geometrie darf nicht den ganzen Durchlauf abbrechen.

**Zum Fachlichen**

- *Warum GlobalId und nicht Name?* Namen koennen doppelt sein und sich aendern;
  die GlobalId ist im Standard eindeutig.
- *Wie gross duerfen die Modelle sein?* Der Attributvergleich ist unkritisch.
  Die Geometrie ist der Engpass - dafuer gibt es den Cache und die Option,
  nur die Aenderungen zu rendern.
- *Was waere der naechste sinnvolle Schritt?* Schwellenwerte statt reiner
  Erkennung: nicht nur «verschoben», sondern «um mehr als 5 cm verschoben».
