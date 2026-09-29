import streamlit as st

st.set_page_config(
    page_title="IND320 Reservoir Dashboard",
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
        title="Data",
        icon="📊",
    ),
    st.Page(
        "pages/03_Plots.py",
        title="Plots",
        icon="📈",
    ),
    st.Page(
        "pages/04_About.py",
        title="About",
        icon="ℹ️",
    ),
]

navigation = st.navigation(pages)
navigation.run()