import pandas as pd
import requests
import streamlit as st


# Public endpoint containing the reservoir statistics
# used by the Streamlit application.
NVE_DATA_URL = (
    "https://biapi.nve.no/magasinstatistikk/"
    "api/Magasinstatistikk/HentOffentligData"
)


@st.cache_data(ttl=3600)
def load_data():
    """
    Retrieve and prepare Norwegian reservoir statistics.

    Data are downloaded directly from the NVE Magasinstatistikk
    API. The result is cached for one hour to avoid unnecessary
    API requests whenever Streamlit reruns the application.
    """

    # Retrieve the latest publicly available reservoir data.
    response = requests.get(
        NVE_DATA_URL,
        timeout=30,
    )

    # Stop execution if the API returns an unsuccessful status code.
    response.raise_for_status()

    # Convert the JSON response into a Pandas DataFrame.
    df = pd.DataFrame(
        response.json()
    )

    # Rename the original NVE variables to descriptive English
    # names used consistently throughout the project.
    df = df.rename(
        columns={
            "dato_Id": "date",
            "omrType": "area_type",
            "omrnr": "area_number",
            "iso_aar": "iso_year",
            "iso_uke": "iso_week",
            "fyllingsgrad": "fill_level",
            "kapasitet_TWh": "capacity_twh",
            "fylling_TWh": "stored_energy_twh",
            "neste_Publiseringsdato": "next_publication_date",
            "fyllingsgrad_forrige_uke": "previous_week_fill_level",
            "endring_fyllingsgrad": "change_in_fill_level",
        }
    )

    # Convert the observation date to a Pandas datetime type.
    df["date"] = pd.to_datetime(
        df["date"]
    )

    # NVE uses 0001-01-01 as a placeholder when no next
    # publication date is available. Replace it with a missing value.
    df["next_publication_date"] = df[
        "next_publication_date"
    ].replace(
        "0001-01-01T00:00:00",
        pd.NA,
    )

    # Convert valid publication dates to datetime values.
    # Missing or invalid values are converted to NaT.
    df["next_publication_date"] = pd.to_datetime(
        df["next_publication_date"],
        errors="coerce",
    )

    # Sort the observations consistently by date and area
    # before returning the prepared dataset to Streamlit.
    df = (
        df
        .sort_values(
            [
                "date",
                "area_type",
                "area_number",
            ]
        )
        .reset_index(drop=True)
    )

    return df