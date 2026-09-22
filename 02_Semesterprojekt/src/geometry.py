"""Geometrie-Erzeugung mit Cache (Projektplan Etappe 6, Kap. 11).

Die Meshes aller Elemente werden einmal mit ifcopenshell.geom erzeugt und als
.npz unter cache/<sha1 der Datei>.npz abgelegt. Der zweite Ladevorgang liest
nur noch die npz-Datei. Koordinaten sind in Metern (ifcopenshell rechnet die
Modelleinheiten um) und in Weltkoordinaten (USE_WORLD_COORDS).
"""

import hashlib
import multiprocessing
from pathlib import Path

import ifcopenshell
import ifcopenshell.geom
import numpy as np

from src.config import CACHE_DIR


def file_hash(path: Path) -> str:
    """SHA1 des Dateiinhalts - identische Datei = identischer Cache."""
    sha1 = hashlib.sha1()
    with open(path, "rb") as fh:
        sha1.update(fh.read())
    return sha1.hexdigest()


def cache_path(path: Path) -> Path:
    """Pfad der npz-Datei fuer eine IFC-Datei."""
    return CACHE_DIR / f"{file_hash(path)}.npz"


def create_meshes(ifc_file: ifcopenshell.file) -> dict:
    """Erzeugt alle Meshes: {guid: {"verts": (n,3), "faces": (m,3)}}.

    Der Iterator laeuft mit mehreren Threads. Elemente ohne Geometrie
    liefert er gar nicht erst; fehlerhafte Elemente ueberspringt er einzeln.
    """
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())

    meshes = {}
    if not iterator.initialize():
        return meshes
    while True:
        shape = iterator.get()
        verts = np.array(shape.geometry.verts, dtype=np.float32).reshape(-1, 3)
        faces = np.array(shape.geometry.faces, dtype=np.int32).reshape(-1, 3)
        meshes[shape.guid] = {"verts": verts, "faces": faces}
        if not iterator.next():
            break
    return meshes


def save_cache(meshes: dict, path: Path) -> None:
    """Schreibt alle Meshes in eine npz-Datei (Schluessel "guid|verts" / "guid|faces").

    "|" kommt im IFC-GUID-Alphabet (A-Z, a-z, 0-9, _, $) nicht vor.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {}
    for guid, mesh in meshes.items():
        arrays[f"{guid}|verts"] = mesh["verts"]
        arrays[f"{guid}|faces"] = mesh["faces"]
    np.savez_compressed(path, **arrays)


def load_cache(path: Path) -> dict:
    """Liest Meshes aus einer npz-Datei zurueck."""
    meshes = {}
    with np.load(path) as data:
        for key in data.files:
            guid, kind = key.split("|")
            meshes.setdefault(guid, {})[kind] = data[key]
    return meshes


def load_meshes(ifc_path: Path, ifc_file: ifcopenshell.file) -> dict:
    """Meshes einer Datei - aus dem Cache, sonst erzeugen und cachen."""
    ifc_path = Path(ifc_path)
    npz = cache_path(ifc_path)
    if npz.exists():
        return load_cache(npz)
    meshes = create_meshes(ifc_file)
    save_cache(meshes, npz)
    return meshes


def mesh_summary(mesh: dict) -> dict:
    """Vergleichbare Kennwerte eines Meshes (Projektplan Kap. 10, Ebene 3).

    center: Schwerpunkt der Bounding-Box, size: Abmessungen, n_triangles.
    Kein Mesh-Topologie-Vergleich - bewusste Abgrenzung.
    """
    verts = mesh["verts"]
    low = verts.min(axis=0)
    high = verts.max(axis=0)
    return {
        "center": tuple(float(v) for v in (low + high) / 2),
        "size": tuple(float(v) for v in high - low),
        "n_triangles": int(len(mesh["faces"])),
    }
