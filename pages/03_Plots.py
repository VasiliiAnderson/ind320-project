import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from modules.data_loader import load_data


st.title("Reservoir Plots")

# Load the reservoir dataset
df = load_data()

st.write(
    "Select a data column and a range of months to explore the reservoir data."
)

# Use national observations for reservoir time-series measurements
national_data = (
    df[
        (df["area_type"] == "NO")
        & (df["area_number"] == 0)
    ]
    .sort_values("date")
    .copy()
)

# Create a month variable for the month slider
national_data["month"] = (
    national_data["date"]
    .dt.to_period("M")
    .astype(str)
)

df["month"] = (
    df["date"]
    .dt.to_period("M")
    .astype(str)
)

# Available months in chronological order
month_options = (
    national_data["month"]
    .drop_duplicates()
    .tolist()
)

# Let the user select any imported data column or all measurements
selected_column = st.selectbox(
    "Select data column",
    options=["All"] + df.columns.drop("month").tolist(),
)

# Select the time period to display
# The first month is selected by default
selected_months = st.select_slider(
    "Select month range",
    options=month_options,
    value=(month_options[0], month_options[0]),
)

start_month, end_month = selected_months

# Filter national observations to the selected period
filtered_national = national_data[
    (national_data["month"] >= start_month)
    & (national_data["month"] <= end_month)
]

# Filter the complete dataset to the selected period
filtered_df = df[
    (df["month"] >= start_month)
    & (df["month"] <= end_month)
]

# Reservoir measurement columns that can be selected individually
measurement_columns = [
    "fill_level",
    "capacity_twh",
    "stored_energy_twh",
    "previous_week_fill_level",
    "change_in_fill_level",
]

# Time-varying measurements used in the combined plot
# Capacity is excluded because national capacity is constant
combined_columns = [
    "fill_level",
    "stored_energy_twh",
    "previous_week_fill_level",
    "change_in_fill_level",
]

# Readable labels for reservoir measurements
plot_labels = {
    "fill_level": "Fill Level",
    "capacity_twh": "Capacity (TWh)",
    "stored_energy_twh": "Stored Energy (TWh)",
    "previous_week_fill_level": "Previous Week Fill Level",
    "change_in_fill_level": "Change in Fill Level",
}

# Create the figure
fig, ax = plt.subplots(figsize=(12, 6))


if selected_column == "All":

    # Normalise using the complete national time series so that the
    # scale remains consistent when the selected month range changes
    normalized_data = national_data[combined_columns].copy()

    for column in combined_columns:
        minimum = normalized_data[column].min()
        maximum = normalized_data[column].max()

        normalized_data[column] = (
            normalized_data[column] - minimum
        ) / (maximum - minimum)

    # Keep only values belonging to the selected period
    normalized_filtered = normalized_data.loc[
        filtered_national.index
    ]

    # Plot all time-varying measurements together
    for column in combined_columns:
        ax.plot(
            filtered_national["date"],
            normalized_filtered[column],
            label=plot_labels[column],
        )

    ax.set_title(
        "Normalised Reservoir Measurements – Norway"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel("Normalised Value (0–1)")
    ax.legend(loc="best")


elif selected_column in measurement_columns:

    # Plot a single national reservoir measurement over time
    ax.plot(
        filtered_national["date"],
        filtered_national[selected_column],
    )

    ax.set_title(
        f"{plot_labels[selected_column]} – Norway"
    )
    ax.set_xlabel("Date")
    ax.set_ylabel(plot_labels[selected_column])


elif selected_column == "date":

    # Show the number of observations recorded on each date
    counts = (
        filtered_df["date"]
        .value_counts()
        .sort_index()
    )

    ax.plot(
        counts.index,
        counts.values,
    )

    ax.set_title("Number of Observations by Date")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Observations")


elif selected_column == "next_publication_date":

    # Show frequencies of valid next-publication dates
    counts = (
        filtered_df["next_publication_date"]
        .dropna()
        .value_counts()
        .sort_index()
    )

    ax.plot(
        counts.index,
        counts.values,
    )

    ax.set_title("Next Publication Dates")
    ax.set_xlabel("Next Publication Date")
    ax.set_ylabel("Number of Observations")


else:

    # Identifier and categorical variables are more naturally shown
    # as frequency distributions than as time series
    counts = (
        filtered_df[selected_column]
        .value_counts()
        .sort_index()
    )

    ax.bar(
        counts.index.astype(str),
        counts.values,
    )

    readable_name = (
        selected_column
        .replace("_", " ")
        .title()
    )

    ax.set_title(
        f"Number of Observations by {readable_name}"
    )
    ax.set_xlabel(readable_name)
    ax.set_ylabel("Number of Observations")


# Apply common formatting to all plots
ax.grid(alpha=0.3)
fig.tight_layout()

st.caption(
    f"Showing data from {start_month} to {end_month}. "
    "Reservoir measurements use national observations (NO, area 0)."
)

st.pyplot(fig)