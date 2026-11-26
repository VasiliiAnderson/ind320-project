import streamlit as st


st.set_page_config(
    page_title="IND320 Energy Dashboard",
    page_icon="💧",
    layout="wide",
)


pages = {
    "": [
        st.Page(
            "pages/01_Home.py",
            title="Home",
            icon="🏠",
            default=True,
        ),
    ],

    "Explore": [
        st.Page(
            "pages/02_Map_Overview.py",
            title="Map & Data Overview",
            icon="🗺️",
        ),
        st.Page(
            "pages/04_Cross_Border.py",
            title="Energy & Markets",
            icon="⚡",
        ),
    ],

    "Analyse": [
        st.Page(
            "pages/05_Seasonal_Analysis.py",
            title="Seasonal Patterns",
            icon="🔄",
        ),
        st.Page(
            "pages/06_Weather_Analysis.py",
            title="Weather & Anomalies",
            icon="🌦️",
        ),
        st.Page(
            "pages/06_Correlation.py",
            title="Weather–Reservoir Correlation",
            icon="📊",
        ),
    ],

    "Predict": [
        st.Page(
            "pages/07_Forecast.py",
            title="Reservoir Forecast",
            icon="🔮",
        ),
    ],

    "Information": [
        st.Page(
            "pages/07_About.py",
            title="About",
            icon="ℹ️",
        ),
    ],
}


navigation = st.navigation(pages)
navigation.run()