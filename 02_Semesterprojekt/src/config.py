"""Zentrale Konfiguration des IFC-Diff Viewers.

Alle Farben, Toleranzen, Pfade und Attributlisten liegen hier, damit im
restlichen Code keine "Magic Numbers" vorkommen (Projektplan Kap. 7, Punkt 5).
"""

from pathlib import Path

# --- Pfade -------------------------------------------------------------------
# PROJECT_DIR ist der Ordner 02_Semesterprojekt/, unabhaengig davon, von wo
# das Programm gestartet wird.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
CACHE_DIR = PROJECT_DIR / "cache"
OUTPUT_DIR = PROJECT_DIR / "output"
DB_PATH = OUTPUT_DIR / "ifc_diff.db"

# --- Aenderungsarten ---------------------------------------------------------
ADDED = "ADDED"
DELETED = "DELETED"
MODIFIED = "MODIFIED"
UNCHANGED = "UNCHANGED"
CHANGE_TYPES = [ADDED, DELETED, MODIFIED, UNCHANGED]

# --- Farben und Opazitaeten fuer den 3D-Viewer (Projektplan Kap. 11) ---------
COLORS = {
    ADDED: "#2E9E5B",      # Gruen
    DELETED: "#D1434A",    # Rot
    MODIFIED: "#E08A1E",   # Orange
    UNCHANGED: "#9AA0A6",  # Grau
}
OPACITY = {
    ADDED: 1.0,
    DELETED: 1.0,
    MODIFIED: 1.0,
    UNCHANGED: 0.07,
}

# --- Toleranzen fuer den Vergleich (Projektplan Kap. 10) ---------------------
# Laengen in Metern: 1 mm
LENGTH_TOLERANCE = 0.001
# Allgemeine Zahlenwerte in Property Sets
NUMBER_TOLERANCE = 1e-6

# --- Attribute ---------------------------------------------------------------
# Direkte Attribute, die je Element verglichen werden
COMPARED_ATTRIBUTES = ["Name", "Description", "ObjectType", "Tag", "PredefinedType"]

# Attribute, die bewusst nicht verglichen werden (aendern sich bei jedem
# Export, sagen aber nichts ueber die Planung aus)
EXCLUDED_ATTRIBUTES = ["GlobalId", "OwnerHistory", "id"]

# --- Performance -------------------------------------------------------------
# Ab dieser Elementanzahl warnt die UI und bietet "nur Aenderungen rendern" an
MAX_ELEMENTS_FULL_RENDER = 20_000
