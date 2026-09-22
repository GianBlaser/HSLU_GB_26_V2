"""IFC-Diff Viewer - Streamlit-Oberflaeche.

Start aus dem Repo-Root mit aktivierter venv:
    streamlit run 02_Semesterprojekt/app.py

Aufbau: main() ruft je Seitenbereich eine Funktion auf. Das Vergleichs-
ergebnis liegt in st.session_state["result"], damit es Filter- und
Tab-Wechsel ueberlebt (Streamlit fuehrt das Skript bei jeder Interaktion
von oben neu aus).
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Projektordner importierbar machen, egal von wo streamlit gestartet wird
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.analytics import (changes_by_class, changes_by_storey, filter_changes,  # noqa: E402
                           top_changed_properties)
from src.charts import plot_changes_by_class, plot_changes_by_storey, plot_top_properties  # noqa: E402
from src.config import (ADDED, CONTEXT_MODES, DATA_DIR, DELETED, MODIFIED, OUTPUT_DIR,  # noqa: E402
                        UNCHANGED)
from src.database import connect, load_history, save_result  # noqa: E402
from src.diff_engine import DiffResult, compare_models  # noqa: E402
from src.ifc_loader import IfcModel  # noqa: E402
from src.report import write_report  # noqa: E402
from src.viewer import render_image  # noqa: E402

UPLOAD_DIR = OUTPUT_DIR / "uploads"
ALL = "(alle)"


# --- Dateiauswahl ------------------------------------------------------------

def save_upload(uploaded_file) -> Path:
    """Schreibt eine hochgeladene Datei nach output/uploads (ifcopenshell braucht einen Pfad)."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    path = UPLOAD_DIR / uploaded_file.name
    with open(path, "wb") as fh:
        fh.write(uploaded_file.getbuffer())
    return path


def select_file(label: str, default_index: int) -> Path:
    """Eine Datei waehlen: aus data/ oder per Upload. Gibt den Pfad zurueck."""
    files = sorted(path.name for path in DATA_DIR.glob("*.ifc"))
    st.markdown(f"**{label}**")
    uploaded = st.file_uploader("Eigene IFC hochladen", type=["ifc"], key=f"upload_{label}")
    if uploaded is not None:
        return save_upload(uploaded)
    name = st.selectbox("oder aus data/ waehlen", files, index=min(default_index, len(files) - 1),
                        key=f"select_{label}")
    return DATA_DIR / name


def run_comparison(path_a: Path, path_b: Path, with_geometry: bool) -> None:
    """Vergleicht zwei Dateien, speichert in SQLite und im Session-State."""
    with st.spinner("Modelle laden und vergleichen ..."):
        model_a, model_b = IfcModel(path_a), IfcModel(path_b)
        if with_geometry:
            # Erster Aufruf tesselliert und cacht, danach kommt alles aus cache/
            model_a.load_geometry()
            model_b.load_geometry()
        result = compare_models(model_a, model_b)
        comparison_id = save_result(connect(), result)
    st.session_state["result"] = result
    st.session_state["comparison_id"] = comparison_id
    # Modelle behalten: der 3D-Viewer braucht die Meshes
    st.session_state["models"] = (model_a, model_b) if with_geometry else None
    st.session_state.pop("render", None)


# --- Ergebnisdarstellung -----------------------------------------------------

def show_kpis(result: DiffResult) -> None:
    """Kennzahlen-Zeile: eine Kachel je Aenderungsart."""
    counts = result.counts()
    columns = st.columns(4)
    columns[0].metric("Hinzugefuegt", counts[ADDED])
    columns[1].metric("Geloescht", counts[DELETED])
    columns[2].metric("Geaendert", counts[MODIFIED])
    columns[3].metric("Unveraendert", counts[UNCHANGED])


def show_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Filterleiste; gibt die gefilterte Tabelle zurueck."""
    columns = st.columns(4)
    ifc_class = columns[0].selectbox("IfcClass", [ALL] + sorted(df["ifc_class"].unique()))
    storey = columns[1].selectbox("Geschoss", [ALL] + sorted(df["storey"].unique()))
    change_type = columns[2].selectbox("Aenderungsart", [ALL, ADDED, DELETED, MODIFIED, UNCHANGED])
    only_changes = columns[3].checkbox("Nur Aenderungen", value=True)

    filtered = filter_changes(
        df,
        ifc_class="" if ifc_class == ALL else ifc_class,
        storey="" if storey == ALL else storey,
        change_type="" if change_type == ALL else change_type,
    )
    if only_changes:
        filtered = filtered[filtered["change_type"] != UNCHANGED]
    return filtered


def show_table(df: pd.DataFrame) -> str:
    """Tabelle mit Zeilenauswahl; gibt die GlobalId der gewaehlten Zeile zurueck ("" = keine)."""
    event = st.dataframe(df, use_container_width=True, hide_index=True,
                         on_select="rerun", selection_mode="single-row")
    rows = event.selection.rows
    if not rows:
        return ""
    return df.iloc[rows[0]]["global_id"]


def show_details(result: DiffResult, guid: str) -> None:
    """Detailansicht alt/neu fuer ein Element."""
    change = None
    for candidate in result.changes:
        if candidate.global_id == guid:
            change = candidate
    if change is None:
        return
    st.subheader(f"{change.name}  ({change.ifc_class}, {change.change_type})")
    st.caption(f"GlobalId {change.global_id} - Geschoss: {change.storey or '-'}")
    if change.attribute_changes:
        details = pd.DataFrame(change.attribute_changes)
        details.columns = ["Quelle", "Pset", "Property", "Wert A (alt)", "Wert B (neu)"]
        st.dataframe(details.astype(str), use_container_width=True, hide_index=True)
    else:
        st.info("Keine Attributaenderungen (Element hinzugefuegt, geloescht oder unveraendert).")


def show_charts(result: DiffResult, df: pd.DataFrame) -> None:
    """Drei Diagramme aus charts.py."""
    if result.count(UNCHANGED) == len(result.changes):
        st.info("Keine Aenderungen - keine Diagramme.")
        return
    left, right = st.columns(2)
    left.pyplot(plot_changes_by_storey(changes_by_storey(df)))
    right.pyplot(plot_changes_by_class(changes_by_class(df)))
    st.pyplot(plot_top_properties(top_changed_properties(result)))


def show_export(df: pd.DataFrame, comparison_id: int) -> None:
    """CSV-Download der (gefilterten) Tabelle."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("CSV herunterladen", csv, file_name=f"ifc_diff_{comparison_id}.csv",
                       mime="text/csv")


def show_viewer(result: DiffResult, filtered: pd.DataFrame, selected_guid: str) -> None:
    """3D-Ansicht: geaenderte Elemente farbig, Kontext waehlbar, Filter aus der Tabelle."""
    models = st.session_state.get("models")
    if models is None:
        st.info("Fuer die 3D-Ansicht beim Vergleich das Haekchen 'Geometrie vergleichen' setzen.")
        return
    left, right = st.columns([1, 3])
    context_mode = left.radio("Unveraenderte Elemente", CONTEXT_MODES)
    use_filter = left.checkbox("Nur gefilterte Elemente (Tab Tabelle)", value=False)
    focus = left.checkbox("Kamera auf gewaehltes Element (Tab Tabelle)", value=bool(selected_guid),
                          disabled=not selected_guid)
    guids = set(filtered["global_id"]) if use_filter else {c.global_id for c in result.changes}
    focus_guid = selected_guid if focus else ""

    # Nur neu rendern, wenn sich Kontext, Auswahl oder Fokus geaendert haben
    key = (context_mode, frozenset(guids), focus_guid)
    cached = st.session_state.get("render")
    if cached is None or cached[0] != key:
        with st.spinner("Rendern ..."):
            image = render_image(result, models[0], models[1], guids, context_mode, focus_guid)
        st.session_state["render"] = (key, image)
    right.image(st.session_state["render"][1], use_container_width=True)
    left.caption("DELETED aus Stand A, alle anderen aus Stand B. Ansicht isometrisch auf die Aenderungen.")


def show_report_button(result: DiffResult, comparison_id: int) -> None:
    """PDF-Report erzeugen (mit 3D-Bild, falls gerendert) und zum Download anbieten."""
    if st.button("PDF-Report erzeugen"):
        cached = st.session_state.get("render")
        image = cached[1] if cached else None
        path = write_report(result, OUTPUT_DIR / f"ifc_diff_report_{comparison_id}.pdf", image)
        with open(path, "rb") as fh:
            st.download_button("PDF herunterladen", fh.read(), file_name=path.name, mime="application/pdf")


def show_history() -> None:
    """Alle bisherigen Laeufe aus SQLite."""
    st.dataframe(load_history(connect()), use_container_width=True, hide_index=True)


# --- Seite -------------------------------------------------------------------

def main() -> None:
    """Seitenaufbau: Auswahl, Vergleich, Tabs mit Tabelle / Diagrammen / Historie."""
    st.set_page_config(page_title="IFC-Diff Viewer", layout="wide")
    st.title("IFC-Diff Viewer")
    st.caption("Vergleicht zwei Staende desselben IFC-Modells ueber die GlobalId.")

    column_a, column_b = st.columns(2)
    with column_a:
        path_a = select_file("Stand A (alt)", 0)
    with column_b:
        path_b = select_file("Stand B (neu)", 1)

    with_geometry = st.checkbox("Geometrie vergleichen (Bounding-Box, Dreiecksanzahl) - erster Lauf dauert laenger",
                                value=True)
    if st.button("Vergleichen", type="primary"):
        run_comparison(path_a, path_b, with_geometry)

    result = st.session_state.get("result")
    if result is None:
        st.info("Zwei Dateien waehlen und auf Vergleichen klicken.")
        return

    comparison_id = st.session_state["comparison_id"]
    st.success(f"{result.file_a}  ->  {result.file_b}   |   Vergleich #{comparison_id} gespeichert "
               f"({result.duration_s:.2f} s)")
    if result.schema_differs():
        st.warning(f"Verschiedene Schemata: {result.schema_a} vs. {result.schema_b} - Vergleich unsicher")
    show_kpis(result)

    df = result.to_dataframe()
    tab_table, tab_viewer, tab_charts, tab_history = st.tabs(["Tabelle", "3D-Ansicht", "Diagramme", "Historie"])
    with tab_table:
        filtered = show_filters(df)
        selected_guid = show_table(filtered)
        show_export(filtered, comparison_id)
        if selected_guid:
            show_details(result, selected_guid)
    with tab_viewer:
        show_viewer(result, filtered, selected_guid)
        show_report_button(result, comparison_id)
    with tab_charts:
        show_charts(result, df)
    with tab_history:
        show_history()


main()
