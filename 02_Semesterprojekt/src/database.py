"""SQLite-Speicherung der Vergleichslaeufe (Historie), Schema nach Projektplan Kap. 9.

Drei Tabellen:
- comparison        ein Vergleichslauf mit Kennzahlen
- element_change    eine Zeile je Element und Lauf
- attribute_change  eine Zeile je geaendertem Attribut/Property
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import ADDED, DB_PATH, DELETED, MODIFIED, UNCHANGED
from src.diff_engine import DiffResult

SCHEMA = """
CREATE TABLE IF NOT EXISTS comparison (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    file_a       TEXT NOT NULL,
    file_b       TEXT NOT NULL,
    schema_a     TEXT,
    schema_b     TEXT,
    n_added      INTEGER,
    n_deleted    INTEGER,
    n_modified   INTEGER,
    n_unchanged  INTEGER,
    duration_s   REAL
);

CREATE TABLE IF NOT EXISTS element_change (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    comparison_id  INTEGER NOT NULL REFERENCES comparison(id),
    global_id      TEXT NOT NULL,
    ifc_class      TEXT,
    name           TEXT,
    storey         TEXT,
    change_type    TEXT NOT NULL,
    n_attr_changes INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_ec_comp ON element_change(comparison_id);
CREATE INDEX IF NOT EXISTS idx_ec_type ON element_change(change_type);

CREATE TABLE IF NOT EXISTS attribute_change (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    element_change_id INTEGER NOT NULL REFERENCES element_change(id),
    source            TEXT,
    pset_name         TEXT,
    property_name     TEXT NOT NULL,
    value_a           TEXT,
    value_b           TEXT
);
"""


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Oeffnet die Datenbank (legt Ordner und Tabellen bei Bedarf an)."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    return conn


def save_result(conn: sqlite3.Connection, result: DiffResult) -> int:
    """Speichert einen Vergleichslauf komplett und gibt die comparison.id zurueck."""
    counts = result.counts()
    cursor = conn.execute(
        """INSERT INTO comparison
           (created_at, file_a, file_b, schema_a, schema_b,
            n_added, n_deleted, n_modified, n_unchanged, duration_s)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (datetime.now().isoformat(timespec="seconds"),
         result.file_a, result.file_b, result.schema_a, result.schema_b,
         counts[ADDED], counts[DELETED], counts[MODIFIED], counts[UNCHANGED],
         result.duration_s),
    )
    comparison_id = cursor.lastrowid

    for change in result.changes:
        save_element_change(conn, comparison_id, change)

    conn.commit()
    return comparison_id


def save_element_change(conn: sqlite3.Connection, comparison_id: int, change) -> int:
    """Speichert ein ElementChange samt seinen Attributaenderungen."""
    cursor = conn.execute(
        """INSERT INTO element_change
           (comparison_id, global_id, ifc_class, name, storey, change_type, n_attr_changes)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (comparison_id, change.global_id, change.ifc_class, change.name,
         change.storey, change.change_type, change.n_attr_changes),
    )
    element_change_id = cursor.lastrowid

    rows = []
    for diff in change.attribute_changes:
        # Werte als Text: SQLite hat keine Tuples, und die UI zeigt sie ohnehin als Text
        rows.append((element_change_id, diff["source"], diff["pset_name"],
                     diff["property_name"], to_text(diff["value_a"]), to_text(diff["value_b"])))
    conn.executemany(
        """INSERT INTO attribute_change
           (element_change_id, source, pset_name, property_name, value_a, value_b)
           VALUES (?, ?, ?, ?, ?, ?)""",
        rows,
    )
    return element_change_id


def to_text(value) -> str:
    """Wandelt einen Wert fuer die Speicherung in Text um; None bleibt None."""
    if value is None:
        return None
    return str(value)


def load_history(conn: sqlite3.Connection) -> pd.DataFrame:
    """Alle Vergleichslaeufe, neuester zuerst."""
    return pd.read_sql("SELECT * FROM comparison ORDER BY id DESC", conn)


def load_changes(conn: sqlite3.Connection, comparison_id: int) -> pd.DataFrame:
    """Alle Elementaenderungen eines Laufs.

    int(): IDs aus einem DataFrame sind numpy.int64, die sqlite3 nicht
    korrekt bindet (liefert stillschweigend 0 Zeilen).
    """
    return pd.read_sql(
        "SELECT * FROM element_change WHERE comparison_id = ? ORDER BY change_type, ifc_class, name",
        conn, params=(int(comparison_id),),
    )


def load_attribute_changes(conn: sqlite3.Connection, element_change_id: int) -> pd.DataFrame:
    """Attributaenderungen eines Elements (Detailansicht alt/neu)."""
    return pd.read_sql(
        "SELECT source, pset_name, property_name, value_a, value_b "
        "FROM attribute_change WHERE element_change_id = ? ORDER BY source, property_name",
        conn, params=(int(element_change_id),),
    )
