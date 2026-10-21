import streamlit as st


st.title("IND320 Energy Dashboard")

st.write(
    """
    This application was developed as part of IND320 – Data to Decision
    at NMBU. It combines Norwegian reservoir statistics from the NVE
    Magasinstatistikk API with cross-border electricity flow data from
    the ENTSO-E Transparency Platform.
    """
)

st.subheader("Navigation")

st.write(
    """
    Use the sidebar to navigate between:

    - **Home** – introduction to the application
    - **Reservoir Data** – explore reservoir statistics retrieved from the NVE API
    - **Reservoir Plots** – visualise reservoir measurements across areas and time periods
    - **Cross-Border Flows** – analyse electricity imports and exports using ENTSO-E data stored in MongoDB
    - **About** – information about the project, data sources and technology
    """
)

st.subheader("Data Sources")

st.write(
    """
    Reservoir statistics are retrieved directly from the
    **NVE Magasinstatistikk API**.

    Cross-border physical flow data are retrieved from the
    **ENTSO-E Transparency Platform API**, processed using
    Cassandra and Spark, and stored in MongoDB Atlas for use
    in the Streamlit application.
    """
)