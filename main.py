import streamlit as st

st.set_page_config(
    page_title="IND320 Energy Dashboard",
    page_icon="💧",
    layout="wide",
)

pages = [
    st.Page(
        "pages/01_Home.py",
        title="Home",
        icon="🏠",
        default=True,
    ),
    st.Page(
        "pages/02_Data.py",
        title="Reservoir Data",
        icon="📊",
    ),
    st.Page(
        "pages/03_Plots.py",
        title="Reservoir Plots",
        icon="📈",
    ),
    st.Page(
        "pages/05_Seasonal_Analysis.py",
        title="Seasonal Analysis",
        icon="🔄",
    ),
    st.Page(
        "pages/06_Weather_Analysis.py",
        title="Weather Analysis",
        icon="🌦️",
    ),
    st.Page(
        "pages/07_About.py",
        title="About",
        icon="ℹ️",
    ),
    st.Page(
        "pages/04_Cross_Border.py",
        title="Cross-Border Flows",
        icon="⚡",
    ),
]

navigation = st.navigation(pages)
navigation.run()