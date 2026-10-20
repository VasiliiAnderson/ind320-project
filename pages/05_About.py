import streamlit as st


st.title("About the Project")

st.write(
    """
    This application was developed as part of the second compulsory
    assignment in IND320 – Data to Decision at NMBU.

    The project combines Norwegian reservoir statistics with
    cross-border electricity flow data in an interactive Streamlit
    dashboard.
    """
)

st.subheader("Purpose")

st.write(
    """
    The purpose of the application is to demonstrate a complete
    data pipeline from external APIs to local and remote databases,
    data processing with Spark, and interactive visualisation in
    Streamlit.

    The dashboard allows users to explore both Norwegian reservoir
    conditions and physical electricity flows between Norwegian
    bidding zones and neighbouring countries.
    """
)

st.subheader("Data Sources")

st.write(
    """
    The project uses two main data sources:

    - **NVE Magasinstatistikk API** – Norwegian reservoir statistics,
      including fill levels, storage capacity and stored energy.
    - **ENTSO-E Transparency Platform API** – physical cross-border
      electricity flow data between Norwegian bidding zones and
      neighbouring countries.
    """
)

st.subheader("Data Processing")

st.write(
    """
    Reservoir statistics are retrieved directly from the NVE API
    when the Streamlit application is used.

    Cross-border electricity data follow a larger processing pipeline:

    **ENTSO-E API → Cassandra → Spark → MongoDB Atlas → Streamlit**

    ENTSO-E data for the latest two-year period are first retrieved
    through the API and stored locally in Cassandra. Spark is used to
    read, clean and prepare the data. The processed dataset is then
    stored in MongoDB Atlas, which is used as the data source for the
    cross-border Streamlit page.
    """
)

st.subheader("Application Structure")

st.write(
    """
    The application contains five pages:

    - **Home** – introduction and navigation
    - **Reservoir Data** – reservoir observations and sparklines
    - **Reservoir Plots** – interactive reservoir visualisations
    - **Cross-Border Flows** – import and export analysis based on
      ENTSO-E data stored in MongoDB
    - **About** – information about the project, data sources and
      processing pipeline
    """
)

st.subheader("Technology")

st.write(
    """
    The project uses Python together with Pandas, Matplotlib and
    Streamlit for data preparation and visualisation.

    Apache Spark is used for distributed data processing, Cassandra
    is used as the local database for ENTSO-E data, and MongoDB Atlas
    is used as the remote database accessed by the Streamlit
    application.

    Cassandra is run locally using Docker, while sensitive
    credentials such as the ENTSO-E API token and MongoDB connection
    string are stored outside the GitHub repository.
    """
)