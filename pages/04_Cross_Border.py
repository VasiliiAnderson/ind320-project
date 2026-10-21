import calendar

import matplotlib.pyplot as plt
import streamlit as st

from modules.mongodb_loader import (
    get_annual_totals,
    get_connections,
    get_monthly_flow,
    get_years,
)


st.title("Cross-Border Electricity Flows")

st.write(
    "Explore physical electricity flows between Norwegian "
    "bidding zones and neighbouring countries using data "
    "from the ENTSO-E Transparency Platform."
)

# Retrieve all cross-border connections currently stored
# in the MongoDB collection.
connections = get_connections()

# Stop the page gracefully if the database does not contain data.
if not connections:
    st.warning(
        "No ENTSO-E data are available in MongoDB."
    )
    st.stop()


# Split the dashboard into two columns:
# annual statistics on the left and monthly flows on the right.
left_col, right_col = st.columns(2)


# ---------------------------------------------------------
# Left column: annual import/export pie chart
# ---------------------------------------------------------
with left_col:
    st.subheader("Annual Import and Export")

    # Let the user choose which Norwegian cross-border
    # connection should be analysed.
    selected_connection = st.radio(
        "Select connection",
        options=connections,
    )

    # Retrieve the years available for the selected connection.
    years = get_years(
        selected_connection
    )

    selected_year = st.selectbox(
        "Select year",
        options=years,
        index=len(years) - 1,
    )

    # Aggregate annual transferred energy by direction
    # directly in MongoDB.
    annual_totals = get_annual_totals(
        selected_connection,
        selected_year,
    )

    if not annual_totals.empty:
        # Convert MWh to GWh so the values in the chart
        # are easier to interpret.
        annual_totals["total_gwh"] = (
            annual_totals["total_mwh"] / 1000
        )

        # Include both direction and transferred energy
        # in the pie-chart labels.
        labels = [
            (
                f"{row.direction} "
                f"({row.total_gwh:,.0f} GWh)"
            )
            for row in annual_totals.itertuples()
        ]

        fig, ax = plt.subplots(
            figsize=(6, 6)
        )

        # Show the relative annual shares of import and export.
        ax.pie(
            annual_totals["total_mwh"],
            labels=labels,
            autopct="%1.1f%%",
        )

        ax.set_title(
            f"{selected_connection} – "
            f"{selected_year}"
        )

        st.pyplot(fig)

    else:
        st.info(
            "No annual data are available "
            "for the selected connection and year."
        )


# ---------------------------------------------------------
# Right column: monthly physical-flow line plot
# ---------------------------------------------------------
with right_col:
    st.subheader("Monthly Physical Flow")

    # Allow several months to be selected simultaneously.
    selected_months = st.pills(
        "Select months",
        options=list(range(1, 13)),
        default=[1],
        selection_mode="multi",
        format_func=lambda month: (
            calendar.month_abbr[month]
        ),
    )

    if selected_months:
        # Use the same selected connection and year as the
        # annual chart, but retrieve only the chosen months.
        monthly_flow = get_monthly_flow(
            selected_connection,
            selected_year,
            selected_months,
        )

        if not monthly_flow.empty:
            fig, ax = plt.subplots(
                figsize=(9, 6)
            )

            # Find the available flow directions, normally
            # Import and Export.
            directions = monthly_flow[
                "direction"
            ].unique()

            # Assign one consistent colour to each direction
            # so Import and Export keep the same colours
            # across all selected months.
            direction_colors = {
                direction: f"C{index}"
                for index, direction in enumerate(
                    directions
                )
            }

            # Each month is plotted as a separate segment.
            # This prevents Matplotlib from drawing a line
            # across months that were not selected.
            for direction in directions:
                direction_data = monthly_flow[
                    monthly_flow[
                        "direction"
                    ] == direction
                ]

                # Only the first segment for each direction
                # receives a label, preventing duplicate
                # Import/Export entries in the legend.
                first_segment = True

                for month in selected_months:
                    month_data = (
                        direction_data[
                            direction_data[
                                "timestamp_utc"
                            ].dt.month == month
                        ]
                        .sort_values(
                            "timestamp_utc"
                        )
                    )

                    if not month_data.empty:
                        ax.plot(
                            month_data[
                                "timestamp_utc"
                            ],
                            month_data[
                                "quantity_mw"
                            ],
                            label=(
                                direction
                                if first_segment
                                else None
                            ),
                            color=(
                                direction_colors[
                                    direction
                                ]
                            ),
                        )

                        first_segment = False

            # Add descriptive labels and basic formatting.
            ax.set_title(
                f"{selected_connection} – "
                f"{selected_year}"
            )

            ax.set_xlabel(
                "Timestamp (UTC)"
            )

            ax.set_ylabel(
                "Physical Flow (MW)"
            )

            ax.legend(
                title="Direction"
            )

            ax.grid(
                alpha=0.3
            )

            fig.tight_layout()

            st.pyplot(fig)

        else:
            st.info(
                "No observations are available "
                "for the selected months."
            )

    else:
        st.info(
            "Select at least one month."
        )


# ---------------------------------------------------------
# Data-source documentation
# ---------------------------------------------------------
# Keep the processing description available without taking
# permanent space in the main dashboard layout.
with st.expander(
    "About the data and processing"
):
    st.write(
        """
        Cross-border physical flow data are retrieved from
        the ENTSO-E Transparency Platform API.

        Data for the latest two-year period are first stored
        in Cassandra. Spark is then used to read, filter and
        prepare the data before the curated dataset is stored
        in MongoDB Atlas.

        This Streamlit page reads the prepared data directly
        from MongoDB.
        """
    )