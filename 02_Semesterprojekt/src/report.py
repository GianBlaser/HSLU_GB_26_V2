"""PDF-Report eines Vergleichs (Projektplan Etappe 8).

Erzeugt mit matplotlib PdfPages - kein zusaetzliches Modul. Seiten:
1. Titel mit Kennzahlen und Dateien
2. Diagramme (je Geschoss, je IfcClass, Top-Properties)
3. 3D-Ansicht (falls ein Bild uebergeben wird)
4+. Tabelle der Aenderungen, seitenweise
"""

from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from src.analytics import changes_by_class, changes_by_storey, only_changes, top_changed_properties
from src.charts import plot_changes_by_class, plot_changes_by_storey, plot_top_properties
from src.config import ADDED, COLORS, DELETED, MODIFIED, UNCHANGED
from src.diff_engine import DiffResult

PAGE_SIZE = (8.27, 11.69)     # A4 hoch in Zoll
ROWS_PER_PAGE = 35
TABLE_COLUMNS = ["change_type", "ifc_class", "name", "storey", "n_attr_changes"]
TABLE_HEADERS = ["Art", "IfcClass", "Name", "Geschoss", "Attr."]


def title_page(pdf: PdfPages, result: DiffResult) -> None:
    """Seite 1: Titel, Dateien, Kennzahlen als farbige Kacheln."""
    fig = plt.figure(figsize=PAGE_SIZE)
    fig.text(0.08, 0.92, "IFC-Diff Report", fontsize=26, weight="bold")
    fig.text(0.08, 0.885, datetime.now().strftime("%d.%m.%Y %H:%M"), fontsize=10, color="gray")
    lines = [
        f"Stand A (alt):  {result.file_a}   [{result.schema_a}]",
        f"Stand B (neu):  {result.file_b}   [{result.schema_b}]",
        f"Elemente total: {len(result.changes)}     Dauer: {result.duration_s:.2f} s",
    ]
    for i, line in enumerate(lines):
        fig.text(0.08, 0.83 - i * 0.03, line, fontsize=11, family="monospace")
    if result.schema_differs():
        fig.text(0.08, 0.73, "Achtung: verschiedene IFC-Schemata - Vergleich unsicher", fontsize=11, color="red")

    counts = result.counts()
    labels = {ADDED: "hinzugefuegt", DELETED: "geloescht", MODIFIED: "geaendert", UNCHANGED: "unveraendert"}
    for i, kind in enumerate([ADDED, DELETED, MODIFIED, UNCHANGED]):
        ax = fig.add_axes([0.08 + i * 0.22, 0.55, 0.19, 0.12])
        ax.set_facecolor(COLORS[kind])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(0.5, 0.6, str(counts[kind]), ha="center", va="center", fontsize=28, color="white", weight="bold")
        ax.text(0.5, 0.2, labels[kind], ha="center", va="center", fontsize=10, color="white")

    fig.text(0.08, 0.45, "Vergleichsebenen: Direktattribute, Property Sets (Toleranz 1e-6),\n"
             "Geometrie: Einfuegepunkt, Bounding-Box (1 mm), Dreiecksanzahl.\n"
             "Kein Mesh-Topologie-Vergleich (bewusste Abgrenzung).", fontsize=10, va="top")
    pdf.savefig(fig)
    plt.close(fig)


def chart_pages(pdf: PdfPages, result: DiffResult, df: pd.DataFrame) -> None:
    """Seite 2: die drei Diagramme untereinander."""
    if result.count(UNCHANGED) == len(result.changes):
        return
    for fig in [plot_changes_by_storey(changes_by_storey(df)),
                plot_changes_by_class(changes_by_class(df)),
                plot_top_properties(top_changed_properties(result))]:
        fig.set_size_inches(PAGE_SIZE[0], PAGE_SIZE[1] / 2.6)
        pdf.savefig(fig)
        plt.close(fig)


def image_page(pdf: PdfPages, image: np.ndarray) -> None:
    """Seite 3: das 3D-Bild des Viewers."""
    fig = plt.figure(figsize=PAGE_SIZE)
    ax = fig.add_axes([0.05, 0.3, 0.9, 0.55])
    ax.imshow(image)
    ax.axis("off")
    fig.text(0.08, 0.9, "3D-Ansicht der Aenderungen", fontsize=16, weight="bold")
    pdf.savefig(fig)
    plt.close(fig)


def table_pages(pdf: PdfPages, df: pd.DataFrame) -> None:
    """Seiten 4+: Tabelle der Aenderungen, ROWS_PER_PAGE Zeilen je Seite."""
    changes = only_changes(df).sort_values(["change_type", "ifc_class", "name"])
    if changes.empty:
        return
    n_pages = int(np.ceil(len(changes) / ROWS_PER_PAGE))
    for page in range(n_pages):
        chunk = changes.iloc[page * ROWS_PER_PAGE:(page + 1) * ROWS_PER_PAGE]
        fig = plt.figure(figsize=PAGE_SIZE)
        fig.text(0.08, 0.94, f"Aenderungen ({page + 1}/{n_pages})", fontsize=16, weight="bold")
        ax = fig.add_axes([0.05, 0.05, 0.9, 0.86])
        ax.axis("off")
        table = ax.table(cellText=chunk[TABLE_COLUMNS].values, colLabels=TABLE_HEADERS,
                         loc="upper center", cellLoc="left",
                         colWidths=[0.13, 0.25, 0.37, 0.17, 0.08])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.3)
        # Erste Spalte in der Farbe der Aenderungsart
        for row, kind in enumerate(chunk["change_type"], start=1):
            table[row, 0].set_facecolor(COLORS[kind])
            table[row, 0].get_text().set_color("white")
        pdf.savefig(fig)
        plt.close(fig)


def write_report(result: DiffResult, path: Path, image: np.ndarray = None) -> Path:
    """Schreibt den kompletten Report als PDF und gibt den Pfad zurueck."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = result.to_dataframe()
    with PdfPages(path) as pdf:
        title_page(pdf, result)
        chart_pages(pdf, result, df)
        if image is not None:
            image_page(pdf, image)
        table_pages(pdf, df)
    return path
