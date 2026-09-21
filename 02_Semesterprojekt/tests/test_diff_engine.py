"""Tests der Diff-Engine gegen die Ground Truth aus tools/make_variant.py.

Aufruf aus dem Repo-Root: pytest 02_Semesterprojekt/tests
"""

import json

import pytest

from src.config import ADDED, DATA_DIR, DELETED, MODIFIED, UNCHANGED
from src.diff_engine import SOURCE_GEOMETRY, compare_models, values_equal
from src.ifc_loader import IfcModel

FILE_A = DATA_DIR / "Building-Architecture.ifc"
FILE_B = DATA_DIR / "Building-Architecture_B.ifc"
TRUTH = DATA_DIR / "Building-Architecture_B_ground_truth.json"


@pytest.fixture(scope="module")
def truth() -> dict:
    """Ground Truth des Generators."""
    with open(TRUTH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def result():
    """Vergleich A gegen B, einmal je Testmodul."""
    return compare_models(IfcModel(FILE_A), IfcModel(FILE_B))


def guids_of(result, change_type: str) -> set:
    """Alle GUIDs einer Aenderungsart."""
    return {c.global_id for c in result.changes if c.change_type == change_type}


def test_self_comparison_has_no_changes():
    """Datei gegen sich selbst: alles UNCHANGED."""
    result = compare_models(IfcModel(FILE_A), IfcModel(FILE_A))
    counts = result.counts()
    assert counts[UNCHANGED] == len(result.changes) > 0
    assert counts[ADDED] == counts[DELETED] == counts[MODIFIED] == 0


def test_deleted(result, truth):
    """Geloeschte Elemente werden als DELETED erkannt."""
    assert guids_of(result, DELETED) == {d["guid"] for d in truth["deleted"]}


def test_added(result, truth):
    """Kopien mit neuer GUID werden als ADDED erkannt."""
    assert guids_of(result, ADDED) == {a["guid"] for a in truth["added"]}


def test_modified_and_moved(result, truth):
    """Umbenannte und verschobene Elemente sind MODIFIED, sonst nichts."""
    expected = {m["guid"] for m in truth["modified"]} | {m["guid"] for m in truth["moved"]}
    assert guids_of(result, MODIFIED) == expected


def test_modified_details(result, truth):
    """Je geaendertes Element werden Name und Mengenwert gefunden."""
    by_guid = {c.global_id: c for c in result.changes}
    for entry in truth["modified"]:
        found = {(d["source"], d["property_name"]) for d in by_guid[entry["guid"]].attribute_changes}
        for change in entry["changes"]:
            assert (change["source"], change["property"]) in found


def test_moved_detected_as_geometry(result, truth):
    """Verschiebung erscheint genau einmal als GEOMETRY-Aenderung."""
    by_guid = {c.global_id: c for c in result.changes}
    for entry in truth["moved"]:
        sources = [d["source"] for d in by_guid[entry["guid"]].attribute_changes]
        assert sources == [SOURCE_GEOMETRY]


def test_dataframe_matches_counts(result):
    """DataFrame und Kennzahlen stimmen ueberein."""
    df = result.to_dataframe()
    assert len(df) == len(result.changes)
    nonzero = {kind: n for kind, n in result.counts().items() if n > 0}
    assert df["change_type"].value_counts().to_dict() == nonzero


def test_values_equal_tolerance():
    """Zahlen mit Toleranz, Strings exakt, bool nicht als Zahl."""
    assert values_equal(1.0, 1.0 + 1e-9)
    assert not values_equal(1.0, 1.1)
    assert values_equal("a", "a")
    assert not values_equal(None, "a")
    assert not values_equal(True, 1.0000001)
