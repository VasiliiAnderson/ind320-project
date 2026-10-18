import streamlit as st

from modules.data_loader import load_data


st.title("Reservoir Data")

# Load reservoir statistics directly from the NVE API
df = load_data()

st.write(
    "Explore Norwegian reservoir statistics retrieved directly "
    "from the NVE Magasinstatistikk API."
)

# Select geographical area type
selected_area_type = st.radio(
    "Select area type",
    options=["EL", "NO", "VASS"],
    horizontal=True,
)

# Keep observations belonging to the selected area type
area_data = (
    df[df["area_type"] == selected_area_type]
    .sort_values(["area_number", "date"])
    .copy()
)

# Find the area numbers associated with the selected area type
area_numbers = sorted(
    area_data["area_number"]
    .dropna()
    .unique()
    .tolist()
)

st.caption(
    f"Available area numbers for {selected_area_type}: "
    + ", ".join(map(str, area_numbers))
)

# Create a month variable for interval selection
area_data["month"] = (
    area_data["date"]
    .dt.to_period("M")
    .astype(str)
)

# Available months in chronological order
month_options = (
    area_data["month"]
    .drop_duplicates()
    .sort_values()
    .tolist()
)

# Use approximately the most recent 12 months as the default interval
default_start_index = max(0, len(month_options) - 12)

selected_months = st.select_slider(
    "Select data interval",
    options=month_options,
    value=(
        month_options[default_start_index],
        month_options[-1],
    ),
)

start_month, end_month = selected_months

# Filter observations to the selected time interval
filtered_data = area_data[
    (area_data["month"] >= start_month)
    & (area_data["month"] <= end_month)
].copy()

st.caption(
    f"Showing data from {start_month} to {end_month}."
)

# Columns shown in the main data table
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

st.subheader("Reservoir Observations")

st.dataframe(
    filtered_data[display_columns],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Area Overview")

st.write(
    "Each row represents an area belonging to the selected area type. "
    "The sparklines show reservoir development during the selected period."
)

# Create one row for each area number
overview_rows = []

for area_number in area_numbers:
    area_period = (
        filtered_data[
            filtered_data["area_number"] == area_number
        ]
        .sort_values("date")
    )

    overview_rows.append(
        {
            "Area Number": area_number,
            "Fill Level": (
                area_period["fill_level"]
                .dropna()
                .astype(float)
                .tolist()
            ),
            "Stored Energy (TWh)": (
                area_period["stored_energy_twh"]
                .dropna()
                .astype(float)
                .tolist()
            ),
        }
    )

# Display sparklines for each area
st.dataframe(
    overview_rows,
    column_config={
        "Area Number": st.column_config.NumberColumn(
            "Area Number"
        ),
        "Fill Level": st.column_config.LineChartColumn(
            "Fill Level"
        ),
        "Stored Energy (TWh)": st.column_config.LineChartColumn(
            "Stored Energy (TWh)"
        ),
    },
    hide_index=True,
    use_container_width=True,
)