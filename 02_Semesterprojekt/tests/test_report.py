"""Tests fuer report.py und den Kamera-Fokus im Viewer."""

import numpy as np
import pytest

from src import geometry
from src.config import CONTEXT_TRANSPARENT, DATA_DIR
from src.diff_engine import compare_models
from src.ifc_loader import IfcModel
from src.report import write_report
from src.viewer import build_plotter

FILE_A = DATA_DIR / "Building-Architecture.ifc"
FILE_B = DATA_DIR / "Building-Architecture_B.ifc"


@pytest.fixture(scope="module")
def scene(tmp_path_factory):
    """Modelle mit Geometrie und Vergleich."""
    geometry.CACHE_DIR = tmp_path_factory.mktemp("cache")
    model_a, model_b = IfcModel(FILE_A), IfcModel(FILE_B)
    model_a.load_geometry()
    model_b.load_geometry()
    return compare_models(model_a, model_b), model_a, model_b


def pdf_page_count(path) -> int:
    """Seitenzahl eines PDFs (pymupdf nur im Test, nicht im Programm)."""
    pymupdf = pytest.importorskip("pymupdf")
    with pymupdf.open(path) as doc:
        return len(doc)


def test_report_written_with_image(scene, tmp_path):
    """Report mit Bild: Titel + 3 Diagramme + Bild + 1 Tabellenseite = 6 Seiten."""
    result, _, _ = scene
    image = np.zeros((50, 80, 3), dtype=np.uint8)
    path = write_report(result, tmp_path / "sub" / "r.pdf", image)
    assert path.exists() and path.stat().st_size > 10_000
    assert pdf_page_count(path) == 6


def test_report_without_changes_is_short(tmp_path):
    """Datei gegen sich selbst: nur die Titelseite."""
    result = compare_models(IfcModel(FILE_A), IfcModel(FILE_A))
    path = write_report(result, tmp_path / "r.pdf")
    assert pdf_page_count(path) == 1


def test_focus_moves_camera(scene):
    """Mit focus_guid liegt der Kamera-Fokus auf dem Element, sonst auf allen Aenderungen."""
    result, model_a, model_b = scene
    guids = {c.global_id for c in result.changes}
    wall = "0OfZwWc8j9QP5uX8xPTxDH"
    overview = build_plotter(result, model_a, model_b, guids, CONTEXT_TRANSPARENT)
    focused = build_plotter(result, model_a, model_b, guids, CONTEXT_TRANSPARENT, focus_guid=wall)
    bounds = np.array(model_b.meshes[wall]["verts"])
    center = (bounds.min(axis=0) + bounds.max(axis=0)) / 2
    assert np.allclose(focused.camera.focal_point, center, atol=1e-3)
    assert not np.allclose(overview.camera.focal_point, center, atol=1e-3)
    overview.close()
    focused.close()


def test_focus_without_geometry_falls_back(scene):
    """Element ohne Mesh (Kamin): Kamera wie in der Uebersicht."""
    result, model_a, model_b = scene
    guids = {c.global_id for c in result.changes}
    overview = build_plotter(result, model_a, model_b, guids, CONTEXT_TRANSPARENT)
    focused = build_plotter(result, model_a, model_b, guids, CONTEXT_TRANSPARENT, focus_guid="3Fbgsvr8nAYfGs9y5keub0")
    assert np.allclose(overview.camera.focal_point, focused.camera.focal_point)
    overview.close()
    focused.close()
