import streamlit as st

st.title("Norwegian Reservoir Dashboard")

st.write(
    """
    This application explores Norwegian reservoir data and was developed
    as part of the IND320 Data to Decision course at NMBU.
    """
)

st.subheader("Navigation")

st.write(
    """
    Use the sidebar to navigate between:

    - **Home** – introduction to the application
    - **Data** – explore the reservoir dataset
    - **Plots** – interactively visualise reservoir measurements
    - **About** – information about the project
    """
)