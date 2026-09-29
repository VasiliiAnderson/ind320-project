from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    data_path = Path("data/reservoirs.csv")

    df = pd.read_csv(data_path)

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

    df["date"] = pd.to_datetime(df["date"])

    df["next_publication_date"] = df["next_publication_date"].replace(
        "0001-01-01T00:00:00",
        pd.NA,
    )

    df["next_publication_date"] = pd.to_datetime(
        df["next_publication_date"],
        errors="coerce",
    )

    # Sort observations chronologically and by geographical area
    df = (
        df
        .sort_values(["date", "area_type", "area_number"])
        .reset_index(drop=True)
    )

    return df