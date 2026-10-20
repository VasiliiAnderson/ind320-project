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

# Get available connections from MongoDB
connections = get_connections()

if not connections:
    st.warning(
        "No ENTSO-E data are available in MongoDB."
    )
    st.stop()


# Create the two-column layout required by the assignment
left_col, right_col = st.columns(2)


# ---------------------------------------------------------
# Left column: annual import/export pie chart
# ---------------------------------------------------------
with left_col:
    st.subheader("Annual Import and Export")

    selected_connection = st.radio(
        "Select connection",
        options=connections,
    )

    years = get_years(selected_connection)

    selected_year = st.selectbox(
        "Select year",
        options=years,
        index=len(years) - 1,
    )

    annual_totals = get_annual_totals(
        selected_connection,
        selected_year,
    )

    if not annual_totals.empty:
        # Convert MWh to GWh for easier interpretation
        annual_totals["total_gwh"] = (
            annual_totals["total_mwh"] / 1000
        )

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
        monthly_flow = get_monthly_flow(
            selected_connection,
            selected_year,
            selected_months,
        )

        if not monthly_flow.empty:
            fig, ax = plt.subplots(
                figsize=(9, 6)
            )

            # Use one fixed colour for each direction
            directions = monthly_flow[
                "direction"
            ].unique()

            direction_colors = {
                direction: f"C{index}"
                for index, direction in enumerate(
                    directions
                )
            }

            # Plot each selected month separately so
            # unselected months appear as gaps.
            for direction in directions:
                direction_data = monthly_flow[
                    monthly_flow[
                        "direction"
                    ] == direction
                ]

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