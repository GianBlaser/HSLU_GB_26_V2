"""Tests fuer geometry.py und die Geometrie-Ebene der Diff-Engine."""

import json
import time

import pytest

from src import geometry
from src.config import DATA_DIR
from src.diff_engine import SOURCE_GEOMETRY, compare_models
from src.ifc_loader import IfcModel

FILE_A = DATA_DIR / "Building-Architecture.ifc"
FILE_B = DATA_DIR / "Building-Architecture_B.ifc"
TRUTH = DATA_DIR / "Building-Architecture_B_ground_truth.json"


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    """Cache in einen temporaeren Ordner umleiten, damit Tests sich nicht beeinflussen."""
    monkeypatch.setattr(geometry, "CACHE_DIR", tmp_path)
    return tmp_path


def test_meshes_created_for_elements_with_geometry(cache_dir):
    """Alle Elemente mit Representation bekommen ein Mesh, die anderen nicht."""
    model = IfcModel(FILE_A)
    n = model.load_geometry()
    with_geometry = [g for g, e in model.elements.items() if e.Representation is not None]
    assert n == len(with_geometry)
    assert model.get_geometry_summary("1Ano2ZUxnEIvVQ_beukl8b") == {}   # Geschoss ohne Geometrie


def test_summary_is_plausible(cache_dir):
    """Bounding-Box in Metern, positive Abmessungen, Dreiecke vorhanden."""
    model = IfcModel(FILE_A)
    model.load_geometry()
    summary = model.get_geometry_summary("3zR0BOEcLADRKln4HYporH")   # Bodenplatte
    assert summary["n_triangles"] > 0
    assert all(s > 0 for s in summary["size"])
    assert all(s < 100 for s in summary["size"])   # Meter, nicht Millimeter


def test_cache_written_and_reused(cache_dir):
    """Erster Lauf schreibt npz, zweiter Lauf liest sie und ist schneller."""
    model = IfcModel(FILE_A)
    t0 = time.perf_counter()
    first = model.load_geometry()
    t_first = time.perf_counter() - t0
    assert geometry.cache_path(FILE_A).exists()

    t0 = time.perf_counter()
    second = IfcModel(FILE_A).load_geometry()
    t_second = time.perf_counter() - t0
    assert first == second
    assert t_second < t_first


def test_cache_roundtrip_identical(cache_dir):
    """Aus dem Cache geladene Meshes sind identisch mit den erzeugten."""
    model = IfcModel(FILE_A)
    created = geometry.create_meshes(model.file)
    geometry.save_cache(created, cache_dir / "x.npz")
    loaded = geometry.load_cache(cache_dir / "x.npz")
    assert set(created) == set(loaded)
    for guid in created:
        assert (created[guid]["verts"] == loaded[guid]["verts"]).all()
        assert (created[guid]["faces"] == loaded[guid]["faces"]).all()


def test_moved_elements_detected_by_bounding_box(cache_dir):
    """Mit Geometrie werden verschobene Elemente auch ueber center erkannt."""
    with open(TRUTH, encoding="utf-8") as fh:
        truth = json.load(fh)
    model_a, model_b = IfcModel(FILE_A), IfcModel(FILE_B)
    model_a.load_geometry()
    model_b.load_geometry()
    by_guid = {c.global_id: c for c in compare_models(model_a, model_b).changes}
    for entry in truth["moved"]:
        change = by_guid[entry["guid"]]
        if not model_b.get_geometry_summary(entry["guid"]):
            continue   # Element ohne eigene Geometrie (z.B. Kamin ohne Representation)
        names = {d["property_name"] for d in change.attribute_changes if d["source"] == SOURCE_GEOMETRY}
        assert "Placement" in names
        assert "center" in names
        assert "size" not in names   # verschoben, nicht skaliert


def test_self_comparison_with_geometry_unchanged(cache_dir):
    """Datei gegen sich selbst bleibt auch mit Geometrie ohne Aenderungen."""
    model_a, model_b = IfcModel(FILE_A), IfcModel(FILE_A)
    model_a.load_geometry()
    model_b.load_geometry()
    result = compare_models(model_a, model_b)
    assert result.count("UNCHANGED") == len(result.changes)
