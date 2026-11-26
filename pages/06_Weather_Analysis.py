import streamlit as st

from modules.area_selector import (
    area_selector,
)
from modules.data_loader import (
    load_data,
)
from modules.weather_analysis import (
    download_weather,
    lof_outliers,
    spc_outliers,
)


st.title(
    "Weather & Anomalies"
)

st.write(
    "Explore ERA5 weather data and identify unusual "
    "observations using seasonally adjusted variation, "
    "statistical process control and Local Outlier Factor."
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


st.caption(
    f"ERA5 weather data for "
    f"{selected_area_type} area {selected_area}, "
    "based on 10 reproducibly sampled locations."
)


# ---------------------------------------------------------
# Download weather
# ---------------------------------------------------------

with st.spinner(
    "Loading ERA5 weather data..."
):

    weather = download_weather(
        area_type=selected_area_type,
        area_number=selected_area,
        start_date="2024-01-01",
        end_date="2024-12-31",
        n_locations=10,
    )


# ---------------------------------------------------------
# Weather-property selection
# ---------------------------------------------------------

weather_options = {
    "Temperature": {
        "column": "avg_temperature",
        "unit": "°C",
    },
    "Precipitation": {
        "column": "avg_precipitation",
        "unit": "mm",
    },
    "Snowfall": {
        "column": "avg_snowfall",
        "unit": "cm",
    },
}


selected_weather = st.selectbox(
    "Weather property",
    options=list(
        weather_options.keys()
    ),
    index=0,
    help=(
        "Select the meteorological property used "
        "in both anomaly analyses."
    ),
)


weather_column = (
    weather_options[
        selected_weather
    ]["column"]
)

weather_unit = (
    weather_options[
        selected_weather
    ]["unit"]
)


weather_series = (
    weather
    .set_index(
        "time"
    )[
        weather_column
    ]
    .dropna()
)


# ---------------------------------------------------------
# Basic summary
# ---------------------------------------------------------

summary_col1, summary_col2, summary_col3 = (
    st.columns(3)
)


summary_col1.metric(
    "Observations",
    f"{len(weather_series):,}",
)


summary_col2.metric(
    "Mean",
    (
        f"{weather_series.mean():.2f} "
        f"{weather_unit}"
    ),
)


summary_col3.metric(
    "Standard deviation",
    (
        f"{weather_series.std():.2f} "
        f"{weather_unit}"
    ),
)


# ---------------------------------------------------------
# Analysis tabs
# ---------------------------------------------------------

spc_tab, lof_tab = st.tabs(
    [
        "SATV / SPC",
        "Local Outlier Factor",
    ]
)


# =========================================================
# SATV / SPC
# =========================================================

with spc_tab:

    st.subheader(
        "Seasonally Adjusted Variation & SPC"
    )

    st.write(
        "DCT high-pass filtering is used to remove "
        "slow seasonal variation. Robust statistical "
        "process-control boundaries are then used to "
        "identify unusual observations."
    )


    col1, col2 = (
        st.columns(2)
    )


    with col1:

        cutoff = st.slider(
            "DCT cut-off (cycles/year)",
            min_value=2,
            max_value=24,
            value=12,
            step=1,
            help=(
                "Controls how much low-frequency "
                "seasonal variation is removed."
            ),
        )


    with col2:

        n_sd = st.slider(
            "SPC standard deviations",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.5,
        )


    spc_fig, spc_summary = (
        spc_outliers(
            weather_series,
            cutoff=cutoff,
            n_sd=n_sd,
            variable_label=(
                selected_weather
            ),
            unit=weather_unit,
        )
    )


    st.plotly_chart(
        spc_fig,
        width="stretch",
    )


    metric_col1, metric_col2 = (
        st.columns(2)
    )


    metric_col1.metric(
        "SPC outliers",
        spc_summary[
            "n_outliers"
        ],
    )


    metric_col2.metric(
        "Share of observations",
        (
            f"{spc_summary['share']:.2%}"
        ),
    )


# =========================================================
# LOCAL OUTLIER FACTOR
# =========================================================

with lof_tab:

    st.subheader(
        "Local Outlier Factor"
    )

    st.write(
        "Local Outlier Factor identifies observations "
        "whose local density differs substantially from "
        "surrounding observations."
    )


    col1, col2 = (
        st.columns(2)
    )


    with col1:

        contamination = st.slider(
            "Expected anomaly proportion",
            min_value=0.005,
            max_value=0.05,
            value=0.01,
            step=0.005,
            format="%.3f",
        )


    with col2:

        n_neighbors = st.slider(
            "Number of neighbours",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
        )


    lof_fig, lof_summary = (
        lof_outliers(
            weather_series,
            contamination=(
                contamination
            ),
            n_neighbors=(
                n_neighbors
            ),
            variable_label=(
                selected_weather
            ),
            unit=weather_unit,
        )
    )


    st.plotly_chart(
        lof_fig,
        width="stretch",
    )


    metric_col1, metric_col2 = (
        st.columns(2)
    )


    metric_col1.metric(
        "LOF anomalies",
        lof_summary[
            "n_anomalies"
        ],
    )


    metric_col2.metric(
        "Share of observations",
        (
            f"{lof_summary['share']:.2%}"
        ),
    )


# ---------------------------------------------------------
# Method information
# ---------------------------------------------------------

with st.expander(
    "About the methods"
):

    st.markdown(
        """
        **SATV / SPC**

        A discrete cosine transform is used to remove
        lower-frequency seasonal behaviour. The remaining
        seasonally adjusted variation is used to construct
        robust SPC boundaries.

        **Local Outlier Factor**

        LOF compares the local density around each observation
        with the density around neighbouring observations.
        Observations in unusually sparse regions are classified
        as anomalies.

        The same methods can be applied interactively to
        temperature, precipitation and snowfall.
        """
    )