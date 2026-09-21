"""Vergleich zweier IFC-Staende (Klassen ElementChange, DiffResult).

Vergleichslogik nach Projektplan Kap. 10:
1. Direkte Attribute (Name, Description, ObjectType, Tag, PredefinedType)
2. Property Sets, Zahlen mit Toleranz
3. Geometrie - in dieser Etappe nur die Einfuegekoordinaten (Placement);
   Bounding-Box und Dreiecksanzahl folgen in Etappe 6.
"""

import time
from dataclasses import dataclass, field

import pandas as pd

from src.config import ADDED, DELETED, LENGTH_TOLERANCE, MODIFIED, NUMBER_TOLERANCE, UNCHANGED
from src.ifc_loader import IfcModel

# Quellen einer Attributaenderung (entspricht Spalte "source" in SQLite)
SOURCE_ATTRIBUTE = "ATTRIBUTE"
SOURCE_PSET = "PSET"
SOURCE_GEOMETRY = "GEOMETRY"


@dataclass
class ElementChange:
    """Eine Aenderung an einem Element (oder "unveraendert")."""

    global_id: str
    ifc_class: str
    name: str
    storey: str
    change_type: str
    # Liste von Dicts: source, pset_name, property_name, value_a, value_b
    attribute_changes: list = field(default_factory=list)

    @property
    def n_attr_changes(self) -> int:
        """Anzahl geaenderter Attribute/Properties."""
        return len(self.attribute_changes)


@dataclass
class DiffResult:
    """Ergebnis eines Vergleichs: Liste der Aenderungen plus Kennzahlen."""

    file_a: str
    file_b: str
    schema_a: str
    schema_b: str
    changes: list = field(default_factory=list)
    duration_s: float = 0.0

    def count(self, change_type: str) -> int:
        """Anzahl Elemente einer Aenderungsart."""
        return sum(1 for change in self.changes if change.change_type == change_type)

    def counts(self) -> dict:
        """Kennzahlen je Aenderungsart."""
        return {kind: self.count(kind) for kind in [ADDED, DELETED, MODIFIED, UNCHANGED]}

    def schema_differs(self) -> bool:
        """True, wenn A und B verschiedene IFC-Schemata haben (Warnung in UI)."""
        return self.schema_a != self.schema_b

    def to_dataframe(self) -> pd.DataFrame:
        """Eine Zeile je Element, fuer Tabelle und Auswertung."""
        rows = []
        for change in self.changes:
            rows.append({
                "global_id": change.global_id,
                "ifc_class": change.ifc_class,
                "name": change.name,
                "storey": change.storey,
                "change_type": change.change_type,
                "n_attr_changes": change.n_attr_changes,
            })
        return pd.DataFrame(rows)


def values_equal(value_a, value_b, tolerance: float = NUMBER_TOLERANCE) -> bool:
    """Vergleicht zwei Werte; Zahlen mit Toleranz, alles andere exakt.

    bool ist in Python ein int, soll aber exakt verglichen werden.
    """
    is_number_a = isinstance(value_a, (int, float)) and not isinstance(value_a, bool)
    is_number_b = isinstance(value_b, (int, float)) and not isinstance(value_b, bool)
    if is_number_a and is_number_b:
        return abs(value_a - value_b) <= tolerance
    return value_a == value_b


def compare_dicts(dict_a: dict, dict_b: dict, source: str) -> list:
    """Vergleicht zwei flache Dicts und liefert die Unterschiede als Liste."""
    diffs = []
    all_keys = sorted(set(dict_a) | set(dict_b))
    for key in all_keys:
        value_a = dict_a.get(key)
        value_b = dict_b.get(key)
        if values_equal(value_a, value_b):
            continue
        # Bei Psets steckt der Pset-Name vor dem Punkt ("Qto_WallBaseQuantities.NetVolume")
        if source == SOURCE_PSET:
            pset_name, _, property_name = key.rpartition(".")
        else:
            pset_name, property_name = "", key
        diffs.append({
            "source": source,
            "pset_name": pset_name,
            "property_name": property_name,
            "value_a": value_a,
            "value_b": value_b,
        })
    return diffs


def compare_placement(placement_a: tuple, placement_b: tuple) -> list:
    """Vergleicht Einfuegekoordinaten mit der Laengentoleranz."""
    moved = len(placement_a) != len(placement_b)
    for coord_a, coord_b in zip(placement_a, placement_b):
        if abs(coord_a - coord_b) > LENGTH_TOLERANCE:
            moved = True
    if not moved:
        return []
    return [{
        "source": SOURCE_GEOMETRY,
        "pset_name": "",
        "property_name": "Placement",
        "value_a": placement_a,
        "value_b": placement_b,
    }]


def compare_element(model_a: IfcModel, model_b: IfcModel, guid: str) -> ElementChange:
    """Vergleicht ein Element, das in beiden Staenden vorkommt."""
    diffs = []
    diffs += compare_dicts(model_a.get_attributes(guid), model_b.get_attributes(guid), SOURCE_ATTRIBUTE)
    diffs += compare_dicts(model_a.get_psets(guid), model_b.get_psets(guid), SOURCE_PSET)
    diffs += compare_placement(model_a.get_placement(guid), model_b.get_placement(guid))

    change_type = MODIFIED if diffs else UNCHANGED
    # Beschreibende Infos immer aus dem neuen Stand B
    info = model_b.get_info(guid)
    return ElementChange(guid, info["ifc_class"], info["name"], info["storey"], change_type, diffs)


def compare_models(model_a: IfcModel, model_b: IfcModel) -> DiffResult:
    """Vergleicht Stand A (alt) mit Stand B (neu) ueber die GlobalId."""
    start = time.perf_counter()
    result = DiffResult(model_a.path.name, model_b.path.name, model_a.schema, model_b.schema)

    for guid in sorted(model_a.elements):
        if guid in model_b.elements:
            result.changes.append(compare_element(model_a, model_b, guid))
        else:
            info = model_a.get_info(guid)
            result.changes.append(ElementChange(guid, info["ifc_class"], info["name"], info["storey"], DELETED))

    for guid in sorted(model_b.elements):
        if guid not in model_a.elements:
            info = model_b.get_info(guid)
            result.changes.append(ElementChange(guid, info["ifc_class"], info["name"], info["storey"], ADDED))

    result.duration_s = time.perf_counter() - start
    return result
