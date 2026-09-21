"""IFC-Diff Viewer - Streamlit-Oberflaeche (Minimalversion, wird in Etappe 5 ausgebaut).

Start aus dem Repo-Root mit aktivierter venv:
    streamlit run 02_Semesterprojekt/app.py
"""

import sys
from pathlib import Path

import streamlit as st

# Projektordner importierbar machen, egal von wo streamlit gestartet wird
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import ADDED, DATA_DIR, DELETED, MODIFIED, UNCHANGED  # noqa: E402
from src.database import connect, load_history, save_result  # noqa: E402
from src.diff_engine import compare_models  # noqa: E402
from src.ifc_loader import IfcModel  # noqa: E402


def list_ifc_files() -> list[str]:
    """Alle IFC-Dateien im data-Ordner, alphabetisch."""
    return sorted(path.name for path in DATA_DIR.glob("*.ifc"))


def show_kpis(result) -> None:
    """Kennzahlen-Zeile: eine Kachel je Aenderungsart."""
    counts = result.counts()
    columns = st.columns(4)
    columns[0].metric("Hinzugefuegt", counts[ADDED])
    columns[1].metric("Geloescht", counts[DELETED])
    columns[2].metric("Geaendert", counts[MODIFIED])
    columns[3].metric("Unveraendert", counts[UNCHANGED])


def main() -> None:
    """Seitenaufbau: Auswahl, Vergleich, Ergebnis, Historie."""
    st.set_page_config(page_title="IFC-Diff Viewer", layout="wide")
    st.title("IFC-Diff Viewer")

    files = list_ifc_files()
    column_a, column_b = st.columns(2)
    file_a = column_a.selectbox("Stand A (alt)", files, index=0)
    file_b = column_b.selectbox("Stand B (neu)", files, index=min(1, len(files) - 1))

    if st.button("Vergleichen", type="primary"):
        with st.spinner("Modelle laden und vergleichen ..."):
            result = compare_models(IfcModel(DATA_DIR / file_a), IfcModel(DATA_DIR / file_b))
            comparison_id = save_result(connect(), result)
        st.session_state["result"] = result
        st.success(f"Vergleich #{comparison_id} gespeichert ({result.duration_s:.2f} s)")

    result = st.session_state.get("result")
    if result is not None:
        if result.schema_differs():
            st.warning(f"Verschiedene Schemata: {result.schema_a} vs. {result.schema_b} - Vergleich unsicher")
        show_kpis(result)
        df = result.to_dataframe()
        only_changes = st.checkbox("Nur Aenderungen anzeigen", value=True)
        if only_changes:
            df = df[df["change_type"] != UNCHANGED]
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("Historie (SQLite)"):
        st.dataframe(load_history(connect()), use_container_width=True, hide_index=True)


main()
