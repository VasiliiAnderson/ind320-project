import pandas as pd
import streamlit as st

from modules.data_loader import load_data


st.title("Reservoir Data")

# Load the reservoir dataset
df = load_data()

st.write(
    "The table below shows the most relevant variables from the "
    "Norwegian reservoir dataset."
)

# Select relevant columns for the main table
display_columns = [
    "date",
    "area_type",
    "area_number",
    "iso_year",
    "iso_week",
    "fill_level",
    "capacity_twh",
    "stored_energy_twh",
    "previous_week_fill_level",
    "change_in_fill_level",
]

st.dataframe(
    df[display_columns],
    use_container_width=True,
    hide_index=True,
)

st.subheader("First Month Overview")

# Use national observations to obtain one coherent time series
national_data = (
    df[
        (df["area_type"] == "NO")
        & (df["area_number"] == 0)
    ]
    .sort_values("date")
)

# Select observations from the first month in the dataset
first_date = national_data["date"].min()
first_month_end = first_date + pd.DateOffset(months=1)

first_month = national_data[
    (national_data["date"] >= first_date)
    & (national_data["date"] < first_month_end)
]

# Reservoir measurement variables that are meaningful as sparklines
sparkline_columns = [
    "fill_level",
    "capacity_twh",
    "stored_energy_twh",
    "previous_week_fill_level",
    "change_in_fill_level",
]

# Create one row for every column in the imported dataset
overview_rows = []

for column in df.columns:

    # Only reservoir measurements are visualised as sparklines
    if column in sparkline_columns:
        values = (
            first_month[column]
            .dropna()
            .astype(float)
            .tolist()
        )
    else:
        values = []

    overview_rows.append(
        {
            "Column": column,
            "Data Type": str(df[column].dtype),
            "First Month": values,
        }
    )

overview_df = pd.DataFrame(overview_rows)

st.write(
    "Each row represents one column in the imported dataset. "
    "For reservoir measurement variables, the sparkline shows "
    "national observations from the first month of the time series."
)

# Display one row per imported column with a sparkline where applicable
st.dataframe(
    overview_df,
    column_config={
        "Column": st.column_config.TextColumn(
            "Data Column"
        ),
        "Data Type": st.column_config.TextColumn(
            "Data Type"
        ),
        "First Month": st.column_config.LineChartColumn(
            "First Month"
        ),
    },
    hide_index=True,
    use_container_width=True,
    height=430,
)

st.caption(
    "Sparklines show national observations from the first month of the "
    "dataset for reservoir measurement variables. Identifier, categorical "
    "and datetime columns are listed without a sparkline."
)