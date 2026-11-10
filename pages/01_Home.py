import streamlit as st


st.title("IND320 Energy Dashboard")

st.write(
    """
    This application was developed as part of IND320 – Data to Decision
    at NMBU. The project combines Norwegian reservoir statistics,
    cross-border electricity flow data and historical ERA5 weather data
    in an interactive Streamlit dashboard.
    """
)

st.subheader("Navigation")

st.write(
    """
    Use the sidebar to navigate between:

    - **Home** – introduction to the application
    - **Reservoir Data** – explore reservoir statistics retrieved from the NVE API
    - **Reservoir Plots** – visualise reservoir measurements across geographical areas and time periods
    - **Seasonal Analysis** – analyse reservoir filling levels using STL decomposition and a spectrogram
    - **Weather Analysis** – analyse ERA5 precipitation outliers and temperature anomalies
    - **Cross-Border Flows** – analyse electricity imports and exports using ENTSO-E data stored in MongoDB
    - **About** – information about the project, data sources and technology
    """
)

st.subheader("Data Sources")

st.write(
    """
    Reservoir statistics are retrieved directly from the
    **NVE Magasinstatistikk API**.

    Historical temperature, precipitation and snowfall data are
    retrieved from the **Open-Meteo Historical Weather API** using
    the ERA5 reanalysis model. NVE geographical shapefiles are used
    to define the relevant Norwegian regions and sample weather
    locations.

    Cross-border physical flow data are retrieved from the
    **ENTSO-E Transparency Platform API**, processed using Cassandra
    and Spark, and stored in MongoDB Atlas for use in the application.
    """
)