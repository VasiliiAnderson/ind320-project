import matplotlib.pyplot as plt
import streamlit as st

from modules.weather_analysis import (
    download_weather,
    spc_outliers,
    temperature_lof,
)


st.title("Weather Analysis")

st.write(
    "Explore ERA5 precipitation and temperature data "
    "for Norwegian electricity areas."
)

# Select electricity area
area_number = st.selectbox(
    "Select electricity area",
    options=[1, 2, 3, 4, 5],
    index=2,
)

region = f"NO{area_number}"

st.caption(
    f"Weather data are downloaded for {region} "
    "using sampled locations within the bidding area."
)

# Assignment requires NO3 for 2024 in the notebook.
# The Streamlit page allows the same analysis for all areas.
weather = download_weather(
    region=region,
    start_date="2024-01-01",
    end_date="2024-12-31",
    n_locations=10,
)

precipitation_series = (
    weather
    .set_index("time")["avg_precipitation"]
)

temperature_series = (
    weather
    .set_index("time")["avg_temperature"]
)

# Required analysis tabs
spc_tab, lof_tab = st.tabs(
    [
        "Precipitation / SPC",
        "Temperature / LOF",
    ]
)


# ---------------------------------------------------------
# PRECIPITATION / SPC
# ---------------------------------------------------------

with spc_tab:
    st.subheader(
        "Precipitation Outliers"
    )

    st.write(
        "DCT high-pass filtering is used to remove "
        "slow seasonal variation before robust SPC "
        "boundaries are calculated."
    )

    col1, col2 = st.columns(2)

    with col1:
        cutoff = st.slider(
            "DCT cut-off (cycles/year)",
            min_value=2,
            max_value=24,
            value=12,
            step=1,
        )

    with col2:
        n_sd = st.slider(
            "SPC standard deviations",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.5,
        )

    spc_fig, spc_summary = spc_outliers(
        precipitation_series,
        cutoff=cutoff,
        n_sd=n_sd,
    )

    st.pyplot(spc_fig)
    plt.close(spc_fig)

    col1, col2 = st.columns(2)

    col1.metric(
        "Outliers",
        spc_summary["n_outliers"],
    )

    col2.metric(
        "Share of observations",
        f"{spc_summary['share']:.2%}",
    )


# ---------------------------------------------------------
# TEMPERATURE / LOF
# ---------------------------------------------------------

with lof_tab:
    st.subheader(
        "Temperature Anomalies"
    )

    st.write(
        "Local Outlier Factor identifies temperature "
        "observations with unusual local density."
    )

    contamination = st.slider(
        "Expected anomaly proportion",
        min_value=0.005,
        max_value=0.05,
        value=0.01,
        step=0.005,
        format="%.3f",
    )

    lof_fig, lof_summary = temperature_lof(
        temperature_series,
        contamination=contamination,
    )

    st.pyplot(lof_fig)
    plt.close(lof_fig)

    col1, col2 = st.columns(2)

    col1.metric(
        "Anomalies",
        lof_summary["n_anomalies"],
    )

    col2.metric(
        "Share of observations",
        f"{lof_summary['share']:.2%}",
    )