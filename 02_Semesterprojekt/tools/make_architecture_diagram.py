"""Erzeugt das Architekturdiagramm fuer die Dokumentation.

Aufruf aus dem Repo-Root mit aktivierter venv:
    python 02_Semesterprojekt/tools/make_architecture_diagram.py

Schreibt docs/architektur.png. Mit Matplotlib gezeichnet, damit das Bild
jederzeit reproduzierbar ist und keine externe Zeichensoftware braucht.
"""

import sys
from pathlib import Path

import matplotlib

# Projektordner importierbar machen (das Skript liegt in tools/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from src.config import ADDED, COLORS, MODIFIED, PROJECT_DIR  # noqa: E402

DARK = "#1F2933"
INK = "#323F4B"
MUTED = "#7B8794"

# (x, y, Breite, Hoehe, Titel, Beschreibung, Farbe)
BOXES = [
    (0.5, 6.2, 3.0, 1.1, "tools/make_variant.py", "Testdaten-Generator\n+ ground_truth.json", COLORS[ADDED]),
    (0.5, 4.5, 3.0, 1.1, "src/ifc_loader.py", "Klasse IfcModel:\nGUID-Dict, Psets, Geschoss", INK),
    (4.0, 4.5, 3.0, 1.1, "src/geometry.py", "Meshes + npz-Cache,\nBounding-Box-Kennwerte", INK),
    (4.0, 2.8, 3.0, 1.1, "src/diff_engine.py", "ElementChange, DiffResult\ncompare_models()", COLORS[MODIFIED]),
    (7.5, 2.8, 3.0, 1.1, "src/database.py", "SQLite: comparison,\nelement_change, attribute_change", INK),
    (0.5, 1.1, 3.0, 1.1, "src/analytics.py", "Pandas: Pivots,\nTop-Properties, Filter", INK),
    (4.0, 1.1, 3.0, 1.1, "src/charts.py", "Matplotlib:\ngestapelte Balken", INK),
    (7.5, 1.1, 3.0, 1.1, "src/viewer.py", "PyVista offscreen:\nFarben, Kontext, Kamera", INK),
    (7.5, 4.5, 3.0, 1.1, "src/report.py", "PDF: KPIs, Diagramme,\n3D-Bild, Tabelle", INK),
]
# (von, nach) als Indizes in BOXES
ARROWS = [(0, 1), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (5, 6), (3, 7), (6, 8), (7, 8)]


def box_center(box: tuple) -> tuple:
    """Mittelpunkt einer Box."""
    x, y, w, h = box[:4]
    return x + w / 2, y + h / 2


def anchor(box_from: tuple, box_to: tuple) -> tuple:
    """Startpunkt am Rand von box_from in Richtung box_to.

    Waagrecht, wenn die Boxen auf derselben Hoehe liegen, sonst senkrecht -
    so treffen die Pfeile die Kanten und nicht die Beschriftung.
    """
    x1, y1, w1, h1 = box_from[:4]
    x2, y2 = box_center(box_to)
    cx, cy = box_center(box_from)
    if abs(y2 - cy) < h1:
        return (x1 + w1 if x2 > cx else x1, cy)
    return (cx, y1 if y2 < cy else y1 + h1)


def draw_box(ax, box: tuple) -> None:
    """Zeichnet eine Box mit Titel und Beschreibung."""
    x, y, w, h, title, text, color = box
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                facecolor=color, edgecolor="none"))
    ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="center", color="white",
            fontsize=11, family="monospace", weight="bold")
    ax.text(x + w / 2, y + 0.33, text, ha="center", va="center", color="white", fontsize=8.5)


def draw_arrow(ax, box_from: tuple, box_to: tuple) -> None:
    """Zeichnet einen Pfeil von Rand zu Rand zwischen zwei Boxen."""
    ax.add_patch(FancyArrowPatch(anchor(box_from, box_to), anchor(box_to, box_from),
                                 arrowstyle="-|>", mutation_scale=14, color=MUTED, linewidth=1.3))


def draw_app_bar(ax) -> None:
    """Zeichnet app.py als breiten Balken am unteren Rand."""
    ax.add_patch(FancyBboxPatch((0.5, 0.1), 10.0, 0.8, boxstyle="round,pad=0.02,rounding_size=0.12",
                                facecolor=DARK, edgecolor="none"))
    ax.text(1.0, 0.5, "app.py", ha="left", va="center", color="white", fontsize=12,
            family="monospace", weight="bold")
    ax.text(2.5, 0.5, "Streamlit-Hauptkomponente: Auswahl/Upload, Vergleich, Kennzahlen, Tabelle mit\n"
            "Detailansicht, 3D-Ansicht, Diagramme, CSV- und PDF-Export, Historie",
            ha="left", va="center", color="white", fontsize=8.5)


def main() -> None:
    """Zeichnet das Diagramm und speichert es als PNG."""
    fig, ax = plt.subplots(figsize=(11, 8.4))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 8.4)
    ax.axis("off")

    ax.text(0.5, 8.0, "IFC-Diff Viewer - Architektur", fontsize=19, weight="bold", color=DARK)
    ax.text(0.5, 7.65, "Pfeile = Datenfluss. app.py (Streamlit) ruft alle Module auf.",
            fontsize=10, color=MUTED)

    for index_from, index_to in ARROWS:
        draw_arrow(ax, BOXES[index_from], BOXES[index_to])
    for box in BOXES:
        draw_box(ax, box)

    draw_app_bar(ax)

    ax.text(0.5, 7.4, "src/config.py: Farben, Toleranzen, Pfade   |   tests/: 35 pytest-Tests",
            fontsize=9, color=MUTED, style="italic")

    path = PROJECT_DIR / "docs" / "architektur.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"geschrieben: {path}")


if __name__ == "__main__":
    main()
