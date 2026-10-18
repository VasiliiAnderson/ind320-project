import matplotlib.pyplot as plt
import streamlit as st

from modules.data_loader import load_data


st.title("Reservoir Plots")

# Load reservoir statistics directly from the NVE API
df = load_data()

st.write(
    "Compare reservoir measurements across geographical areas "
    "using data retrieved directly from the NVE Magasinstatistikk API."
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

# Find area numbers associated with the selected area type
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

# Create month variable for interval selection
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

# Use approximately the most recent 12 months as default
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

# Filter observations to selected time interval
filtered_data = area_data[
    (area_data["month"] >= start_month)
    & (area_data["month"] <= end_month)
].copy()

# Reservoir measurements available for plotting
measurement_columns = {
    "Fill Level": "fill_level",
    "Capacity (TWh)": "capacity_twh",
    "Stored Energy (TWh)": "stored_energy_twh",
    "Previous Week Fill Level": "previous_week_fill_level",
    "Change in Fill Level": "change_in_fill_level",
}

selected_measurement_label = st.selectbox(
    "Select reservoir measurement",
    options=list(measurement_columns.keys()),
)

selected_measurement = measurement_columns[
    selected_measurement_label
]

# Create plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot one line for each area number
for area_number in area_numbers:
    area_period = (
        filtered_data[
            filtered_data["area_number"] == area_number
        ]
        .sort_values("date")
    )

    if not area_period.empty:
        ax.plot(
            area_period["date"],
            area_period[selected_measurement],
            label=f"Area {area_number}",
        )

ax.set_title(
    f"{selected_measurement_label} – {selected_area_type}"
)
ax.set_xlabel("Date")
ax.set_ylabel(selected_measurement_label)
ax.grid(alpha=0.3)

# Only show legend when there are areas to display
if area_numbers:
    ax.legend(
        title="Area Number",
        loc="best",
    )

fig.tight_layout()

st.pyplot(fig)

st.caption(
    f"Showing {selected_measurement_label.lower()} "
    f"for {selected_area_type} areas from "
    f"{start_month} to {end_month}."
)