"""Tests fuer analytics.py und charts.py."""

import pytest

from src.analytics import (changes_by_class, changes_by_storey, filter_changes,
                           top_changed_properties)
from src.charts import plot_changes_by_storey, plot_top_properties, save_figure
from src.config import ADDED, DATA_DIR, DELETED, MODIFIED
from src.diff_engine import compare_models
from src.ifc_loader import IfcModel

FILE_A = DATA_DIR / "Building-Architecture.ifc"
FILE_B = DATA_DIR / "Building-Architecture_B.ifc"


@pytest.fixture(scope="module")
def result():
    """Vergleich A gegen B."""
    return compare_models(IfcModel(FILE_A), IfcModel(FILE_B))


@pytest.fixture(scope="module")
def df(result):
    """Tabelle des Vergleichs."""
    return result.to_dataframe()


def test_pivot_totals_match_counts(df, result):
    """Summe je Aenderungsart im Pivot = Kennzahlen des Vergleichs."""
    for pivot in [changes_by_storey(df), changes_by_class(df)]:
        counts = result.counts()
        assert pivot[ADDED].sum() == counts[ADDED]
        assert pivot[DELETED].sum() == counts[DELETED]
        assert pivot[MODIFIED].sum() == counts[MODIFIED]
        assert (pivot["total"] == pivot[[ADDED, DELETED, MODIFIED]].sum(axis=1)).all()


def test_pivot_sorted_descending(df):
    """Pivot ist nach total absteigend sortiert."""
    totals = list(changes_by_class(df)["total"])
    assert totals == sorted(totals, reverse=True)


def test_top_properties(result):
    """Name und NetVolume je 2x, Placement 2x - Reihenfolge nach Haeufigkeit."""
    top = top_changed_properties(result)
    counts = dict(zip(top["property"], top["count"]))
    assert counts["Name"] == 2
    assert counts["Qto_WallBaseQuantities.NetVolume"] == 2
    assert counts["Placement"] == 2
    assert list(top["count"]) == sorted(top["count"], reverse=True)


def test_top_properties_empty_when_no_changes():
    """Datei gegen sich selbst: leere Tabelle mit den erwarteten Spalten."""
    result = compare_models(IfcModel(FILE_A), IfcModel(FILE_A))
    top = top_changed_properties(result)
    assert len(top) == 0
    assert list(top.columns) == ["source", "property", "count"]


def test_filter_changes(df):
    """Filter wirken einzeln und kombiniert; leer = kein Filter."""
    assert len(filter_changes(df)) == len(df)
    walls = filter_changes(df, ifc_class="IfcWall")
    assert (walls["ifc_class"] == "IfcWall").all()
    modified_walls = filter_changes(df, ifc_class="IfcWall", change_type=MODIFIED)
    assert len(modified_walls) == 2


def test_charts_render_and_save(df, result, tmp_path):
    """Diagramme lassen sich erzeugen und als PNG speichern."""
    path_1 = save_figure(plot_changes_by_storey(changes_by_storey(df)), tmp_path / "storey.png")
    path_2 = save_figure(plot_top_properties(top_changed_properties(result)), tmp_path / "top.png")
    assert path_1.stat().st_size > 1000
    assert path_2.stat().st_size > 1000
