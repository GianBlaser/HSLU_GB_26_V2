"""3D-Darstellung der Aenderungen mit PyVista (Projektplan Etappe 7, Kap. 11).

Geaenderte Elemente werden opak in ihrer Farbe gezeichnet, unveraenderte
als transparenter Kontext (oder nur Kanten, oder gar nicht). DELETED-Elemente
gibt es nur in Stand A, alle anderen kommen aus Stand B.

Gerendert wird offscreen in ein Bild (numpy-Array), das Streamlit mit
st.image anzeigt. Das braucht kein stpyvista und laeuft ueberall.
"""

import numpy as np
import pyvista as pv

from src.config import (ADDED, COLORS, CONTEXT_EDGES, CONTEXT_OFF, DELETED, MODIFIED, OPACITY,
                        UNCHANGED, VIEWER_BACKGROUND, VIEWER_SIZE)
from src.diff_engine import DiffResult
from src.ifc_loader import IfcModel

LEGEND_LABELS = {ADDED: "hinzugefuegt", DELETED: "geloescht", MODIFIED: "geaendert", UNCHANGED: "unveraendert"}


def make_polydata(mesh: dict) -> pv.PolyData:
    """Baut aus verts (n,3) und faces (m,3) ein PyVista-Mesh.

    PyVista erwartet je Dreieck einen Zaehler vorneweg: [3, i, j, k].
    """
    faces = mesh["faces"]
    counts = np.full((len(faces), 1), 3, dtype=np.int32)
    return pv.PolyData(mesh["verts"], np.hstack([counts, faces]).ravel())


def collect_meshes(result: DiffResult, model_a: IfcModel, model_b: IfcModel, guids: set) -> dict:
    """Sammelt je Aenderungsart die Meshes der gewuenschten Elemente.

    DELETED aus Modell A, alles andere aus Modell B. Elemente ohne Geometrie
    werden einzeln uebersprungen.
    """
    grouped = {kind: [] for kind in [ADDED, DELETED, MODIFIED, UNCHANGED]}
    for change in result.changes:
        if change.global_id not in guids:
            continue
        source = model_a if change.change_type == DELETED else model_b
        mesh = source.meshes.get(change.global_id)
        if mesh is not None:
            grouped[change.change_type].append(make_polydata(mesh))
    return grouped


def add_group(plotter: pv.Plotter, meshes: list, change_type: str, context_mode: str) -> None:
    """Fuegt alle Meshes einer Aenderungsart als ein zusammengefasstes Objekt hinzu."""
    if not meshes:
        return
    if change_type == UNCHANGED and context_mode == CONTEXT_OFF:
        return
    # Ein grosses Mesh statt hunderter kleiner: deutlich schneller beim Rendern
    combined = pv.MultiBlock(meshes).combine()
    style = "wireframe" if (change_type == UNCHANGED and context_mode == CONTEXT_EDGES) else "surface"
    opacity = 0.3 if style == "wireframe" else OPACITY[change_type]
    plotter.add_mesh(combined, color=COLORS[change_type], opacity=opacity, style=style,
                     label=LEGEND_LABELS[change_type])


def build_plotter(result: DiffResult, model_a: IfcModel, model_b: IfcModel,
                  guids: set, context_mode: str) -> pv.Plotter:
    """Stellt die Szene zusammen: Farben, Kontext, Legende, isometrische Kamera."""
    plotter = pv.Plotter(off_screen=True, window_size=list(VIEWER_SIZE))
    plotter.set_background(VIEWER_BACKGROUND)
    grouped = collect_meshes(result, model_a, model_b, guids)
    # Kontext zuerst, damit die farbigen Elemente darueber liegen
    for kind in [UNCHANGED, ADDED, DELETED, MODIFIED]:
        add_group(plotter, grouped[kind], kind, context_mode)
    plotter.add_legend(bcolor=None, face=None, size=(0.18, 0.16))
    plotter.view_isometric()
    focus_on_changes(plotter, grouped)
    plotter.add_axes()
    return plotter


def focus_on_changes(plotter: pv.Plotter, grouped: dict) -> None:
    """Kamera auf die geaenderten Elemente richten, nicht auf den ganzen Kontext.

    Sonst bestimmt ein weit entferntes Kontextelement (z.B. ein Geo-Referenz-
    punkt) den Bildausschnitt und die Aenderungen sind winzig.
    """
    changed = grouped[ADDED] + grouped[DELETED] + grouped[MODIFIED]
    if not changed:
        return
    bounds = np.array([mesh.bounds for mesh in changed])
    low = bounds[:, [0, 2, 4]].min(axis=0)
    high = bounds[:, [1, 3, 5]].max(axis=0)
    center = (low + high) / 2
    diagonal = float(np.linalg.norm(high - low))
    # Isometrische Blickrichtung, Abstand proportional zur Groesse der Aenderungen
    direction = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
    plotter.camera.focal_point = center
    plotter.camera.position = center + direction * diagonal * 1.8
    plotter.camera.up = (0, 0, 1)


def render_image(result: DiffResult, model_a: IfcModel, model_b: IfcModel,
                 guids: set, context_mode: str) -> np.ndarray:
    """Rendert die Szene und gibt das Bild als RGB-Array zurueck."""
    plotter = build_plotter(result, model_a, model_b, guids, context_mode)
    image = plotter.screenshot(return_img=True)
    plotter.close()
    return image
