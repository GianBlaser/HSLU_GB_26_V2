const pptxgen = require("pptxgenjs");
const path = require("path");

const PROJ = "C:/HSLU_Programming/HSLU_GB_26/02_Semesterprojekt";
const OUT = path.join(PROJ, "docs", "MEP", "DT_PROGR_HS26_MEP_GianBlaser_Praesentation.pptx");
const SHOT = (n) => path.join(PROJ, "docs", "screenshots", n);

const C = {
  dark: "1F2933", ink: "323F4B", muted: "7B8794", line: "CBD2D9", light: "F5F7FA", white: "FFFFFF",
  added: "2E9E5B", deleted: "D1434A", modified: "E08A1E", unchanged: "9AA0A6",
};
const FONT_H = "Cambria";
const FONT_B = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Gian Blaser";
pres.title = "IFC-Diff Viewer - MEP";

const W = 13.33, H = 7.5, M = 0.6;
let n = 0;

function base(dark = false) {
  const s = pres.addSlide();
  s.background = { color: dark ? C.dark : C.white };
  return s;
}
function title(s, text, dark = false) {
  s.addText(text, { x: M, y: 0.45, w: W - 2 * M, h: 0.8, fontFace: FONT_H, fontSize: 30, bold: true,
    color: dark ? C.white : C.dark, isTextBox: true, margin: 0 });
}
function footer(s, dark = false) {
  n++;
  s.addText("DT_PROGR HS26 · Modulendpruefung · Gian Blaser · IFC-Diff Viewer",
    { x: M, y: H - 0.5, w: 9, h: 0.3, fontFace: FONT_B, fontSize: 10, color: dark ? C.line : C.muted, isTextBox: true, margin: 0 });
  s.addText(String(n), { x: W - M - 1, y: H - 0.5, w: 1, h: 0.3, fontFace: FONT_B, fontSize: 10,
    color: dark ? C.line : C.muted, align: "right", isTextBox: true, margin: 0 });
}
function bullets(s, items, o) {
  o = Object.assign({ x: M, y: 1.45, w: 6.2, h: 4.6, fontSize: 15 }, o || {});
  const runs = items.map((t, i) => (typeof t === "string"
    ? { text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 } }
    : Object.assign({}, t, { options: Object.assign({ bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 8 }, t.options || {}) })));
  s.addText(runs, { x: o.x, y: o.y, w: o.w, h: o.h, fontFace: FONT_B, fontSize: o.fontSize, color: C.ink,
    valign: "top", isTextBox: true, margin: 0 });
}
function card(s, x, y, w, h, head, text, color) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.08 });
  s.addShape(pres.ShapeType.ellipse, { x: x + 0.2, y: y + 0.22, w: 0.3, h: 0.3, fill: { color }, line: { color } });
  s.addText(head, { x: x + 0.62, y: y + 0.15, w: w - 0.8, h: 0.45, fontFace: FONT_B, fontSize: 14.5, bold: true, color: C.dark, isTextBox: true, margin: 0, valign: "middle" });
  s.addText(text, { x: x + 0.2, y: y + 0.68, w: w - 0.4, h: h - 0.82, fontFace: FONT_B, fontSize: 12, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
}
function codeBox(s, x, y, w, h, runs, fontSize) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: C.dark }, line: { color: C.dark }, rectRadius: 0.08 });
  s.addText(runs, { x: x + 0.22, y: y + 0.18, w: w - 0.44, h: h - 0.36, fontFace: "Courier New",
    fontSize: fontSize || 11.5, color: C.white, isTextBox: true, margin: 0, valign: "top" });
}

// 1 Titel ---------------------------------------------------------------
{
  const s = base(true);
  s.addText("IFC-Diff Viewer", { x: M, y: 2.0, w: 9, h: 1.1, fontFace: FONT_H, fontSize: 46, bold: true, color: C.white, isTextBox: true, margin: 0 });
  s.addText("Zwei Modellstaende vergleichen - tabellarisch, statistisch, im 3D",
    { x: M, y: 3.1, w: 9.5, h: 0.6, fontFace: FONT_B, fontSize: 20, italic: true, color: C.line, isTextBox: true, margin: 0 });
  s.addText([
    { text: "Modulendpruefung - TA.BA_DT_PROGR Digital Twin Programmieren, HS26", options: { breakLine: true } },
    { text: "Gian Blaser · Bachelor Digital Construction, Hochschule Luzern", options: { breakLine: true } },
    { text: "github.com/GianBlaser/HSLU_GB_26_V2" },
  ], { x: M, y: 4.8, w: 10, h: 1.4, fontFace: FONT_B, fontSize: 14, color: C.line, isTextBox: true, margin: 0 });
  [[C.added, "ADDED"], [C.deleted, "DELETED"], [C.modified, "MODIFIED"]].forEach(([c, t], i) => {
    s.addShape(pres.ShapeType.roundRect, { x: 10.3, y: 2.0 + i * 0.9, w: 2.4, h: 0.7, fill: { color: c }, line: { color: c }, rectRadius: 0.1 });
    s.addText(t, { x: 10.3, y: 2.0 + i * 0.9, w: 2.4, h: 0.7, fontFace: FONT_B, fontSize: 15, bold: true, color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 10.3, y: 4.7, w: 2.4, h: 0.7, fill: { color: C.unchanged, transparency: 75 }, line: { color: C.unchanged }, rectRadius: 0.1 });
  s.addText("UNCHANGED", { x: 10.3, y: 4.7, w: 2.4, h: 0.7, fontFace: FONT_B, fontSize: 15, bold: true, color: C.line, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  s.addNotes("10-15 Min. Ablauf: Problem (1) - Ansatz (2-3) - Architektur (4-5) - Kernlogik (6) - Testdaten (7) - Demo (8-9) - Abgrenzungen (10) - Entwicklung (11) - Ausblick (12).");
}

// 2 Problem -------------------------------------------------------------
{
  const s = base();
  title(s, "Das Problem: Modellstaende vergleichen ist Handarbeit");
  bullets(s, [
    "In der BIM-Koordination kommen laufend neue IFC-Staende: Architektur, Tragwerk, Gebaeudetechnik.",
    "Die Frage «Was ist neu, was fehlt, was wurde verschoben?» wird per Sichtvergleich im Viewer oder per Excel-Export beantwortet.",
    "Fehleranfaellig, nicht reproduzierbar, nicht dokumentiert.",
    "Kommerzielle Werkzeuge koennen das - kostenpflichtig und in ihrer Logik nicht einsehbar.",
  ], { w: 7.2, fontSize: 16 });
  s.addShape(pres.ShapeType.roundRect, { x: 8.4, y: 1.45, w: 4.3, h: 4.7, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.1 });
  s.addText("1 : 1", { x: 8.4, y: 1.9, w: 4.3, h: 1.3, fontFace: FONT_H, fontSize: 60, bold: true, color: C.dark, align: "center", isTextBox: true, margin: 0 });
  s.addText("Element fuer Element ueber die GlobalId", { x: 8.7, y: 3.3, w: 3.7, h: 0.8, fontFace: FONT_B, fontSize: 14, color: C.ink, align: "center", isTextBox: true, margin: 0 });
  s.addText("Kontext gemaess Merkblatt:\nDatenauswertung und Daten-Visualisierung", { x: 8.7, y: 4.9, w: 3.7, h: 1.0, fontFace: FONT_B, fontSize: 12, italic: true, color: C.muted, align: "center", isTextBox: true, margin: 0 });
  footer(s);
}

// 3 Loesung in 7 Schritten ----------------------------------------------
{
  const s = base();
  title(s, "Die Loesung: eine durchgehende Kette");
  const items = [
    ["1", "Laden", "Zwei IFC-Dateien, Auswahl oder Upload"],
    ["2", "Vergleichen", "Matching ueber GlobalId, drei Ebenen"],
    ["3", "Speichern", "Jeder Lauf in SQLite - Historie"],
    ["4", "Auswerten", "Pandas: je Geschoss, je IfcClass, je Art"],
    ["5", "Visualisieren", "Matplotlib-Diagramme"],
    ["6", "3D-Ansicht", "geaendert farbig, Kontext transparent"],
    ["7", "Exportieren", "CSV und PDF-Report"],
  ];
  items.forEach(([num, head, text], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.15, y = 1.5 + row * 1.15;
    s.addShape(pres.ShapeType.ellipse, { x, y: y + 0.08, w: 0.55, h: 0.55, fill: { color: C.dark }, line: { color: C.dark } });
    s.addText(num, { x, y: y + 0.08, w: 0.55, h: 0.55, fontFace: FONT_B, fontSize: 15, bold: true, color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(head, { x: x + 0.75, y, w: 5.2, h: 0.4, fontFace: FONT_B, fontSize: 15, bold: true, color: C.dark, isTextBox: true, margin: 0 });
    s.addText(text, { x: x + 0.75, y: y + 0.4, w: 5.2, h: 0.6, fontFace: FONT_B, fontSize: 12.5, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
  });
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 6.25, w: W - 2 * M, h: 0.65, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.08 });
  s.addText("Alle Pflichtmodule im Einsatz: IfcOpenShell · Pandas · Matplotlib · SQLite · Streamlit   (+ PyVista, NumPy)",
    { x: M + 0.25, y: 6.25, w: W - 2 * M - 0.5, h: 0.65, fontFace: FONT_B, fontSize: 13, bold: true, color: C.dark, valign: "middle", isTextBox: true, margin: 0 });
  footer(s);
}

// 4 Architektur ----------------------------------------------------------
{
  const s = base();
  title(s, "Architektur: modularer Aufbau");
  s.addImage({ path: path.join(PROJ, "docs", "architektur.png"), x: 1.35, y: 1.3, w: 7.6, h: 5.55 });
  card(s, 9.2, 1.4, 3.55, 1.65, "Hauptkomponente", "app.py - Streamlit. Je Seitenbereich eine Funktion, main() setzt zusammen.", C.dark);
  card(s, 9.2, 3.25, 3.55, 1.65, "Klassen", "IfcModel, ElementChange, DiffResult - mehr braucht es nicht.", C.modified);
  card(s, 9.2, 5.1, 3.55, 1.65, "Hilfsfunktionen", "Ein Zweck je Funktion, max. 30 Zeilen, Docstring, Typ-Hints.", C.added);
  footer(s);
}

// 5 Werkzeuge ------------------------------------------------------------
{
  const s = base();
  title(s, "Entwicklungsumgebung und Module");
  const rows = [
    [{ text: "Bereich", options: { bold: true, color: C.white, fill: { color: C.dark } } },
     { text: "Werkzeug", options: { bold: true, color: C.white, fill: { color: C.dark } } },
     { text: "Einsatz im Projekt", options: { bold: true, color: C.white, fill: { color: C.dark } } }],
    ["Sprache", "Python 3.13", "venv myenv/ im Repo-Root, requirements.txt eingefroren"],
    ["Editor", "Visual Studio Code", "Python-Extension, integriertes Terminal, Git-Ansicht"],
    ["Versionskontrolle", "Git + GitHub (public)", "ein Commit je Etappe, Konvention [E2] ..., Tag v1.0-abgabefaehig"],
    ["IFC", "IfcOpenShell 0.8.5", "Pflicht-Modul: Lesen, Psets, Container, Geometrie, API"],
    ["Daten", "Pandas 3.0", "Vergleichstabelle, Pivots mit crosstab, Filter"],
    ["Diagramme", "Matplotlib 3.11", "Balkendiagramme und PDF-Report (PdfPages)"],
    ["Datenbank", "SQLite (stdlib)", "drei Tabellen: comparison, element_change, attribute_change"],
    ["Oberflaeche", "Streamlit 1.64", "Upload, Filter, Tabelle mit Zeilenauswahl, vier Tabs"],
    ["3D", "PyVista 0.49", "offscreen gerendertes Bild - keine Zusatzkomponente noetig"],
    ["Tests", "pytest", "35 Tests, Diff-Engine gegen Ground Truth"],
  ];
  s.addTable(rows, { x: M, y: 1.4, w: W - 2 * M, colW: [2.2, 3.0, 6.93], fontFace: FONT_B, fontSize: 12.5,
    color: C.ink, border: { type: "solid", color: C.line, pt: 0.5 }, rowH: 0.43, valign: "middle", margin: 0.06 });
  footer(s);
}

// 6 Kernlogik ------------------------------------------------------------
{
  const s = base();
  title(s, "Kernlogik: Was gilt als «geaendert»?");
  const states = [
    [C.added, "ADDED", "GlobalId nur in B"],
    [C.deleted, "DELETED", "GlobalId nur in A"],
    [C.modified, "MODIFIED", "in beiden, eine Ebene weicht ab"],
    [C.unchanged, "UNCHANGED", "in beiden, alles gleich"],
  ];
  states.forEach(([c, t, d], i) => {
    const x = M + i * 3.07;
    s.addShape(pres.ShapeType.roundRect, { x, y: 1.4, w: 2.85, h: 1.0, fill: { color: c }, line: { color: c }, rectRadius: 0.08 });
    s.addText(t, { x, y: 1.45, w: 2.85, h: 0.42, fontFace: FONT_B, fontSize: 15, bold: true, color: C.white, align: "center", isTextBox: true, margin: 0 });
    s.addText(d, { x: x + 0.1, y: 1.85, w: 2.65, h: 0.5, fontFace: FONT_B, fontSize: 11.5, color: C.white, align: "center", isTextBox: true, margin: 0 });
  });
  card(s, M, 2.7, 3.93, 2.0, "1  Direktattribute", "Name, Description, ObjectType, Tag, PredefinedType - Liste in config.py", C.dark);
  card(s, M + 4.1, 2.7, 3.93, 2.0, "2  Property Sets", "get_psets() flach als «Pset.Property». Zahlen mit Toleranz 1e-6, nicht mit ==.", C.dark);
  card(s, M + 8.2, 2.7, 3.93, 2.0, "3  Geometrie", "Einfuegepunkt, Bounding-Box (1 mm), Dreiecksanzahl - kein Mesh-Vergleich.", C.dark);
  codeBox(s, M, 4.95, W - 2 * M, 1.55, [
    { text: "# Matching ueber ein Dictionary statt verschachtelter Schleifen: O(n) statt O(n²)", options: { color: C.line, breakLine: true } },
    { text: "for guid in model_a.elements:", options: { breakLine: true } },
    { text: "    if guid in model_b.elements:      # Dict-Lookup", options: { breakLine: true } },
    { text: "        changes.append(compare_element(model_a, model_b, guid))", options: {} },
  ], 12);
  footer(s);
}

// 7 Testdaten ------------------------------------------------------------
{
  const s = base();
  title(s, "Eigenleistung: Testdaten mit Ground Truth");
  const blocks = [
    ["Problem", "Keine oeffentlichen IFC-Datensaetze mit zwei echten Planungsstaenden - die buildingSMART-Daten liegen nur in verschiedenen Schema-Versionen vor.", C.deleted],
    ["Loesung", "tools/make_variant.py erzeugt aus Stand A reproduzierbar (Seed) einen Stand B: loeschen, verschieben, umbenennen, duplizieren. Alle Aenderungen in ground_truth.json.", C.modified],
    ["Effekt", "Die Diff-Engine ist beweisbar korrekt: jede gesetzte Aenderung muss gefunden werden, A gegen A muss 0 ergeben.", C.added],
  ];
  blocks.forEach(([h, t, c], i) => {
    const y = 1.45 + i * 1.6;
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 0.02, w: 0.3, h: 0.3, fill: { color: c }, line: { color: c } });
    s.addText(h, { x: M + 0.45, y: y - 0.05, w: 6, h: 0.4, fontFace: FONT_B, fontSize: 16, bold: true, color: C.dark, isTextBox: true, margin: 0 });
    s.addText(t, { x: M + 0.45, y: y + 0.38, w: 6.6, h: 1.15, fontFace: FONT_B, fontSize: 13, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
  });
  codeBox(s, 8.1, 1.45, 4.6, 4.7, [
    { text: "pytest 02_Semesterprojekt/tests", options: { color: C.line, breakLine: true } },
    { text: "35 passed", options: { color: C.added, bold: true, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "test_diff_engine.py   Ground Truth", options: { breakLine: true } },
    { text: "test_database.py      SQLite", options: { breakLine: true } },
    { text: "test_analytics.py     Pivots", options: { breakLine: true } },
    { text: "test_geometry.py      Cache", options: { breakLine: true } },
    { text: "test_viewer.py        Szene", options: { breakLine: true } },
    { text: "test_report.py        PDF", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "A gegen B:  2 / 2 / 4 / 14", options: { color: C.line, bold: true, breakLine: true } },
    { text: "A gegen A:  0 / 0 / 0 / 20", options: { color: C.line, bold: true } },
  ], 12);
  footer(s);
}

// 8 Demo Tabelle ---------------------------------------------------------
{
  const s = base();
  title(s, "Die Anwendung: Tabelle mit Filter und Detailansicht");
  s.addImage({ path: SHOT("app_tabelle.png"), x: 2.55, y: 1.3, w: 8.2, h: 5.4 });
  footer(s);
}

// 9 Demo 3D --------------------------------------------------------------
{
  const s = base();
  title(s, "3D-Ansicht: Aenderungen im transparenten Kontext");
  s.addImage({ path: SHOT("viewer_transparent.png"), x: 0.9, y: 1.45, w: 8.0, h: 4.73 });
  card(s, 9.2, 1.45, 3.55, 1.5, "Farben", "Gruen neu, rot geloescht (aus Stand A), orange geaendert.", C.added);
  card(s, 9.2, 3.1, 3.55, 1.5, "Kontext", "transparent, nur Kanten oder aus - umschaltbar.", C.unchanged);
  card(s, 9.2, 4.75, 3.55, 1.5, "Kopplung", "Filter und Zeilenklick der Tabelle wirken auf die Ansicht.", C.modified);
  footer(s);
}

// 10 Abgrenzungen --------------------------------------------------------
{
  const s = base();
  title(s, "Abgrenzungen - bewusst gesetzt");
  const cards = [
    [C.deleted, "Kein Mesh-Topologie-Vergleich", "Geometrie ueber Einfuegepunkt, Bounding-Box und Dreiecksanzahl. Ein intern anders aufgebautes Bauteil gleicher Groesse gilt als unveraendert."],
    [C.modified, "Nur gleiche Schemata sinnvoll", "IFC2x3 gegen IFC4 erzeugt eine Warnung; der Vergleich laeuft, das Ergebnis ist unsicher."],
    [C.modified, "Neue GUIDs nicht erkennbar", "Vergibt ein Werkzeug beim Export neue GlobalIds, erscheint alles als DELETED + ADDED. Ein hoher Anteil ist der Hinweis darauf."],
    [C.ink, "3D-Ansicht ist ein Bild", "Offscreen gerendert statt interaktiv eingebettet - dafuer laeuft sie ohne Zusatzkomponente zuverlaessig."],
    [C.added, "Testbarkeit geloest", "Fehlende Zwei-Staende-Testdaten durch eigenen Generator mit Ground Truth ersetzt."],
    [C.added, "Performance", "Dict-Matching O(n); Geometrie-Cache als npz: 0.88 s beim ersten Laden, 0.03 s danach."],
  ];
  cards.forEach(([c, h, t], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    card(s, M + col * 4.1, 1.4 + row * 2.6, 3.93, 2.4, h, t, c);
  });
  footer(s);
}

// 11 Entwicklung ---------------------------------------------------------
{
  const s = base();
  title(s, "Entwicklung in Etappen - und was dabei schiefging");
  const et = ["E0 Geruest", "E1 Testdaten", "E2 Diff-Engine", "E3 SQLite", "E4 Auswertung",
              "E5 Streamlit-UI", "E6 Geometrie", "E7 3D-Viewer", "E8 Report", "E9 Doku"];
  et.forEach((t, i) => {
    const x = M + (i % 5) * 2.45, y = 1.4 + Math.floor(i / 5) * 0.75;
    s.addShape(pres.ShapeType.roundRect, { x, y, w: 2.25, h: 0.55, fill: { color: C.added }, line: { color: C.added }, rectRadius: 0.08 });
    s.addText(t, { x, y, w: 2.25, h: 0.55, fontFace: FONT_B, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addText("Jede Etappe: lauffaehiger Code, gruene Tests, ein Commit. Tag v1.0-abgabefaehig nach E5.",
    { x: M, y: 2.95, w: W - 2 * M, h: 0.4, fontFace: FONT_B, fontSize: 13, italic: true, color: C.muted, isTextBox: true, margin: 0 });
  s.addText("Drei Befunde, die Zeit gekostet haben - und im Code kommentiert sind:",
    { x: M, y: 3.5, w: W - 2 * M, h: 0.4, fontFace: FONT_B, fontSize: 15, bold: true, color: C.dark, isTextBox: true, margin: 0 });
  card(s, M, 3.95, 3.93, 2.3, "numpy.int64 in SQLite", "Eine ID aus einem DataFrame als Parameter liefert stillschweigend 0 Zeilen - kein Fehler. Loesung: int(). Eigener Regressionstest.", C.deleted);
  card(s, M + 4.1, 3.95, 3.93, 2.3, "GUIDs enden auf _", "Der npz-Cache trennte Schluessel mit __ - bei GUIDs auf _ brach das. Jetzt |, das im GUID-Alphabet nicht vorkommt. Vom Test gefunden.", C.deleted);
  card(s, M + 8.2, 3.95, 3.93, 2.3, "copy_class ohne Geometrie", "ifcopenshell.api kopiert die Representation nicht - Kopien im Testdatensatz waren unsichtbar. Jetzt explizit gesetzt.", C.deleted);
  footer(s);
}

// 12 Ausblick ------------------------------------------------------------
{
  const s = base(true);
  title(s, "Fazit und Ausblick", true);
  s.addText([
    { text: "Ein lauffaehiges Werkzeug fuer eine taegliche Frage der BIM-Koordination.", options: { bold: true, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Durchgehende Kette von der IFC-Datei bis zum PDF-Report, 35 Tests, ", options: {} },
    { text: "Diff-Logik gegen eine selbst erzeugte Ground Truth abgesichert.", options: {} },
  ], { x: M, y: 1.4, w: 7.2, h: 1.6, fontFace: FONT_B, fontSize: 16, color: C.line, isTextBox: true, margin: 0, valign: "top" });
  const next = [
    ["Interaktiver Viewer", "Einbettung statt Standbild (stpyvista)"],
    ["Regelpruefung", "Schwellenwerte: «Wand um mehr als 5 cm verschoben»"],
    ["Mehr als zwei Staende", "Zeitreihe ueber die SQLite-Historie"],
    ["Mengenauswertung", "geaenderte Mengen als Kostenhinweis"],
  ];
  s.addText("Naechste Schritte", { x: M, y: 3.2, w: 6, h: 0.4, fontFace: FONT_B, fontSize: 16, bold: true, color: C.white, isTextBox: true, margin: 0 });
  next.forEach(([h, t], i) => {
    const y = 3.7 + i * 0.75;
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 0.08, w: 0.28, h: 0.28, fill: { color: C.added }, line: { color: C.added } });
    s.addText(h, { x: M + 0.45, y, w: 3.0, h: 0.45, fontFace: FONT_B, fontSize: 13.5, bold: true, color: C.white, valign: "middle", isTextBox: true, margin: 0 });
    s.addText(t, { x: M + 3.5, y, w: 5.0, h: 0.45, fontFace: FONT_B, fontSize: 13, color: C.line, valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addImage({ path: SHOT("viewer_transparent.png"), x: 9.0, y: 2.4, w: 3.8, h: 2.25 });
  s.addText("github.com/GianBlaser/HSLU_GB_26_V2", { x: 9.0, y: 4.8, w: 3.8, h: 0.4, fontFace: FONT_B, fontSize: 12, color: C.line, align: "center", isTextBox: true, margin: 0 });
  footer(s, true);
}

pres.writeFile({ fileName: OUT }).then(f => console.log("written", f));
