import matplotlib.pyplot as plt
import streamlit as st

from modules.area_selector import area_selector
from modules.data_loader import load_data
from modules.seasonal_analysis import (
    plot_spectrogram,
    plot_stl,
)


st.title("Seasonal Analysis")

st.write(
    "Explore seasonal patterns in Norwegian reservoir filling "
    "levels using STL decomposition and a spectrogram."
)

# Load reservoir statistics directly from the NVE API
df = load_data()

# Use the shared Magasinstatistikk area selector
selected_area_type, selected_area = area_selector(df)

# Prepare weekly filling-level series
fill_series = (
    df[
        (df["area_type"] == selected_area_type)
        & (df["area_number"] == selected_area)
    ][["date", "fill_level"]]
    .dropna()
    .sort_values("date")
    .drop_duplicates(subset="date")
    .set_index("date")["fill_level"]
)

st.caption(
    f"Analysing {selected_area_type} area {selected_area} "
    f"with {len(fill_series)} weekly observations."
)

# Create the required tabs
stl_tab, spectrogram_tab = st.tabs(
    ["STL Decomposition", "Spectrogram"]
)


# -------------------------------------------------------------------
# STL TAB
# -------------------------------------------------------------------

with stl_tab:
    st.subheader("STL Decomposition")

    st.write(
        "STL separates the reservoir filling-level time series into "
        "trend, seasonal and residual components."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        seasonal = st.slider(
            "Seasonal smoother",
            min_value=3,
            max_value=51,
            value=13,
            step=2,
            help=(
                "Controls the seasonal smoothing. "
                "The value must be an odd integer."
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
                "Controls the long-term trend smoothing. "
                "The value must be an odd integer greater than 52."
            ),
        )

    with col3:
        robust = st.toggle(
            "Robust fitting",
            value=True,
            help=(
                "Reduces the influence of extreme observations "
                "on the decomposition."
            ),
        )

    # Perform STL analysis
    stl_fig = plot_stl(
        fill_series,
        seasonal=seasonal,
        trend=trend,
        robust=robust,
    )

    # Display STL figure
    st.pyplot(stl_fig)

    # Close Matplotlib figure after rendering
    plt.close(stl_fig)

    st.caption(
        "The decomposition separates the observed filling level "
        "into trend, seasonal and residual components."
    )


# -------------------------------------------------------------------
# SPECTROGRAM TAB
# -------------------------------------------------------------------

with spectrogram_tab:
    st.subheader("Spectrogram")

    st.write(
        "The spectrogram shows how the frequency content of the "
        "reservoir filling-level series changes over time."
    )

    col1, col2 = st.columns(2)

    with col1:
        window_length = st.slider(
            "Window length (weeks)",
            min_value=52,
            max_value=208,
            value=104,
            step=26,
            help=(
                "Number of weekly observations included "
                "in each spectrogram window."
            ),
        )

    with col2:
        overlap = st.slider(
            "Window overlap (weeks)",
            min_value=0,
            max_value=window_length - 1,
            value=min(52, window_length - 1),
            help=(
                "Number of observations shared between "
                "consecutive spectrogram windows."
            ),
        )

    # Create spectrogram
    spectrogram_fig = plot_spectrogram(
        fill_series,
        window_length=window_length,
        overlap=overlap,
    )

    # Display spectrogram
    st.pyplot(spectrogram_fig)

    # Close Matplotlib figure after rendering
    plt.close(spectrogram_fig)

    st.caption(
        "A strong signal around 1 cycle per year indicates "
        "an annual seasonal pattern in reservoir filling."
    )