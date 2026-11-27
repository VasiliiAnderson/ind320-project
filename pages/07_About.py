import streamlit as st


st.title("About the Project")

st.write(
    """
    This application was developed as part of
    **IND320 – Data to Decision at NMBU**.

    The project demonstrates how multiple energy, weather and
    financial data sources can be integrated, analysed and presented
    through an interactive decision-support dashboard.
    """
)


# ---------------------------------------------------------
# Purpose
# ---------------------------------------------------------

st.subheader("Purpose")

st.write(
    """
    The main purpose of the dashboard is to explore how Norwegian
    reservoir conditions develop over time and how they relate to
    weather conditions, electricity markets and selected financial
    variables.

    The application follows the workflow:

    **Explore → Analyse → Predict**
    """
)


# ---------------------------------------------------------
# Data sources
# ---------------------------------------------------------

st.subheader("Data Sources")

st.markdown(
    """
    - **NVE Magasinstatistikk API**  
      Weekly Norwegian reservoir filling levels, capacity and
      stored energy.

    - **Open-Meteo Historical Weather API**  
      ERA5 temperature, precipitation and snowfall observations.

    - **NVE geographical shapefiles**  
      Used to define electricity price areas and water regions
      and to sample geographical weather locations.

    - **ENTSO-E Transparency Platform**  
      Physical cross-border electricity-flow observations.

    - **Norges Bank API**  
      Daily EUR/NOK and USD/NOK spot exchange rates.
    """
)


# ---------------------------------------------------------
# Analysis methods
# ---------------------------------------------------------

st.subheader("Analysis Methods")

st.markdown(
    """
    The dashboard uses several time-series and machine-learning methods:

    - **STL decomposition** for separating reservoir filling levels
      into trend, seasonal and residual components.
    - **Spectrogram analysis** for studying how frequency patterns
      change over time.
    - **Discrete Cosine Transform (DCT)** and **Statistical Process
      Control (SPC)** for identifying unusual weather observations.
    - **Local Outlier Factor (LOF)** for anomaly detection.
    - **Sliding-window correlation** with selectable lag and window
      length for investigating weather–reservoir relationships.
    - **River SNARIMAX** for monthly reservoir forecasting with
      optional exogenous weather and currency variables.
    """
)


# ---------------------------------------------------------
# Application structure
# ---------------------------------------------------------

st.subheader("Application Structure")

st.markdown(
    """
    ### Explore
    - **Map & Data Overview**
    - **Energy & Markets**

    ### Analyse
    - **Seasonal Patterns**
    - **Weather & Anomalies**
    - **Weather–Reservoir Correlation**

    ### Predict
    - **Reservoir Forecast**

    ### Information
    - **About**
    """
)


# ---------------------------------------------------------
# Forecasting
# ---------------------------------------------------------

st.subheader("Forecasting")

st.write(
    """
    Reservoir forecasts are produced at monthly resolution using
    River's SNARIMAX model.

    Users can configure the training history, forecast horizon,
    model parameters and exogenous variables.

    Since actual future weather and exchange rates are unknown,
    historical monthly weather averages and the latest observed
    currency rates are used as transparent future assumptions.

    Raw model predictions are retained, while displayed reservoir
    filling forecasts are constrained to the physically valid
    interval between 0 and 1.
    """
)


# ---------------------------------------------------------
# Performance and robustness
# ---------------------------------------------------------

st.subheader("Performance and Robustness")

st.markdown(
    """
    Several measures are used to improve the user experience:

    - Streamlit caching reduces repeated API and database calls.
    - Loading indicators are shown during computationally expensive
      operations.
    - External API and database errors are handled gracefully.
    - ERA5 availability is checked before weather requests are made.
    - Smaller representative geographical samples are used where
      appropriate to reduce API usage.
    """
)


# ---------------------------------------------------------
# Technology
# ---------------------------------------------------------

st.subheader("Technology")

st.markdown(
    """
    The project uses:

    - Python
    - Pandas
    - GeoPandas
    - Plotly
    - Streamlit
    - SciPy
    - scikit-learn
    - statsmodels
    - River
    - MongoDB Atlas
    - Apache Spark
    - Cassandra
    """
)