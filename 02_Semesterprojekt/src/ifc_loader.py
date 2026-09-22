"""Kapselt eine IFC-Datei fuer den Vergleich (Klasse IfcModel)."""

from pathlib import Path

import ifcopenshell
import ifcopenshell.util.element

from src.config import COMPARED_ATTRIBUTES, EXCLUDED_ATTRIBUTES
from src.geometry import load_meshes, mesh_summary


class IfcModel:
    """Eine geladene IFC-Datei mit schnellem Zugriff ueber die GlobalId.

    Verglichen werden alle IfcProduct (Bauteile, Raeume, Geschosse usw.).
    Das Dict `elements` erlaubt das Matching zweier Staende in O(1) je Element
    statt einer verschachtelten Schleife (Projektplan Kap. 7, Punkt 8).
    """

    def __init__(self, path: str):
        """Oeffnet die Datei und baut das GUID-Dict auf."""
        self.path = Path(path)
        self.file = ifcopenshell.open(str(self.path))
        self.schema = self.file.schema
        self.elements = {}
        for product in self.file.by_type("IfcProduct"):
            self.elements[product.GlobalId] = product
        # Meshes werden erst auf Wunsch geladen (load_geometry), weil das
        # bei grossen Modellen dauert und fuer den Attributvergleich nicht noetig ist
        self.meshes = {}

    def __len__(self) -> int:
        """Anzahl Elemente im Modell."""
        return len(self.elements)

    def get_attributes(self, guid: str) -> dict:
        """Direkte Attribute eines Elements (Name, Description, ...).

        Nur die in config.COMPARED_ATTRIBUTES gelisteten; Attribute, die die
        IfcClass nicht hat (z.B. PredefinedType bei IfcSite), werden ausgelassen.
        """
        element = self.elements[guid]
        attributes = {}
        for name in COMPARED_ATTRIBUTES:
            if hasattr(element, name):
                attributes[name] = getattr(element, name)
        return attributes

    def get_psets(self, guid: str) -> dict:
        """Property Sets flach als {"Pset_X.PropY": wert}.

        get_psets() liefert auch Mengen (Qto_*) und je Pset einen Eintrag
        "id" (Entity-Nummer) - der wird ausgeschlossen, er ist keine
        Planungsinformation.
        """
        element = self.elements[guid]
        flat = {}
        for pset_name, properties in ifcopenshell.util.element.get_psets(element).items():
            for prop_name, value in properties.items():
                if prop_name in EXCLUDED_ATTRIBUTES:
                    continue
                flat[f"{pset_name}.{prop_name}"] = value
        return flat

    def get_storey(self, guid: str) -> str:
        """Name des Geschosses (oder des naechsten raeumlichen Containers).

        Im Unterricht wurde der Container ueber f.get_inverse() und
        IfcRelContainedInSpatialStructure gesucht; get_container() macht
        dasselbe in einer Zeile.
        """
        container = ifcopenshell.util.element.get_container(self.elements[guid])
        if container is None:
            return ""
        return container.Name or ""

    def get_placement(self, guid: str) -> tuple:
        """Lokale Einfuegekoordinaten (x, y, z) oder leeres Tuple."""
        placement = self.elements[guid].ObjectPlacement
        if placement is None or not placement.is_a("IfcLocalPlacement"):
            return ()
        return tuple(placement.RelativePlacement.Location.Coordinates)

    def get_info(self, guid: str) -> dict:
        """Kurzinfo fuer Tabellen: IfcClass, Name, Geschoss."""
        element = self.elements[guid]
        return {
            "ifc_class": element.is_a(),
            "name": element.Name or "",
            "storey": self.get_storey(guid),
        }

    def load_geometry(self) -> int:
        """Laedt alle Meshes (aus Cache oder neu) und gibt deren Anzahl zurueck."""
        self.meshes = load_meshes(self.path, self.file)
        return len(self.meshes)

    def get_geometry_summary(self, guid: str) -> dict:
        """Bounding-Box-Kennwerte eines Elements oder leeres Dict ohne Geometrie."""
        mesh = self.meshes.get(guid)
        if mesh is None:
            return {}
        return mesh_summary(mesh)
