const pptxgen = require("pptxgenjs");
const path = require("path");

const PROJ = "C:/HSLU_Programming/HSLU_GB_26/02_Semesterprojekt";
const OUT = path.join(PROJ, "docs", "ZP1", "DT_PROGR_HS26_ZP1_GianBlaser_Praesentation.pptx");

// Palette: dunkles Schiefer + die drei Diff-Farben aus config.py
const C = {
  dark: "1F2933", ink: "323F4B", muted: "7B8794", line: "CBD2D9", light: "F5F7FA", white: "FFFFFF",
  added: "2E9E5B", deleted: "D1434A", modified: "E08A1E", unchanged: "9AA0A6",
};
const FONT_H = "Cambria";
const FONT_B = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "Gian Blaser";
pres.title = "IFC-Diff Viewer - ZP1";

const W = 13.33, H = 7.5, M = 0.6;

function base(slide, dark = false) {
  slide.background = { color: dark ? C.dark : C.white };
  return slide;
}
function title(slide, text, dark = false) {
  slide.addText(text, { x: M, y: 0.45, w: W - 2 * M, h: 0.8, fontFace: FONT_H, fontSize: 32, bold: true,
    color: dark ? C.white : C.dark, isTextBox: true, margin: 0 });
}
function footer(slide, n, dark = false) {
  slide.addText(`DT_PROGR HS26  ·  ZP1  ·  Gian Blaser  ·  IFC-Diff Viewer`, { x: M, y: H - 0.5, w: 8, h: 0.3,
    fontFace: FONT_B, fontSize: 10, color: dark ? C.line : C.muted, isTextBox: true, margin: 0 });
  slide.addText(String(n), { x: W - M - 1, y: H - 0.5, w: 1, h: 0.3, fontFace: FONT_B, fontSize: 10,
    color: dark ? C.line : C.muted, align: "right", isTextBox: true, margin: 0 });
}
function body(slide, items, opts) {
  const o = Object.assign({ x: M, y: 1.5, w: 6, h: 4.5, fontSize: 15, color: C.ink }, opts || {});
  const runs = items.map((t, i) => (typeof t === "string"
    ? { text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6 } }
    : Object.assign({ options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6 } }, t)));
  slide.addText(runs, { x: o.x, y: o.y, w: o.w, h: o.h, fontFace: FONT_B, fontSize: o.fontSize, color: o.color,
    valign: "top", isTextBox: true, margin: 0 });
}
function card(slide, x, y, w, h, head, text, color) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.08 });
  slide.addShape(pres.ShapeType.ellipse, { x: x + 0.2, y: y + 0.2, w: 0.35, h: 0.35, fill: { color }, line: { color } });
  slide.addText(head, { x: x + 0.7, y: y + 0.15, w: w - 0.9, h: 0.45, fontFace: FONT_B, fontSize: 15, bold: true, color: C.dark, isTextBox: true, margin: 0, valign: "middle" });
  slide.addText(text, { x: x + 0.2, y: y + 0.7, w: w - 0.4, h: h - 0.85, fontFace: FONT_B, fontSize: 12.5, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
}
function tag(slide, x, y, text, color) {
  slide.addShape(pres.ShapeType.roundRect, { x, y, w: 1.55, h: 0.42, fill: { color }, line: { color }, rectRadius: 0.1 });
  slide.addText(text, { x, y, w: 1.55, h: 0.42, fontFace: FONT_B, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
}

let n = 0;

// 1 Titel ------------------------------------------------------------------
{
  const s = base(pres.addSlide(), true); n++;
  s.addText("IFC-Diff Viewer", { x: M, y: 2.0, w: 9, h: 1.1, fontFace: FONT_H, fontSize: 48, bold: true, color: C.white, isTextBox: true, margin: 0 });
  s.addText("Was hat sich seit dem letzten Modellstand geändert?", { x: M, y: 3.1, w: 10, h: 0.6, fontFace: FONT_B, fontSize: 22, italic: true, color: C.line, isTextBox: true, margin: 0 });
  s.addText([
    { text: "Zwischenpräsentation 1 – Konzept Semesterprojekt", options: { breakLine: true } },
    { text: "Modul TA.BA_DT_PROGR Digital Twin Programmieren, HS26", options: { breakLine: true } },
    { text: "Gian Blaser · Hochschule Luzern, Digital Construction", options: { breakLine: true } },
    { text: "github.com/GianBlaser/HSLU_GB_26_V2" },
  ], { x: M, y: 4.6, w: 10, h: 1.6, fontFace: FONT_B, fontSize: 14, color: C.line, isTextBox: true, margin: 0 });
  // Farbmotiv: drei Kacheln der Diff-Zustaende
  [[C.added, "ADDED"], [C.deleted, "DELETED"], [C.modified, "MODIFIED"]].forEach(([c, t], i) => {
    s.addShape(pres.ShapeType.roundRect, { x: 10.3, y: 2.0 + i * 0.9, w: 2.4, h: 0.7, fill: { color: c }, line: { color: c }, rectRadius: 0.1 });
    s.addText(t, { x: 10.3, y: 2.0 + i * 0.9, w: 2.4, h: 0.7, fontFace: FONT_B, fontSize: 16, bold: true, color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addShape(pres.ShapeType.roundRect, { x: 10.3, y: 4.7, w: 2.4, h: 0.7, fill: { color: C.unchanged, transparency: 75 }, line: { color: C.unchanged }, rectRadius: 0.1 });
  s.addText("UNCHANGED", { x: 10.3, y: 4.7, w: 2.4, h: 0.7, fontFace: FONT_B, fontSize: 16, bold: true, color: C.line, align: "center", valign: "middle", isTextBox: true, margin: 0 });
  s.addNotes("Kurzpräsentation (3 Min): Folien 1, 2, 4, 8, 10. Übrige Folien = ausführlicher schriftlicher Teil.");
}

// 2 Ausgangslage -------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Ausgangslage: Modellstände vergleichen ist Handarbeit");
  body(s, [
    "In der BIM-Koordination kommen laufend neue IFC-Stände: Architektur, Tragwerk, HLKS – wöchentlich, manchmal täglich.",
    "Die Frage «Was ist neu, was fehlt, was wurde verschoben?» wird heute meist per Sichtvergleich im Viewer oder per Excel-Export beantwortet.",
    "Fehleranfällig, nicht reproduzierbar, nicht dokumentiert.",
    "Kommerzielle Tools (Solibri, BIMcollab) können das – aber als Blackbox und kostenpflichtig.",
  ], { w: 7.2, fontSize: 16 });
  // rechte Seite: grosse Zahl
  s.addShape(pres.ShapeType.roundRect, { x: 8.4, y: 1.5, w: 4.3, h: 4.6, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.1 });
  s.addText("1 : 1", { x: 8.4, y: 1.8, w: 4.3, h: 1.4, fontFace: FONT_H, fontSize: 64, bold: true, color: C.dark, align: "center", isTextBox: true, margin: 0 });
  s.addText("Element für Element über die GlobalId –\nnicht «ungefähr hinschauen»", { x: 8.7, y: 3.3, w: 3.7, h: 1.0, fontFace: FONT_B, fontSize: 14, color: C.ink, align: "center", isTextBox: true, margin: 0 });
  s.addText("Kontext gemäss Merkblatt:\nDatenauswertung + Daten-Visualisierung", { x: 8.7, y: 4.6, w: 3.7, h: 1.2, fontFace: FONT_B, fontSize: 12, italic: true, color: C.muted, align: "center", isTextBox: true, margin: 0 });
  footer(s, n);
}

// 3 Zielsetzung ------------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Zielsetzung und Funktionsumfang");
  s.addText("Ein Python-Programm, das zwei IFC-Stände desselben Projekts vergleicht und die Unterschiede tabellarisch, statistisch und im 3D-Viewer farbcodiert zeigt.",
    { x: M, y: 1.4, w: W - 2 * M, h: 0.8, fontFace: FONT_B, fontSize: 16, color: C.ink, isTextBox: true, margin: 0 });
  const items = [
    ["1", "Laden", "Zwei IFC-Dateien: Stand A (alt), Stand B (neu) – Auswahl oder Upload"],
    ["2", "Vergleichen", "Matching über GlobalId → ADDED / DELETED / MODIFIED / UNCHANGED"],
    ["3", "Speichern", "Jeder Lauf in SQLite: Historie aller Vergleiche"],
    ["4", "Auswerten", "Pandas: Änderungen je Geschoss, je IfcClass, je Änderungsart"],
    ["5", "Visualisieren", "Matplotlib-Diagramme; 3D-Viewer: geändert opak farbig, Kontext transparent"],
    ["6", "Exportieren", "CSV heute, PDF-Report geplant"],
  ];
  items.forEach(([num, head, text], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = M + col * 6.15, y = 2.45 + row * 1.35;
    s.addShape(pres.ShapeType.ellipse, { x, y: y + 0.1, w: 0.6, h: 0.6, fill: { color: C.dark }, line: { color: C.dark } });
    s.addText(num, { x, y: y + 0.1, w: 0.6, h: 0.6, fontFace: FONT_B, fontSize: 16, bold: true, color: C.white, align: "center", valign: "middle", isTextBox: true, margin: 0 });
    s.addText(head, { x: x + 0.8, y, w: 5.2, h: 0.4, fontFace: FONT_B, fontSize: 16, bold: true, color: C.dark, isTextBox: true, margin: 0 });
    s.addText(text, { x: x + 0.8, y: y + 0.42, w: 5.2, h: 0.75, fontFace: FONT_B, fontSize: 13, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
  });
  footer(s, n);
}

// 4 Kernlogik ----------------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Kernlogik: Was gilt als «geändert»?");
  s.addText("Eigene Diff-Definition – Schlüssel ist die GlobalId, Matching per Dictionary statt verschachtelter Schleifen.",
    { x: M, y: 1.35, w: W - 2 * M, h: 0.5, fontFace: FONT_B, fontSize: 15, color: C.ink, isTextBox: true, margin: 0 });
  // 4 Zustaende
  const states = [
    [C.added, "ADDED", "GlobalId nur in Stand B"],
    [C.deleted, "DELETED", "GlobalId nur in Stand A"],
    [C.modified, "MODIFIED", "in beiden, mind. eine Ebene weicht ab"],
    [C.unchanged, "UNCHANGED", "in beiden, alle Ebenen gleich"],
  ];
  states.forEach(([c, t, d], i) => {
    const x = M + i * 3.07;
    s.addShape(pres.ShapeType.roundRect, { x, y: 2.0, w: 2.85, h: 1.1, fill: { color: c }, line: { color: c }, rectRadius: 0.08 });
    s.addText(t, { x, y: 2.05, w: 2.85, h: 0.45, fontFace: FONT_B, fontSize: 16, bold: true, color: C.white, align: "center", isTextBox: true, margin: 0 });
    s.addText(d, { x: x + 0.1, y: 2.5, w: 2.65, h: 0.55, fontFace: FONT_B, fontSize: 12, color: C.white, align: "center", isTextBox: true, margin: 0 });
  });
  // 3 Ebenen
  s.addText("Drei Vergleichsebenen je Element", { x: M, y: 3.4, w: 8, h: 0.4, fontFace: FONT_B, fontSize: 16, bold: true, color: C.dark, isTextBox: true, margin: 0 });
  card(s, M, 3.9, 3.9, 2.4, "1  Direktattribute", "Name, Description, ObjectType, Tag, PredefinedType – exakter Vergleich", C.dark);
  card(s, M + 4.1, 3.9, 3.9, 2.4, "2  Property Sets", "get_psets() flach als «Pset.Property». Zahlen mit Toleranz 1e-6, nicht mit ==. Entity-IDs und OwnerHistory ausgeschlossen.", C.dark);
  card(s, M + 8.2, 3.9, 3.9, 2.4, "3  Geometrie (vereinfacht)", "Heute: Einfügepunkt (Toleranz 1 mm). Geplant: Bounding-Box-Schwerpunkt, Abmessungen, Dreiecksanzahl. Bewusst kein Mesh-Topologie-Vergleich.", C.dark);
  footer(s, n);
}

// 5 Architektur ------------------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Architektur: modularer Aufbau");
  const bw = 2.75, bh = 1.35, gap = 0.31;
  const col = i => M + i * (bw + gap);
  const boxes = [
    // [col, y, label, sub, color]
    [0, 1.5, "ifc_loader.py", "Klasse IfcModel\nGUID-Dict, Psets, Geschoss", C.ink],
    [1, 1.5, "diff_engine.py", "ElementChange, DiffResult\ncompare_models()", C.modified],
    [2, 1.5, "database.py", "SQLite: comparison,\nelement_change, attribute_change", C.ink],
    [3, 1.5, "geometry.py", "geplant: Bounding-Box,\nnpz-Mesh-Cache", C.unchanged],
    [0, 3.25, "tools/make_variant.py", "Testdaten-Generator\n+ ground_truth.json", C.added],
    [1, 3.25, "analytics.py", "Pandas: Pivots,\nTop-Properties, Filter", C.ink],
    [2, 3.25, "charts.py", "Matplotlib:\ngestapelte Balken", C.ink],
    [3, 3.25, "viewer.py", "geplant: PyVista,\nKontext transparent", C.unchanged],
  ];
  boxes.forEach(([ci, y, label, sub, c]) => {
    const x = col(ci);
    s.addShape(pres.ShapeType.roundRect, { x, y, w: bw, h: bh, fill: { color: c }, line: { color: c }, rectRadius: 0.08 });
    s.addText(label, { x, y: y + 0.1, w: bw, h: 0.4, fontFace: "Courier New", fontSize: 13, bold: true, color: C.white, align: "center", isTextBox: true, margin: 0 });
    s.addText(sub, { x: x + 0.1, y: y + 0.55, w: bw - 0.2, h: 0.75, fontFace: FONT_B, fontSize: 11, color: C.white, align: "center", isTextBox: true, margin: 0 });
  });
  const arrow = (x1, y1, x2, y2) => s.addShape(pres.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color: C.muted, width: 1.5, endArrowType: "triangle" } });
  const midY = 1.5 + bh / 2;
  arrow(col(0) + bw, midY, col(1), midY);           // loader -> diff
  arrow(col(1) + bw, midY, col(2), midY);           // diff -> db
  arrow(col(1) + bw / 2, 1.5 + bh, col(1) + bw / 2, 3.25);   // diff -> analytics
  arrow(col(1) + bw, 3.25 + bh / 2, col(2), 3.25 + bh / 2);  // analytics -> charts
  // make_variant -> loader (nach oben): Pfeilspitze am Anfang, damit Hoehe positiv bleibt
  s.addShape(pres.ShapeType.line, { x: col(0) + bw / 2, y: 1.5 + bh, w: 0, h: 3.25 - (1.5 + bh), line: { color: C.muted, width: 1.5, beginArrowType: "triangle" } });
  // UI als breiter Balken
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 5.0, w: W - 2 * M, h: 0.95, fill: { color: C.dark }, line: { color: C.dark }, rectRadius: 0.08 });
  s.addText("app.py", { x: M + 0.3, y: 5.0, w: 2.2, h: 0.95, fontFace: "Courier New", fontSize: 15, bold: true, color: C.white, valign: "middle", isTextBox: true, margin: 0 });
  s.addText("Streamlit-Hauptkomponente: ruft die Module auf, hält das Ergebnis im Session-State, zeigt Kennzahlen, Tabelle, Details, Diagramme, Historie",
    { x: M + 2.5, y: 5.0, w: W - 2 * M - 2.8, h: 0.95, fontFace: FONT_B, fontSize: 12.5, color: C.line, valign: "middle", isTextBox: true, margin: 0 });
  s.addText("src/config.py: Farben, Toleranzen, Pfade – keine Magic Numbers im Code.   tests/: 20 pytest-Tests, davon 7 gegen die Ground Truth des Generators.",
    { x: M, y: 6.2, w: W - 2 * M, h: 0.5, fontFace: FONT_B, fontSize: 12, color: C.muted, italic: true, isTextBox: true, margin: 0 });
  footer(s, n);
}

// 6 Entwicklungsumgebung ------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Entwicklungsumgebung, Module und Werkzeuge");
  const rows = [
    [{ text: "Bereich", options: { bold: true, color: C.white, fill: { color: C.dark } } }, { text: "Werkzeug", options: { bold: true, color: C.white, fill: { color: C.dark } } }, { text: "Einsatz im Projekt", options: { bold: true, color: C.white, fill: { color: C.dark } } }],
    ["Sprache", "Python 3.13", "einzige Entwicklungssprache; venv «myenv» im Repo-Root"],
    ["Editor", "Visual Studio Code", "Python-Extension, integriertes Terminal, Git-Ansicht"],
    ["Versionskontrolle", "Git + GitHub (public)", "Commit je Etappe, Konvention «[E2] …», Tag v1.0-abgabefaehig"],
    ["IFC", "IfcOpenShell 0.8.5", "Pflicht-Modul: Lesen, Psets, Container, Geometrie, API für Testdaten"],
    ["Daten", "Pandas 3.0", "Vergleichstabelle, Pivots (crosstab), Filter"],
    ["Diagramme", "Matplotlib 3.11", "gestapelte Balken je Geschoss / IfcClass, Top-Properties"],
    ["Datenbank", "SQLite (Standardbibliothek)", "Historie aller Vergleichsläufe, 3 Tabellen"],
    ["UI", "Streamlit 1.64", "Upload, Filter, Tabelle mit Zeilenauswahl, Tabs"],
    ["Tests", "pytest", "20 Tests, Diff-Engine gegen Ground Truth"],
    ["3D (geplant)", "PyVista + stpyvista", "ausserhalb der Modulliste – Abklärung heute"],
  ];
  s.addTable(rows, { x: M, y: 1.45, w: W - 2 * M, colW: [2.2, 3.0, 6.93], fontFace: FONT_B, fontSize: 12.5, color: C.ink,
    border: { type: "solid", color: C.line, pt: 0.5 }, rowH: 0.42, valign: "middle", margin: 0.06 });
  footer(s, n);
}

// 7 Testdaten -----------------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Testdaten: Generator statt Zufall");
  const blocks = [
    ["Problem", "Es gibt keine öffentlichen IFC-Datensätze mit zwei echten Planungsständen. Die buildingSMART-Testdateien liegen nur in verschiedenen Schema-Versionen vor – ein Diff darauf zeigt Schema-Unterschiede, keine Planungsänderungen.", C.deleted],
    ["Lösung", "tools/make_variant.py erzeugt aus Stand A reproduzierbar (Seed) einen Stand B: n Elemente löschen, n verschieben, n umbenennen und Mengenwert ändern, n duplizieren mit neuer GlobalId. Alle gemachten Änderungen landen in ground_truth.json.", C.modified],
    ["Effekt", "Die Diff-Engine ist automatisiert testbar: jede gesetzte Änderung muss gefunden werden, Datei gegen sich selbst muss 0 ergeben. Eigenleistung, die sich beweisen lässt.", C.added],
  ];
  blocks.forEach(([h, t, c], i) => {
    const y = 1.5 + i * 1.6;
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 0.02, w: 0.3, h: 0.3, fill: { color: c }, line: { color: c } });
    s.addText(h, { x: M + 0.45, y: y - 0.05, w: 6, h: 0.4, fontFace: FONT_B, fontSize: 16, bold: true, color: C.dark, isTextBox: true, margin: 0 });
    s.addText(t, { x: M + 0.45, y: y + 0.38, w: 6.6, h: 1.15, fontFace: FONT_B, fontSize: 13, color: C.ink, isTextBox: true, margin: 0, valign: "top" });
  });
  // rechts: Ground-Truth-Ausschnitt
  s.addShape(pres.ShapeType.roundRect, { x: 8.1, y: 1.5, w: 4.6, h: 4.7, fill: { color: C.dark }, line: { color: C.dark }, rectRadius: 0.08 });
  s.addText([
    { text: "ground_truth.json  (Seed 42)", options: { color: C.line, breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: '"deleted":  2', options: { color: C.deleted, bold: true, breakLine: true } },
    { text: '  IfcWall "house - outer wall …"', options: { breakLine: true } },
    { text: '  IfcBuildingElementProxy "origin"', options: { breakLine: true } },
    { text: '"moved":    2', options: { color: C.modified, bold: true, breakLine: true } },
    { text: '  IfcSlab  (2100, 0) → (3100, 500)', options: { breakLine: true } },
    { text: '  IfcChimney  +1000 / +500 mm', options: { breakLine: true } },
    { text: '"modified": 2', options: { color: C.modified, bold: true, breakLine: true } },
    { text: '  Name "… (rev B)"', options: { breakLine: true } },
    { text: '  Qto NetVolume 4.23 → 4.65', options: { breakLine: true } },
    { text: '"added":    2', options: { color: C.added, bold: true, breakLine: true } },
    { text: '  Kopie mit neuer GlobalId', options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "→ Diff-Engine findet  2 / 2 / 4 / 14", options: { color: C.line, bold: true, breakLine: true } },
    { text: "→ A gegen A:  0 / 0 / 0 / 20", options: { color: C.line, bold: true } },
  ], { x: 8.3, y: 1.7, w: 4.2, h: 4.3, fontFace: "Courier New", fontSize: 12, color: C.white, isTextBox: true, margin: 0, valign: "top", paraSpaceAfter: 2 });
  footer(s, n);
}

// 8 Stand heute ---------------------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Stand heute: Kette läuft durchgehend");
  body(s, [
    "Etappen 0–5 des Projektplans abgeschlossen (Setup, Testdaten, Diff-Engine, SQLite, Auswertung, Streamlit-UI).",
    "Benutzbare Version: Dateien wählen → Vergleichen → Kennzahlen, filterbare Tabelle, Detailansicht alt/neu, Diagramme, CSV, Historie.",
    "20 automatisierte Tests grün.",
    "Git-Tag v1.0-abgabefaehig – ab hier ist jede Etappe ein Zusatz, kein Risiko.",
  ], { w: 6.0, h: 2.7, fontSize: 14 });
  // Etappen-Checkliste
  const et = [["E0", "Geruest + Setup", true], ["E1", "Testdaten-Generator", true], ["E2", "Loader + Diff-Engine", true], ["E3", "SQLite-Historie", true],
              ["E4", "Auswertung + Diagramme", true], ["E5", "Streamlit-UI", true], ["E6", "Geometrie + Cache", false], ["E7", "3D-Viewer", false], ["E8", "Report (optional)", false]];
  et.forEach(([k, t, done], i) => {
    const y = 4.3 + i * 0.26;
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 0.04, w: 0.18, h: 0.18, fill: { color: done ? C.added : C.line }, line: { color: done ? C.added : C.line } });
    s.addText(`${k}  ${t}`, { x: M + 0.3, y, w: 5.5, h: 0.26, fontFace: FONT_B, fontSize: 11.5, color: done ? C.ink : C.muted, valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addImage({ path: path.join(PROJ, "output", "chart_class.png"), x: 6.9, y: 1.45, w: 5.85, h: 3.29 });
  // KPI-Zeile
  [[C.added, "2", "hinzugefügt"], [C.deleted, "2", "gelöscht"], [C.modified, "4", "geändert"], [C.unchanged, "14", "unverändert"]].forEach(([c, v, l], i) => {
    const x = 6.9 + i * 1.5;
    s.addShape(pres.ShapeType.roundRect, { x, y: 4.95, w: 1.35, h: 1.25, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.08 });
    s.addText(v, { x, y: 5.0, w: 1.35, h: 0.7, fontFace: FONT_H, fontSize: 30, bold: true, color: c, align: "center", isTextBox: true, margin: 0 });
    s.addText(l, { x, y: 5.7, w: 1.35, h: 0.4, fontFace: FONT_B, fontSize: 11, color: C.muted, align: "center", isTextBox: true, margin: 0 });
  });
  s.addText("Testlauf Building-Architecture.ifc (IFC4, 20 IfcProduct) gegen generierten Stand B", { x: 6.9, y: 6.3, w: 5.85, h: 0.3, fontFace: FONT_B, fontSize: 10, italic: true, color: C.muted, isTextBox: true, margin: 0 });
  footer(s, n);
}

// 9 Herausforderungen -----------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Herausforderungen und Abgrenzungen");
  const cards = [
    [C.modified, "3D-Viewer in Streamlit", "PyVista/stpyvista liegt ausserhalb der Modulliste und ist in Streamlit heikel. Fallback: PyVista im eigenen Fenster, Screenshot in der UI. Abklärung heute."],
    [C.modified, "Geometrie-Performance", "Tessellierung grosser Modelle dauert. Massnahmen: ifcopenshell.geom.iterator mit Threads, npz-Cache je Datei-Hash, «nur Änderungen rendern» ab 20 000 Elementen."],
    [C.deleted, "Bewusste Abgrenzung", "Kein Mesh-Topologie-Vergleich: Geometrie nur über Einfügepunkt, Bounding-Box und Dreiecksanzahl. Nur gleiche IFC-Schemata; sonst Warnung."],
    [C.added, "Testbarkeit gelöst", "Fehlende Zwei-Stände-Testdaten durch eigenen Generator mit Ground Truth ersetzt – Diff-Engine ist beweisbar korrekt."],
    [C.ink, "Code-Stil", "Jede Zeile muss in der MEP erklärbar sein: drei Klassen, Funktionen unter 30 Zeilen, Docstrings, keine cleveren Einzeiler. ifcopenshell.api nur wo nötig, mit Begründung."],
    [C.ink, "Zeitbudget", "Ca. 40–45 h Entwicklung verfügbar. Etappe 5 ist der Abgabe-Meilenstein; Report und Screencast sind erste Streichkandidaten."],
  ];
  cards.forEach(([c, h, t], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    card(s, M + col * 4.1, 1.5 + row * 2.55, 3.93, 2.35, h, t, c);
  });
  footer(s, n);
}

// 10 Naechste Schritte --------------------------------------------------------------------
{
  const s = base(pres.addSlide()); n++;
  title(s, "Nächste Schritte bis ZP2 (14.12.) und MEP");
  const steps = [
    ["SW8–9", "Etappe 6", "Geometrie + npz-Cache; Bounding-Box in die Diff-Engine", C.ink, true],
    ["SW10–11", "Etappe 7", "3D-Viewer: Änderungen opak farbig, Kontext transparent, Filterkopplung", C.modified, true],
    ["SW12", "Etappe 8", "optional: Zeilen-Klick → Kamera-Zoom, PDF-Report", C.unchanged, false],
    ["SW13", "Doku", "README final, Architekturdiagramm, Screenshots, ZP2-Folien", C.ink, true],
    ["14.12.", "ZP2", "fast finaler Prototyp – Etappe 5 steht bereits, Etappe 7 ist das Ziel", C.added, true],
    ["27.01.", "MEP", "Dokumentation (20 %) + Präsentation 10–15 Min + Demo", C.dark, true],
  ];
  // Zeitstrahl: Datum links, Punkt auf der Linie, Text rechts
  const LX = M + 1.5;
  s.addShape(pres.ShapeType.line, { x: LX, y: 1.75, w: 0, h: 4.4, line: { color: C.line, width: 2 } });
  steps.forEach(([when, head, text, c], i) => {
    const y = 1.55 + i * 0.82;
    s.addText(when, { x: M, y, w: 1.25, h: 0.5, fontFace: FONT_B, fontSize: 12, bold: true, color: C.muted, align: "right", valign: "middle", isTextBox: true, margin: 0 });
    s.addShape(pres.ShapeType.ellipse, { x: LX - 0.16, y: y + 0.09, w: 0.32, h: 0.32, fill: { color: c }, line: { color: C.white, width: 1.5 } });
    s.addText(head, { x: LX + 0.45, y, w: 1.6, h: 0.5, fontFace: FONT_B, fontSize: 14, bold: true, color: C.dark, valign: "middle", isTextBox: true, margin: 0 });
    s.addText(text, { x: LX + 2.1, y, w: W - M - LX - 2.1, h: 0.5, fontFace: FONT_B, fontSize: 13, color: C.ink, valign: "middle", isTextBox: true, margin: 0 });
  });
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 6.4, w: W - 2 * M, h: 0.55, fill: { color: C.light }, line: { color: C.light }, rectRadius: 0.08 });
  s.addText("Frage an den Modulverantwortlichen: PyVista/stpyvista als Zusatzmodul für den 3D-Viewer in Ordnung? (IfcOpenShell erfüllt die Pflicht «mindestens ein externes Modul».)",
    { x: M + 0.2, y: 6.4, w: W - 2 * M - 0.4, h: 0.55, fontFace: FONT_B, fontSize: 12, bold: true, color: C.dark, valign: "middle", isTextBox: true, margin: 0 });
  footer(s, n);
}

pres.writeFile({ fileName: OUT }).then(f => console.log("written", f));
