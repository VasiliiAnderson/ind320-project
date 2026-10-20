import streamlit as st


st.title("About the Project")

st.write(
    """
    This application was developed as part of the first compulsory assignment
    in IND320 – Data to Decision at NMBU.
    """
)

st.subheader("Purpose")

st.write(
    """
    The purpose of the application is to explore Norwegian reservoir data
    through an interactive Streamlit dashboard. The app allows users to inspect
    the underlying dataset and visualise selected variables over time.
    """
)

st.subheader("Data")

st.write(
    """
    The application currently reads the reservoir data from a local CSV file.
    The dataset contains information about reservoir fill levels, storage
    capacity, stored energy, geographical areas and time-related variables.
    """
)

st.subheader("Application Structure")

st.write(
    """
    The application contains four pages:

    - **Home** – introduction and navigation
    - **Data** – overview of the imported dataset and first-month sparklines
    - **Plots** – interactive visualisation of selected variables
    - **About** – information about the project
    """
)

st.subheader("Technology")

st.write(
    """
    The project uses Python, Pandas, Matplotlib and Streamlit.
    Data loading is cached using Streamlit to improve application performance.
    """
)