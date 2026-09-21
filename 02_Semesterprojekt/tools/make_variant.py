"""Testdaten-Generator: erzeugt aus einer IFC-Datei einen "Stand B".

Aus Stand A werden kontrolliert Aenderungen gemacht (loeschen, verschieben,
Attribute/Mengen aendern, duplizieren). Die tatsaechlich gemachten Aenderungen
werden in einer ground_truth.json festgehalten, damit die Diff-Engine in
Etappe 2 automatisiert getestet werden kann (Projektplan Kap. 8).

Aufruf aus dem Repo-Root mit aktivierter venv:
    python 02_Semesterprojekt/tools/make_variant.py data/Building-Architecture.ifc
    python 02_Semesterprojekt/tools/make_variant.py data/Building-Architecture.ifc --n-delete 3 --seed 7

Fuer Loeschen und Kopieren wird ifcopenshell.api verwendet, weil ein blosses
file.remove() Verweise (z.B. in IfcRelContainedInSpatialStructure) haengen
lassen und die Datei unbrauchbar machen wuerde.
"""

import argparse
import json
import random
from pathlib import Path

import ifcopenshell
import ifcopenshell.api

# Offset in Modelleinheiten (die Testdaten sind in mm), deutlich sichtbar
MOVE_OFFSET = (1000.0, 500.0, 0.0)
# Kopien werden versetzt, damit sie nicht exakt auf dem Original liegen
COPY_OFFSET = (3000.0, 0.0, 0.0)
# Faktor, mit dem eine Mengenangabe (Qto) veraendert wird
QUANTITY_FACTOR = 1.1


def pick_candidates(model: ifcopenshell.file) -> list:
    """Gibt alle Bauteile (IfcElement) zurueck, sortiert nach GlobalId.

    Nur IfcElement, keine Raeume/Geschosse: Bauteile haben Geometrie und
    sind das, was in der Praxis geaendert wird. Sortiert, damit derselbe
    Seed immer dieselbe Auswahl liefert.
    """
    elements = model.by_type("IfcElement")
    return sorted(elements, key=lambda e: e.GlobalId)


def move_element(element, offset: tuple) -> dict:
    """Verschiebt ein Element um offset (neuer IfcCartesianPoint)."""
    placement = element.ObjectPlacement.RelativePlacement
    old = placement.Location.Coordinates
    new = (old[0] + offset[0], old[1] + offset[1], old[2] + offset[2])
    # Neuer Punkt statt Aenderung des alten: der alte koennte geteilt sein
    placement.Location = element.file.createIfcCartesianPoint(new)
    return {"guid": element.GlobalId, "name": element.Name,
            "from": list(old), "to": list(new)}


def modify_element(element) -> dict:
    """Aendert den Namen und, falls vorhanden, die erste Mengenangabe."""
    changes = []
    old_name = element.Name
    element.Name = f"{old_name} (rev B)"
    changes.append({"source": "ATTRIBUTE", "property": "Name",
                    "old": old_name, "new": element.Name})

    quantity = find_first_quantity(element)
    if quantity is not None:
        # IfcQuantityLength hat LengthValue, IfcQuantityVolume VolumeValue usw.
        # Das erste Attribut mit float-Wert ist immer der Messwert.
        for attr_name in quantity.wrapped_data.get_attribute_names():
            value = getattr(quantity, attr_name)
            if isinstance(value, float):
                setattr(quantity, attr_name, value * QUANTITY_FACTOR)
                changes.append({"source": "PSET", "property": quantity.Name,
                                "old": value, "new": getattr(quantity, attr_name)})
                break
    return {"guid": element.GlobalId, "changes": changes}


def find_first_quantity(element):
    """Sucht die erste Mengenangabe (IfcPhysicalQuantity) eines Elements."""
    for rel in element.IsDefinedBy:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        definition = rel.RelatingPropertyDefinition
        if definition.is_a("IfcElementQuantity") and definition.Quantities:
            return definition.Quantities[0]
    return None


def duplicate_element(model: ifcopenshell.file, element) -> dict:
    """Kopiert ein Element mit neuer GlobalId und versetzt die Kopie."""
    copy = ifcopenshell.api.run("root.copy_class", model, product=element)
    copy.Name = f"{element.Name} (Kopie)"
    move_element(copy, COPY_OFFSET)
    return {"guid": copy.GlobalId, "copied_from": element.GlobalId, "name": copy.Name}


def delete_element(model: ifcopenshell.file, element) -> dict:
    """Entfernt ein Element samt Verweisen aus dem Modell."""
    info = {"guid": element.GlobalId, "ifc_class": element.is_a(), "name": element.Name}
    ifcopenshell.api.run("root.remove_product", model, product=element)
    return info


def make_variant(model: ifcopenshell.file, counts: dict, seed: int) -> dict:
    """Fuehrt alle Aenderungen aus und gibt die Ground Truth zurueck.

    Jedes Element wird hoechstens einmal veraendert, damit die Ground Truth
    eindeutig bleibt.
    """
    rng = random.Random(seed)
    pool = pick_candidates(model)
    rng.shuffle(pool)
    needed = counts["delete"] + counts["move"] + counts["modify"] + counts["add"]
    if needed > len(pool):
        raise ValueError(f"{needed} Aenderungen gewuenscht, aber nur {len(pool)} Bauteile vorhanden")

    truth = {"deleted": [], "moved": [], "modified": [], "added": []}
    # Reihenfolge: erst kopieren/aendern/verschieben, zuletzt loeschen,
    # damit geloeschte Elemente nicht mehr angefasst werden.
    for _ in range(counts["add"]):
        truth["added"].append(duplicate_element(model, pool.pop()))
    for _ in range(counts["modify"]):
        truth["modified"].append(modify_element(pool.pop()))
    for _ in range(counts["move"]):
        truth["moved"].append(move_element(pool.pop(), MOVE_OFFSET))
    for _ in range(counts["delete"]):
        truth["deleted"].append(delete_element(model, pool.pop()))
    return truth


def parse_args() -> argparse.Namespace:
    """Liest die Kommandozeilenargumente."""
    parser = argparse.ArgumentParser(description="Erzeugt einen Stand B aus einer IFC-Datei.")
    parser.add_argument("source", help="IFC-Datei (Stand A)")
    parser.add_argument("--output", help="Zieldatei, Standard: <source>_B.ifc")
    parser.add_argument("--n-delete", type=int, default=2)
    parser.add_argument("--n-move", type=int, default=2)
    parser.add_argument("--n-modify", type=int, default=2)
    parser.add_argument("--n-add", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42, help="Zufalls-Seed, fuer reproduzierbare Varianten")
    return parser.parse_args()


def main():
    """Einstieg: IFC laden, Variante erzeugen, IFC und Ground Truth schreiben."""
    args = parse_args()
    source = Path(args.source)
    output = Path(args.output) if args.output else source.with_name(source.stem + "_B.ifc")
    truth_path = output.with_name(output.stem + "_ground_truth.json")

    model = ifcopenshell.open(str(source))
    counts = {"delete": args.n_delete, "move": args.n_move,
              "modify": args.n_modify, "add": args.n_add}
    truth = make_variant(model, counts, args.seed)
    truth["source"] = source.name
    truth["variant"] = output.name
    truth["seed"] = args.seed

    model.write(str(output))
    with open(truth_path, "w", encoding="utf-8") as fh:
        json.dump(truth, fh, indent=2, ensure_ascii=False)

    print(f"Variante geschrieben: {output}")
    print(f"Ground Truth:         {truth_path}")
    for kind in ["added", "modified", "moved", "deleted"]:
        print(f"  {kind:<9} {len(truth[kind])}")


if __name__ == "__main__":
    main()
