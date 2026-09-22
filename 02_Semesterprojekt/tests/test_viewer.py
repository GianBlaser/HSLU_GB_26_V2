"""Tests fuer viewer.py (offscreen, ohne Fenster)."""

import numpy as np
import pytest

from src import geometry
from src.config import ADDED, CONTEXT_OFF, CONTEXT_TRANSPARENT, DATA_DIR, DELETED, MODIFIED, UNCHANGED, VIEWER_SIZE
from src.diff_engine import compare_models
from src.ifc_loader import IfcModel
from src.viewer import collect_meshes, make_polydata, render_image

FILE_A = DATA_DIR / "Building-Architecture.ifc"
FILE_B = DATA_DIR / "Building-Architecture_B.ifc"


@pytest.fixture(scope="module")
def scene(tmp_path_factory):
    """Modelle mit Geometrie und Vergleich, einmal je Modul."""
    geometry.CACHE_DIR = tmp_path_factory.mktemp("cache")
    model_a, model_b = IfcModel(FILE_A), IfcModel(FILE_B)
    model_a.load_geometry()
    model_b.load_geometry()
    return compare_models(model_a, model_b), model_a, model_b


def test_make_polydata():
    """Ein Dreieck wird zu einem PolyData mit einer Zelle."""
    mesh = {"verts": np.zeros((3, 3), dtype=np.float32), "faces": np.array([[0, 1, 2]], dtype=np.int32)}
    poly = make_polydata(mesh)
    assert poly.n_points == 3
    assert poly.n_cells == 1


def test_collect_meshes_groups(scene):
    """Jede Aenderungsart mit Geometrie hat Meshes; DELETED kommt aus Modell A."""
    result, model_a, model_b = scene
    guids = {c.global_id for c in result.changes}
    grouped = collect_meshes(result, model_a, model_b, guids)
    assert len(grouped[ADDED]) == 2
    assert len(grouped[DELETED]) >= 1
    assert len(grouped[MODIFIED]) >= 1
    assert len(grouped[UNCHANGED]) >= 1
    deleted_guids = [c.global_id for c in result.changes if c.change_type == DELETED]
    assert all(g in model_a.meshes or g not in model_b.meshes for g in deleted_guids)


def test_collect_meshes_respects_filter(scene):
    """Ein leerer Filter liefert keine Meshes."""
    result, model_a, model_b = scene
    grouped = collect_meshes(result, model_a, model_b, set())
    assert all(len(v) == 0 for v in grouped.values())


def test_render_image_size_and_content(scene):
    """Das Bild hat die konfigurierte Groesse und ist nicht leer."""
    result, model_a, model_b = scene
    guids = {c.global_id for c in result.changes}
    image = render_image(result, model_a, model_b, guids, CONTEXT_TRANSPARENT)
    assert image.shape == (VIEWER_SIZE[1], VIEWER_SIZE[0], 3)
    assert image.std() > 0   # nicht einfarbig


def test_context_off_renders_fewer_pixels(scene):
    """Ohne Kontext ist weniger gezeichnet als mit transparentem Kontext."""
    result, model_a, model_b = scene
    guids = {c.global_id for c in result.changes}
    with_context = render_image(result, model_a, model_b, guids, CONTEXT_TRANSPARENT)
    without = render_image(result, model_a, model_b, guids, CONTEXT_OFF)
    background = np.array([255, 255, 255])
    drawn_with = (with_context != background).any(axis=2).sum()
    drawn_without = (without != background).any(axis=2).sum()
    assert drawn_without < drawn_with
