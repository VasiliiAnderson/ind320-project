import calendar

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from modules.currency_loader import (
    download_exchange_rates,
)
from modules.mongodb_loader import (
    get_annual_totals,
    get_connections,
    get_monthly_flow,
    get_years,
)


st.title("Energy & Markets")

st.write(
    "Explore Norwegian cross-border electricity flows "
    "and NOK exchange rates using data from ENTSO-E "
    "and Norges Bank."
)


# =========================================================
# ENTSO-E CROSS-BORDER FLOWS
# =========================================================

st.header("Cross-Border Electricity Flows")

st.write(
    "Explore physical electricity flows between Norwegian "
    "bidding zones and neighbouring countries."
)


# ---------------------------------------------------------
# Retrieve available connections
# ---------------------------------------------------------

try:
    connections = get_connections()

except Exception as exc:
    st.error(
        "Could not connect to the ENTSO-E MongoDB dataset."
    )
    st.code(str(exc))
    st.stop()


if not connections:
    st.warning(
        "No ENTSO-E data are currently available."
    )
    st.stop()


# ---------------------------------------------------------
# Main controls
# ---------------------------------------------------------

control_col1, control_col2 = st.columns(2)


with control_col1:

    selected_connection = st.selectbox(
        "Connection",
        options=connections,
    )


years = get_years(
    selected_connection
)


if not years:
    st.warning(
        "No years are available for this connection."
    )
    st.stop()


with control_col2:

    selected_year = st.selectbox(
        "Year",
        options=years,
        index=len(years) - 1,
    )


# =========================================================
# Annual import / export
# =========================================================

annual_totals = get_annual_totals(
    selected_connection,
    selected_year,
)


if not annual_totals.empty:

    annual_totals = (
        annual_totals.copy()
    )

    annual_totals[
        "total_gwh"
    ] = (
        annual_totals[
            "total_mwh"
        ]
        / 1000
    )


# =========================================================
# Monthly flow controls
# =========================================================

selected_months = st.pills(
    "Months",
    options=list(
        range(1, 13)
    ),
    default=list(
        range(1, 13)
    ),
    selection_mode="multi",
    format_func=lambda month: (
        calendar.month_abbr[
            month
        ]
    ),
)


# ---------------------------------------------------------
# Dashboard columns
# ---------------------------------------------------------

left_col, right_col = (
    st.columns(2)
)


# ---------------------------------------------------------
# Annual import/export chart
# ---------------------------------------------------------

with left_col:

    st.subheader(
        "Annual Import and Export"
    )

    if annual_totals.empty:

        st.info(
            "No annual data are available "
            "for the selected connection."
        )

    else:

        pie_fig = px.pie(
            annual_totals,
            values="total_gwh",
            names="direction",
            hole=0.4,
            title=(
                f"{selected_connection} – "
                f"{selected_year}"
            ),
        )

        pie_fig.update_traces(
            textposition="inside",
            textinfo=(
                "percent+label"
            ),
            hovertemplate=(
                "%{label}<br>"
                "%{value:,.0f} GWh"
                "<br>%{percent}"
                "<extra></extra>"
            ),
        )

        pie_fig.update_layout(
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
            legend_title_text=(
                "Direction"
            ),
        )

        st.plotly_chart(
            pie_fig,
            width="stretch",
        )


# ---------------------------------------------------------
# Physical-flow chart
# ---------------------------------------------------------

with right_col:

    st.subheader(
        "Physical Flow"
    )

    if not selected_months:

        st.info(
            "Select at least one month."
        )

    else:

        monthly_flow = (
            get_monthly_flow(
                selected_connection,
                selected_year,
                selected_months,
            )
        )

        if monthly_flow.empty:

            st.info(
                "No observations are available "
                "for the selected months."
            )

        else:

            # Aggregate the high-frequency ENTSO-E
            # observations to daily mean values.
            # This makes longer periods easier to read
            # while preserving the overall flow pattern.
            daily_flow = (
                monthly_flow
                .set_index(
                    "timestamp_utc"
                )
                .groupby(
                    "direction"
                )[
                    "quantity_mw"
                ]
                .resample("D")
                .mean()
                .reset_index()
            )


            flow_fig = px.line(
                daily_flow,
                x="timestamp_utc",
                y="quantity_mw",
                color="direction",
                labels={
                    "timestamp_utc": (
                        "Date (UTC)"
                    ),
                    "quantity_mw": (
                        "Daily Average "
                        "Physical Flow (MW)"
                    ),
                    "direction": (
                        "Direction"
                    ),
                },
                title=(
                    f"{selected_connection} – "
                    f"{selected_year}"
                ),
            )


            flow_fig.update_layout(
                hovermode="x unified",
                margin=dict(
                    l=20,
                    r=20,
                    t=60,
                    b=20,
                ),
                legend_title_text=(
                    "Direction"
                ),
            )


            flow_fig.update_traces(
                hovertemplate=(
                    "%{x|%Y-%m-%d}"
                    "<br>"
                    "%{y:,.0f} MW"
                    "<extra></extra>"
                ),
            )


            st.plotly_chart(
                flow_fig,
                width="stretch",
            )


            st.caption(
                "High-frequency ENTSO-E observations "
                "are aggregated to daily mean values "
                "for clearer visualisation."
            )


# =========================================================
# Annual KPIs
# =========================================================

if not annual_totals.empty:

    st.subheader(
        "Annual Flow Summary"
    )

    metric_columns = (
        st.columns(
            len(annual_totals)
        )
    )

    for column, row in zip(
        metric_columns,
        annual_totals.itertuples(),
    ):

        column.metric(
            row.direction,
            (
                f"{row.total_gwh:,.0f} "
                "GWh"
            ),
        )


# =========================================================
# NOK EXCHANGE RATES
# =========================================================

st.divider()

st.header(
    "Exchange Rates"
)

st.write(
    "Daily EUR/NOK and USD/NOK spot exchange rates "
    "from Norges Bank."
)


# ---------------------------------------------------------
# Currency period
# ---------------------------------------------------------

currency_start_date = (
    f"{selected_year}-01-01"
)

currency_end_date = (
    f"{selected_year}-12-31"
)


try:

    exchange_rates = (
        download_exchange_rates(
            currencies=(
                "EUR",
                "USD",
            ),
            start_date=(
                currency_start_date
            ),
            end_date=(
                currency_end_date
            ),
        )
    )

except (
    requests.exceptions.RequestException,
    ValueError,
) as exc:

    st.error(
        "Exchange rates could not be "
        "retrieved from Norges Bank."
    )

    st.code(
        str(exc)
    )

    exchange_rates = (
        pd.DataFrame()
    )


# ---------------------------------------------------------
# Currency visualisation
# ---------------------------------------------------------

if not exchange_rates.empty:

    currency_fig = px.line(
        exchange_rates,
        x="date",
        y="exchange_rate",
        color="currency",
        labels={
            "date": "Date",
            "exchange_rate": (
                "NOK per unit"
            ),
            "currency": (
                "Currency"
            ),
        },
        title=(
            f"EUR/NOK and USD/NOK – "
            f"{selected_year}"
        ),
    )


    currency_fig.update_layout(
        hovermode="x unified",
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
        legend_title_text=(
            "Currency"
        ),
    )


    st.plotly_chart(
        currency_fig,
        width="stretch",
    )


    # -----------------------------------------------------
    # Latest exchange-rate KPIs
    # -----------------------------------------------------

    latest_rates = (
        exchange_rates
        .sort_values("date")
        .groupby(
            "currency",
            as_index=False,
        )
        .last()
    )


    eur_data = (
        latest_rates[
            latest_rates[
                "currency"
            ]
            == "EUR"
        ]
    )

    usd_data = (
        latest_rates[
            latest_rates[
                "currency"
            ]
            == "USD"
        ]
    )


    eur_col, usd_col = (
        st.columns(2)
    )


    if not eur_data.empty:

        eur_rate = (
            eur_data[
                "exchange_rate"
            ].iloc[0]
        )

        eur_date = (
            eur_data[
                "date"
            ].iloc[0]
        )

        eur_col.metric(
            "EUR/NOK",
            f"{eur_rate:.3f}",
            help=(
                "Latest available rate "
                f"in {selected_year}: "
                f"{eur_date:%Y-%m-%d}"
            ),
        )


    if not usd_data.empty:

        usd_rate = (
            usd_data[
                "exchange_rate"
            ].iloc[0]
        )

        usd_date = (
            usd_data[
                "date"
            ].iloc[0]
        )

        usd_col.metric(
            "USD/NOK",
            f"{usd_rate:.3f}",
            help=(
                "Latest available rate "
                f"in {selected_year}: "
                f"{usd_date:%Y-%m-%d}"
            ),
        )


# =========================================================
# Data documentation
# =========================================================

with st.expander(
    "About the data and processing"
):

    st.markdown(
        """
        **ENTSO-E**

        Cross-border physical-flow data originate from the
        ENTSO-E Transparency Platform. The prepared observations
        are stored in MongoDB and retrieved dynamically by the
        Streamlit application.

        Timestamps are parsed explicitly as UTC to avoid
        ambiguity related to daylight-saving time.

        The original ENTSO-E observations have a high temporal
        resolution. For the physical-flow visualisation, these
        observations are aggregated to daily mean values to make
        longer time periods easier to interpret.

        **Norges Bank**

        EUR/NOK and USD/NOK spot exchange rates are downloaded
        directly from the Norges Bank exchange-rate API.
        Exchange-rate observations are daily and therefore
        treated as calendar-date observations rather than
        timezone-dependent hourly observations.

        Both data sources are cached to reduce unnecessary
        requests and improve dashboard performance.
        """
    )