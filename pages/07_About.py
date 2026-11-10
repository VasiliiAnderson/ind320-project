import streamlit as st


st.title("About the Project")

st.write(
    """
    This application has been developed progressively through the
    compulsory assignments in IND320 – Data to Decision at NMBU.

    Compulsory Assignment 3 extends the existing energy dashboard
    with geographical sampling, ERA5 weather data and additional
    time-series analysis methods.
    """
)

st.subheader("Purpose")

st.write(
    """
    The purpose of the application is to demonstrate how data from
    several external sources can be retrieved, processed, analysed
    and presented through an interactive Streamlit application.

    The dashboard allows users to explore Norwegian reservoir
    conditions, seasonal patterns, weather-related outliers and
    anomalies, and cross-border electricity flows.
    """
)

st.subheader("Data Sources")

st.write(
    """
    The project uses the following data sources:

    - **NVE Magasinstatistikk API** – Norwegian reservoir statistics,
      including filling levels, storage capacity and stored energy.
    - **Open-Meteo Historical Weather API** – hourly ERA5 reanalysis
      data for temperature, precipitation and snowfall.
    - **NVE geographical shapefiles** – electricity bidding areas
      and NVE regions used for geographical weather sampling.
    - **ENTSO-E Transparency Platform API** – physical cross-border
      electricity flow data between Norwegian bidding zones and
      neighbouring countries.
    """
)

st.subheader("Analysis Methods")

st.write(
    """
    Compulsory Assignment 3 introduces several additional analysis methods:

    - **DCT high-pass filtering and Statistical Process Control (SPC)**
      for identifying precipitation outliers.
    - **Local Outlier Factor (LOF)** for detecting temperature anomalies.
    - **Seasonal-Trend decomposition using LOESS (STL)** for separating
      reservoir filling levels into trend, seasonal and residual components.
    - **Spectrogram analysis** for examining how frequency patterns in
      reservoir filling levels change over time.
    """
)

st.subheader("Application Structure")

st.write(
    """
    The application contains seven pages:

    - **Home** – introduction and navigation
    - **Reservoir Data** – reservoir observations and sparklines
    - **Reservoir Plots** – interactive reservoir visualisations
    - **Seasonal Analysis** – STL decomposition and spectrogram analysis
    - **Weather Analysis** – precipitation/SPC and temperature/LOF analysis
    - **Cross-Border Flows** – import and export analysis based on
      ENTSO-E data stored in MongoDB
    - **About** – information about the project, data sources and methods
    """
)

st.subheader("Technology")

st.write(
    """
    The project uses Python together with Pandas, GeoPandas,
    Matplotlib, SciPy, scikit-learn, statsmodels and Streamlit.

    NVE shapefiles are processed using GeoPandas, while historical
    weather data are retrieved through Open-Meteo.

    Apache Spark and Cassandra are used in the cross-border electricity
    data pipeline, while MongoDB Atlas provides remote storage for the
    processed ENTSO-E observations used by Streamlit.
    """
)