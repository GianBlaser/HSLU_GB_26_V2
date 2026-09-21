"""Diagramme mit Matplotlib (Projektplan Etappe 4).

Jede Funktion gibt eine Figure zurueck; Streamlit zeigt sie mit
st.pyplot(fig), der Report speichert sie mit save_figure().
"""

from pathlib import Path

import matplotlib

# Backend ohne Fenster: laeuft auch unter Streamlit und in Tests
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
import pandas as pd  # noqa: E402

from src.analytics import CHANGE_ORDER  # noqa: E402
from src.config import COLORS  # noqa: E402

FIGURE_SIZE = (8, 4.5)
DPI = 150
LABELS = {"ADDED": "hinzugefuegt", "DELETED": "geloescht", "MODIFIED": "geaendert"}


def plot_stacked_bars(pivot: pd.DataFrame, title: str, xlabel: str) -> plt.Figure:
    """Gestapelte Balken: eine Saeule je Zeile des Pivots, Farben je Aenderungsart."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    bottom = pd.Series(0, index=pivot.index)
    for change_type in CHANGE_ORDER:
        values = pivot[change_type]
        ax.bar(pivot.index, values, bottom=bottom, color=COLORS[change_type],
               label=LABELS[change_type])
        bottom = bottom + values
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Anzahl Elemente")
    # Stueckzahlen: nur ganze Zahlen auf der Achse
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend()
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    return fig


def plot_changes_by_storey(pivot: pd.DataFrame) -> plt.Figure:
    """Aenderungen je Geschoss."""
    return plot_stacked_bars(pivot, "Aenderungen je Geschoss", "Geschoss")


def plot_changes_by_class(pivot: pd.DataFrame) -> plt.Figure:
    """Aenderungen je IfcClass."""
    return plot_stacked_bars(pivot, "Aenderungen je IfcClass", "IfcClass")


def plot_top_properties(top: pd.DataFrame) -> plt.Figure:
    """Horizontale Balken: die am haeufigsten geaenderten Properties."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)
    # Umgekehrt, damit der haeufigste Eintrag oben steht
    top = top.iloc[::-1]
    ax.barh(top["property"], top["count"], color=COLORS["MODIFIED"])
    ax.set_title("Am haeufigsten geaenderte Properties")
    ax.set_xlabel("Anzahl Aenderungen")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig.tight_layout()
    return fig


def save_figure(fig: plt.Figure, path: Path) -> Path:
    """Speichert eine Figure als PNG und schliesst sie (Speicher freigeben)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    return path
