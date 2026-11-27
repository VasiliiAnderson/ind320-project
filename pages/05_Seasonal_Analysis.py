import streamlit as st

from modules.area_selector import (
    area_selector,
)
from modules.data_loader import (
    load_data,
)
from modules.seasonal_analysis import (
    plot_spectrogram,
    plot_stl,
)


st.title(
    "Seasonal Patterns"
)

st.write(
    "Explore seasonal patterns in Norwegian reservoir "
    "filling levels using STL decomposition and an "
    "interactive spectrogram."
)


# ---------------------------------------------------------
# Load reservoir data
# ---------------------------------------------------------

df = load_data()


# ---------------------------------------------------------
# Shared geographical selection
# ---------------------------------------------------------

selected_area_type, selected_area = (
    area_selector(df)
)


# ---------------------------------------------------------
# Prepare weekly filling-level series
# ---------------------------------------------------------

fill_series = (
    df[
        (
            df["area_type"]
            == selected_area_type
        )
        & (
            df["area_number"]
            == selected_area
        )
    ][
        [
            "date",
            "fill_level",
        ]
    ]
    .dropna()
    .sort_values("date")
    .drop_duplicates(
        subset="date"
    )
    .set_index(
        "date"
    )[
        "fill_level"
    ]
)


st.caption(
    f"Analysing {selected_area_type} area "
    f"{selected_area} with "
    f"{len(fill_series)} weekly observations."
)


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

stl_tab, spectrogram_tab = (
    st.tabs(
        [
            "STL Decomposition",
            "Spectrogram",
        ]
    )
)


# =========================================================
# STL DECOMPOSITION
# =========================================================

with stl_tab:

    st.subheader(
        "STL Decomposition"
    )

    st.write(
        "STL separates the reservoir filling-level "
        "series into trend, seasonal and residual "
        "components."
    )


    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        seasonal = st.slider(
            "Seasonal smoother",
            min_value=3,
            max_value=51,
            value=13,
            step=2,
            help=(
                "Controls seasonal smoothing. "
                "The value must be odd."
            ),
        )


    with col2:

        trend = st.slider(
            "Trend smoother",
            min_value=53,
            max_value=201,
            value=53,
            step=2,
            help=(
                "Controls long-term trend smoothing."
            ),
        )


    with col3:

        robust = st.toggle(
            "Robust fitting",
            value=True,
            help=(
                "Reduces the influence of extreme "
                "observations."
            ),
        )


    if len(fill_series) < 104:

        st.warning(
            "At least two years of weekly observations "
            "are recommended for the STL analysis."
        )

    else:

        stl_fig = plot_stl(
            fill_series,
            seasonal=seasonal,
            trend=trend,
            robust=robust,
        )

        st.plotly_chart(
            stl_fig,
            width="stretch",
        )


        st.caption(
            "The trend represents long-term development, "
            "the seasonal component captures recurring "
            "annual behaviour, and the residual contains "
            "variation not explained by those components."
        )


# =========================================================
# SPECTROGRAM
# =========================================================

with spectrogram_tab:

    st.subheader(
        "Spectrogram"
    )

    st.write(
        "The spectrogram shows how the frequency "
        "content of reservoir filling levels changes "
        "over time."
    )


    col1, col2 = (
        st.columns(2)
    )


    with col1:

        window_length = st.slider(
            "Window length (weeks)",
            min_value=52,
            max_value=min(
                208,
                len(fill_series),
            ),
            value=min(
                104,
                len(fill_series),
            ),
            step=26,
            help=(
                "Number of weekly observations "
                "included in each window."
            ),
        )


    with col2:

        overlap = st.slider(
            "Window overlap (weeks)",
            min_value=0,
            max_value=(
                window_length - 1
            ),
            value=min(
                52,
                window_length - 1,
            ),
            help=(
                "Number of observations shared "
                "between consecutive windows."
            ),
        )


    if (
        len(fill_series)
        < window_length
    ):

        st.warning(
            "The selected window is longer than "
            "the available time series."
        )

    else:

        spectrogram_fig = (
            plot_spectrogram(
                fill_series,
                window_length=(
                    window_length
                ),
                overlap=overlap,
            )
        )

        st.plotly_chart(
            spectrogram_fig,
            width="stretch",
        )


        st.caption(
            "A persistent concentration of power around "
            "1 cycle per year indicates an annual "
            "seasonal pattern in reservoir filling."
        )