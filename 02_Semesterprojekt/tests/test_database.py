"""Tests der SQLite-Speicherung: zwei Laeufe speichern und wieder auslesen."""

import pytest

from src.config import DATA_DIR, MODIFIED
from src.database import connect, load_attribute_changes, load_changes, load_history, save_result
from src.diff_engine import compare_models
from src.ifc_loader import IfcModel

FILE_A = DATA_DIR / "Building-Architecture.ifc"
FILE_B = DATA_DIR / "Building-Architecture_B.ifc"


@pytest.fixture(scope="module")
def result():
    """Vergleich A gegen B."""
    return compare_models(IfcModel(FILE_A), IfcModel(FILE_B))


@pytest.fixture
def conn(tmp_path):
    """Frische Datenbank in einem temporaeren Ordner."""
    connection = connect(tmp_path / "sub" / "test.db")
    yield connection
    connection.close()


def test_two_runs_in_history(conn, result):
    """Zwei gespeicherte Laeufe erscheinen in der Historie, neuester zuerst."""
    id_1 = save_result(conn, result)
    id_2 = save_result(conn, result)
    history = load_history(conn)
    assert list(history["id"]) == [id_2, id_1]
    assert history.iloc[0]["file_b"] == "Building-Architecture_B.ifc"


def test_counts_saved(conn, result):
    """Kennzahlen in comparison entsprechen dem DiffResult."""
    comparison_id = save_result(conn, result)
    row = load_history(conn).set_index("id").loc[comparison_id]
    counts = result.counts()
    assert row["n_added"] == counts["ADDED"]
    assert row["n_deleted"] == counts["DELETED"]
    assert row["n_modified"] == counts["MODIFIED"]
    assert row["n_unchanged"] == counts["UNCHANGED"]


def test_changes_roundtrip(conn, result):
    """Alle Elemente eines Laufs kommen mit Aenderungsart zurueck."""
    comparison_id = save_result(conn, result)
    changes = load_changes(conn, comparison_id)
    assert len(changes) == len(result.changes)
    assert changes["change_type"].value_counts().to_dict() == {
        kind: n for kind, n in result.counts().items() if n > 0
    }


def test_attribute_changes_roundtrip(conn, result):
    """Attributaenderungen eines MODIFIED-Elements sind vollstaendig gespeichert."""
    comparison_id = save_result(conn, result)
    changes = load_changes(conn, comparison_id)
    modified = changes[changes["change_type"] == MODIFIED]
    for _, row in modified.iterrows():
        details = load_attribute_changes(conn, row["id"])
        assert len(details) == row["n_attr_changes"] > 0
        assert details["property_name"].notna().all()


def test_runs_are_isolated(conn, result):
    """Aenderungen des einen Laufs tauchen nicht im anderen auf."""
    id_1 = save_result(conn, result)
    id_2 = save_result(conn, result)
    assert set(load_changes(conn, id_1)["id"]).isdisjoint(load_changes(conn, id_2)["id"])


def test_ids_from_dataframe_work(conn, result):
    """IDs direkt aus dem DataFrame (numpy.int64) muessen als Parameter funktionieren."""
    comparison_id = save_result(conn, result)
    history_id = load_history(conn)["id"].iloc[0]
    changes = load_changes(conn, history_id)
    first_modified = changes[changes["change_type"] == MODIFIED].iloc[0]
    assert len(load_attribute_changes(conn, first_modified["id"])) == first_modified["n_attr_changes"]
