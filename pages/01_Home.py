import streamlit as st


st.title("IND320 Energy Dashboard")

st.write(
    """
    An interactive dashboard for exploring, analysing and forecasting
    Norwegian reservoir conditions using data from NVE, ERA5,
    ENTSO-E and Norges Bank.
    """
)


# ---------------------------------------------------------
# Main workflow
# ---------------------------------------------------------

st.subheader("Explore → Analyse → Predict")

col1, col2, col3 = st.columns(3)


with col1:
    st.markdown(
        """
        ### 🗺️ Explore

        Explore geographical reservoir conditions,
        weather patterns, electricity flows and
        exchange rates.

        **Pages**
        - Map & Data Overview
        - Energy & Markets
        """
    )


with col2:
    st.markdown(
        """
        ### 📊 Analyse

        Investigate seasonal behaviour, anomalies and
        relationships between weather and reservoir
        filling.

        **Pages**
        - Seasonal Patterns
        - Weather & Anomalies
        - Weather–Reservoir Correlation
        """
    )


with col3:
    st.markdown(
        """
        ### 🔮 Predict

        Forecast future reservoir filling levels using
        River SNARIMAX models with optional weather and
        currency variables.

        **Page**
        - Reservoir Forecast
        """
    )


# ---------------------------------------------------------
# Shared geographical selection
# ---------------------------------------------------------

st.subheader("Shared Area Selection")

st.write(
    """
    The geographical selection made on the **Map & Data Overview**
    page is stored using Streamlit session state and reused across
    relevant analysis and forecasting pages.

    This allows the dashboard to behave as one connected application
    rather than a collection of independent pages.
    """
)


# ---------------------------------------------------------
# Data sources
# ---------------------------------------------------------

st.subheader("Data Sources")

st.markdown(
    """
    - **NVE Magasinstatistikk API** – reservoir filling levels,
      capacity and stored energy.
    - **Open-Meteo Historical Weather API / ERA5** – temperature,
      precipitation and snowfall.
    - **NVE geographical shapefiles** – electricity price areas
      and Norwegian water regions.
    - **ENTSO-E Transparency Platform** – cross-border electricity flows.
    - **Norges Bank API** – EUR/NOK and USD/NOK exchange rates.
    """
)


# ---------------------------------------------------------
# Key functionality
# ---------------------------------------------------------

st.subheader("Dashboard Features")

st.markdown(
    """
    The dashboard includes:

    - interactive GeoJSON maps
    - interactive Plotly visualisations
    - STL decomposition and spectrogram analysis
    - SATV/SPC and Local Outlier Factor anomaly detection
    - sliding-window weather–reservoir correlations
    - River SNARIMAX reservoir forecasting
    - selectable forecasting parameters and exogenous variables
    - caching, loading indicators and error handling
    """
)