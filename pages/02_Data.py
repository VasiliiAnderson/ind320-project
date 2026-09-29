import pandas as pd
import streamlit as st

from modules.data_loader import load_data


st.title("Reservoir Data")

# Load the reservoir dataset
df = load_data()

st.write(
    "The table below shows the imported Norwegian reservoir dataset."
)

st.dataframe(
    df,
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

# Create one row for every column in the imported dataset
overview_rows = []

for column in df.columns:

    # LineChartColumn can only visualise numerical values
    if pd.api.types.is_numeric_dtype(first_month[column]):
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
    "For numerical columns, the sparkline shows observations from "
    "the first month of the national time series."
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
    "dataset. Numerical columns are visualised directly, while categorical "
    "and datetime columns are listed without a sparkline."
)