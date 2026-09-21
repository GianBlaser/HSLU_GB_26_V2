"""Auswertung eines Vergleichs mit Pandas (Projektplan Etappe 4).

Alle Funktionen arbeiten auf dem DataFrame aus DiffResult.to_dataframe()
bzw. auf dem DiffResult selbst und liefern wieder DataFrames - so lassen
sich die Ergebnisse direkt in Streamlit zeigen und in charts.py zeichnen.
"""

import pandas as pd

from src.config import ADDED, DELETED, MODIFIED, UNCHANGED
from src.diff_engine import DiffResult

# Reihenfolge der Spalten in Pivots und Diagrammen
CHANGE_ORDER = [ADDED, DELETED, MODIFIED]
# Unbekannte Geschosse (Elemente ohne Container) unter diesem Namen fuehren
NO_STOREY = "(ohne Geschoss)"


def only_changes(df: pd.DataFrame) -> pd.DataFrame:
    """Nur Zeilen mit einer echten Aenderung (kein UNCHANGED)."""
    return df[df["change_type"] != UNCHANGED]


def pivot_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Anzahl Aenderungen je Wert von `column` und je Aenderungsart.

    Ergebnis: Zeilen = Werte der Spalte, Spalten = ADDED/DELETED/MODIFIED,
    plus Spalte "total", absteigend sortiert nach total.
    """
    changes = only_changes(df).copy()
    if column == "storey":
        changes["storey"] = changes["storey"].replace("", NO_STOREY)
    pivot = pd.crosstab(changes[column], changes["change_type"])
    # Fehlende Aenderungsarten als Nullspalten ergaenzen, feste Reihenfolge
    pivot = pivot.reindex(columns=CHANGE_ORDER, fill_value=0)
    pivot["total"] = pivot.sum(axis=1)
    return pivot.sort_values("total", ascending=False)


def changes_by_storey(df: pd.DataFrame) -> pd.DataFrame:
    """Aenderungen je Geschoss."""
    return pivot_by(df, "storey")


def changes_by_class(df: pd.DataFrame) -> pd.DataFrame:
    """Aenderungen je IfcClass."""
    return pivot_by(df, "ifc_class")


def top_changed_properties(result: DiffResult, n: int = 10) -> pd.DataFrame:
    """Die n am haeufigsten geaenderten Attribute/Properties.

    Spalten: source, property, count. Der Pset-Name wird dem Property-Namen
    vorangestellt, damit gleichnamige Properties verschiedener Psets
    getrennt gezaehlt werden.
    """
    rows = []
    for change in result.changes:
        for diff in change.attribute_changes:
            if diff["pset_name"]:
                label = f"{diff['pset_name']}.{diff['property_name']}"
            else:
                label = diff["property_name"]
            rows.append({"source": diff["source"], "property": label})
    if not rows:
        return pd.DataFrame(columns=["source", "property", "count"])
    counts = pd.DataFrame(rows).value_counts().reset_index(name="count")
    return counts.head(n)


def filter_changes(df: pd.DataFrame, ifc_class: str = "", storey: str = "",
                   change_type: str = "") -> pd.DataFrame:
    """Filtert die Tabelle; leerer String bedeutet "kein Filter".

    Wird von der UI fuer Tabelle und Viewer gemeinsam verwendet, damit beide
    immer dieselbe Auswahl zeigen (Projektplan Kap. 11).
    """
    mask = pd.Series(True, index=df.index)
    if ifc_class:
        mask &= df["ifc_class"] == ifc_class
    if storey:
        mask &= df["storey"] == storey
    if change_type:
        mask &= df["change_type"] == change_type
    return df[mask]
