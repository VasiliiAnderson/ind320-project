import streamlit as st


def _store_area_type():
    """Store the current area-type selection across pages."""
    st.session_state["selected_area_type"] = (
        st.session_state["_area_type_widget"]
    )


def _store_area_number():
    """Store the current area-number selection across pages."""
    st.session_state["selected_area_number"] = (
        st.session_state["_area_number_widget"]
    )


def area_selector(df):
    """
    Display a shared Magasinstatistikk area selector.

    The selected area type and number are stored in
    Streamlit session state so they can be reused across pages.

    Returns
    -------
    tuple
        selected_area_type, selected_area_number
    """

    preferred_order = ["EL", "NO", "VASS"]

    available_types = (
        df["area_type"]
        .dropna()
        .unique()
        .tolist()
    )

    area_types = [
        area_type
        for area_type in preferred_order
        if area_type in available_types
    ]

    # Initialise persistent area type
    if (
        "selected_area_type" not in st.session_state
        or st.session_state["selected_area_type"]
        not in area_types
    ):
        st.session_state["selected_area_type"] = "EL"

    # Load persistent value into widget state
    st.session_state["_area_type_widget"] = (
        st.session_state["selected_area_type"]
    )

    selected_area_type = st.radio(
        "Select area type",
        options=area_types,
        horizontal=True,
        key="_area_type_widget",
        on_change=_store_area_type,
    )

    # Find area numbers for selected type
    area_numbers = sorted(
        df.loc[
            df["area_type"] == selected_area_type,
            "area_number",
        ]
        .dropna()
        .unique()
        .tolist()
    )

    # Reset area number if it is invalid for new area type
    if (
        "selected_area_number" not in st.session_state
        or st.session_state["selected_area_number"]
        not in area_numbers
    ):
        st.session_state["selected_area_number"] = area_numbers[0]

    st.session_state["_area_number_widget"] = (
        st.session_state["selected_area_number"]
    )

    selected_area_number = st.selectbox(
        "Select area",
        options=area_numbers,
        key="_area_number_widget",
        on_change=_store_area_number,
    )

    return selected_area_type, selected_area_number