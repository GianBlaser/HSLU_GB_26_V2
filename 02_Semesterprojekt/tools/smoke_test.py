"""Smoke-Test Etappe 0: IFC oeffnen und Grunddaten ausgeben.

Aufruf aus dem Repo-Root mit aktivierter venv:
    python 02_Semesterprojekt/tools/smoke_test.py
"""

import sys
from pathlib import Path

import ifcopenshell

# Projektordner importierbar machen (das Skript liegt in tools/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIR  # noqa: E402


def main():
    """Oeffnet die Test-IFC und gibt Schema, Elementanzahl und Top-5-Klassen aus."""
    path = DATA_DIR / "Building-Architecture.ifc"
    model = ifcopenshell.open(str(path))
    products = model.by_type("IfcProduct")

    print("Datei:  ", path.name)
    print("Schema: ", model.schema)
    print("IfcProduct total:", len(products))

    # Haeufigkeit je IfcClass zaehlen
    counts = {}
    for product in products:
        ifc_class = product.is_a()
        counts[ifc_class] = counts.get(ifc_class, 0) + 1

    print("Top 5 IfcClasses:")
    for ifc_class, n in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5]:
        print(f"  {ifc_class:<25} {n}")


if __name__ == "__main__":
    main()
