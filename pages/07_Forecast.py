import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from modules.area_selector import (
    area_selector,
)
from modules.data_loader import (
    load_data,
)
from modules.forecasting import (
    CURRENCY_FEATURES,
    WEATHER_FEATURES,
    forecast_future_snarimax,
    prepare_forecast_data,
)
from modules.weather_analysis import (
    latest_era5_date,
)


st.title(
    "Reservoir Forecast"
)

st.write(
    "Forecast future monthly reservoir filling levels "
    "using River SNARIMAX with selectable model parameters "
    "and exogenous variables."
)


# ---------------------------------------------------------
# Load data and geographical selection
# ---------------------------------------------------------

df = load_data()


selected_area_type, selected_area = (
    area_selector(df)
)


st.caption(
    f"Forecasting {selected_area_type} area "
    f"{selected_area}."
)


# ---------------------------------------------------------
# Available reservoir months
# ---------------------------------------------------------

area_data = (
    df[
        (
            df["area_type"]
            == selected_area_type
        )
        & (
            df["area_number"]
            == selected_area
        )
    ]
    .sort_values("date")
    .copy()
)


available_months = (
    area_data[
        "date"
    ]
    .dt.to_period("M")
    .drop_duplicates()
    .sort_values()
    .astype(str)
    .tolist()
)


# ---------------------------------------------------------
# Sync with map timeframe
# ---------------------------------------------------------

map_end_month = (
    st.session_state.get(
        "selected_end_month"
    )
)


sync_with_map = st.toggle(
    "Use Map & Data Overview end month",
    value=(
        map_end_month
        in available_months
    ),
    disabled=(
        map_end_month
        not in available_months
    ),
)


if sync_with_map:

    requested_end_month = (
        map_end_month
    )


    st.caption(
        f"Training end is synchronised with "
        f"the map: {requested_end_month}."
    )

else:

    requested_end_month = (
        st.selectbox(
            "Training end month",
            options=available_months,
            index=(
                len(
                    available_months
                )
                - 1
            ),
        )
    )


# ---------------------------------------------------------
# Main forecast controls
# ---------------------------------------------------------

col1, col2 = (
    st.columns(2)
)


with col1:

    history_years = st.slider(
        "Training history (years)",
        min_value=3,
        max_value=10,
        value=5,
        step=1,
    )


with col2:

    horizon_months = st.slider(
        "Forecast horizon (months)",
        min_value=1,
        max_value=12,
        value=6,
        step=1,
    )


# ---------------------------------------------------------
# Exogenous variables
# ---------------------------------------------------------

feature_options = {
    "Temperature": (
        "avg_temperature"
    ),
    "Precipitation": (
        "total_precipitation"
    ),
    "Snowfall": (
        "total_snowfall"
    ),
    "EUR/NOK": (
        "eur_nok"
    ),
    "USD/NOK": (
        "usd_nok"
    ),
}


selected_feature_labels = (
    st.multiselect(
        "Exogenous variables",
        options=list(
            feature_options.keys()
        ),
        default=list(
            feature_options.keys()
        ),
        help=(
            "Weather uses historical monthly "
            "averages for future values. "
            "Currency uses the latest observed rate."
        ),
    )
)


selected_features = [
    feature_options[label]
    for label
    in selected_feature_labels
]


# ---------------------------------------------------------
# Advanced SNARIMAX parameters
# ---------------------------------------------------------

with st.expander(
    "Advanced model parameters"
):

    col1, col2, col3 = (
        st.columns(3)
    )


    with col1:

        p = st.number_input(
            "p – AR order",
            min_value=0,
            max_value=12,
            value=3,
            step=1,
        )


        sp = st.number_input(
            "sp – Seasonal AR order",
            min_value=0,
            max_value=3,
            value=1,
            step=1,
        )


    with col2:

        d = st.number_input(
            "d – Differencing",
            min_value=0,
            max_value=2,
            value=1,
            step=1,
        )


        sd = st.number_input(
            "sd – Seasonal differencing",
            min_value=0,
            max_value=2,
            value=1,
            step=1,
        )


    with col3:

        q = st.number_input(
            "q – MA order",
            min_value=0,
            max_value=12,
            value=1,
            step=1,
        )


        sq = st.number_input(
            "sq – Seasonal MA order",
            min_value=0,
            max_value=3,
            value=1,
            step=1,
        )


st.caption(
    "Monthly seasonality is fixed at m = 12. "
    "The defaults correspond to the best-performing "
    "configuration found in the notebook experiments."
)


# ---------------------------------------------------------
# Determine safe training end
# ---------------------------------------------------------

requested_period = pd.Period(
    requested_end_month,
    freq="M",
)


# Use complete calendar months only.
latest_complete_period = (
    pd.Timestamp.today()
    .to_period("M")
    - 1
)


reservoir_latest_period = (
    area_data[
        "date"
    ]
    .max()
    .to_period("M")
)


effective_end_period = min(
    requested_period,
    latest_complete_period,
    reservoir_latest_period,
)


# Weather adds an ERA5 availability constraint.
if any(
    feature
    in WEATHER_FEATURES
    for feature
    in selected_features
):

    era5_date = (
        latest_era5_date()
    )


    era5_period = (
        era5_date.to_period("M")
    )


    # If the safe ERA5 date is not the final
    # day of the month, use the previous month.
    if (
        era5_date.day
        < era5_period.days_in_month
    ):

        era5_period = (
            era5_period - 1
        )


    effective_end_period = min(
        effective_end_period,
        era5_period,
    )


if (
    effective_end_period
    != requested_period
):

    st.info(
        "The requested end month is not fully "
        "available across the selected data sources. "
        f"The training period therefore ends at "
        f"**{effective_end_period}**."
    )


# ---------------------------------------------------------
# Training dates
# ---------------------------------------------------------

start_period = (
    effective_end_period
    - (
        history_years * 12
        - 1
    )
)


start_date = (
    start_period
    .start_time
    .strftime(
        "%Y-%m-%d"
    )
)


end_date = (
    effective_end_period
    .end_time
    .strftime(
        "%Y-%m-%d"
    )
)


st.caption(
    f"Training period: "
    f"{start_period} → "
    f"{effective_end_period}"
)


# ---------------------------------------------------------
# Prepare forecasting dataset
# ---------------------------------------------------------

with st.spinner(
    "Preparing monthly forecasting data..."
):

    try:

        forecast_data = (
            prepare_forecast_data(
                reservoir_data=df,
                area_type=(
                    selected_area_type
                ),
                area_number=(
                    selected_area
                ),
                start_date=start_date,
                end_date=end_date,
                selected_features=(
                    selected_features
                ),
                n_weather_locations=5,
            )
        )


    except requests.exceptions.HTTPError as exc:

        response = (
            exc.response
        )


        response_url = (
            response.url
            if response is not None
            else ""
        )


        status_code = (
            response.status_code
            if response is not None
            else None
        )


        if (
            status_code == 429
            and "open-meteo.com"
            in response_url
        ):

            st.error(
                "The Open-Meteo daily API request limit "
                "has been reached. Please try again later "
                "or on the following day."
            )

        else:

            st.error(
                "An external data source could not be "
                "retrieved while preparing the forecast."
            )


        st.stop()


    except requests.exceptions.RequestException:

        st.error(
            "An external data source could not be "
            "reached while preparing the forecast. "
            "Please try again later."
        )

        st.stop()


    except ValueError as exc:

        st.error(
            "Forecasting data could not be prepared."
        )

        st.code(
            str(exc)
        )

        st.stop()


    except Exception as exc:

        st.error(
            "Forecasting data could not be prepared."
        )

        st.code(
            str(exc)
        )

        st.stop()


# ---------------------------------------------------------
# Run forecast
# ---------------------------------------------------------

with st.spinner(
    "Training SNARIMAX and generating forecast..."
):

    try:

        (
            future_forecast,
            training_data,
            model,
        ) = forecast_future_snarimax(
            data=forecast_data,
            selected_features=(
                selected_features
            ),
            history_years=(
                history_years
            ),
            horizon_months=(
                horizon_months
            ),
            p=int(p),
            d=int(d),
            q=int(q),
            m=12,
            sp=int(sp),
            sd=int(sd),
            sq=int(sq),
        )


    except Exception as exc:

        st.error(
            "The forecast could not be generated."
        )

        st.code(
            str(exc)
        )

        st.stop()


# ---------------------------------------------------------
# Forecast KPIs
# ---------------------------------------------------------

st.subheader(
    "Forecast Summary"
)


metric1, metric2, metric3 = (
    st.columns(3)
)


metric1.metric(
    "Next month",
    (
        f"{future_forecast['predicted_fill_level'].iloc[0]:.1%}"
    ),
)


metric2.metric(
    "Forecast minimum",
    (
        f"{future_forecast['predicted_fill_level'].min():.1%}"
    ),
)


metric3.metric(
    "Forecast maximum",
    (
        f"{future_forecast['predicted_fill_level'].max():.1%}"
    ),
)


# ---------------------------------------------------------
# Warn about physical clipping
# ---------------------------------------------------------

outside_bounds = (
    (
        future_forecast[
            "predicted_fill_level_raw"
        ]
        < 0
    )
    |
    (
        future_forecast[
            "predicted_fill_level_raw"
        ]
        > 1
    )
)


if outside_bounds.any():

    st.warning(
        "One or more raw SNARIMAX predictions fall "
        "outside the physical [0, 1] reservoir range. "
        "Displayed forecasts are clipped to valid values, "
        "while the raw predictions remain available below."
    )


# ---------------------------------------------------------
# Main forecast chart
# ---------------------------------------------------------

st.subheader(
    "Forecast"
)


history_plot = (
    training_data[
        "fill_level"
    ]
    .tail(24)
)


forecast_fig = (
    go.Figure()
)


forecast_fig.add_trace(
    go.Scatter(
        x=history_plot.index,
        y=history_plot.values,
        mode="lines+markers",
        name="Observed",
        hovertemplate=(
            "%{x|%Y-%m}"
            "<br>Fill level: %{y:.1%}"
            "<extra></extra>"
        ),
    )
)


# Include the final observed value so that
# the forecast line connects to history.
forecast_x = [
    history_plot.index[-1]
] + list(
    future_forecast.index
)


forecast_y = [
    history_plot.iloc[-1]
] + list(
    future_forecast[
        "predicted_fill_level"
    ]
)


forecast_fig.add_trace(
    go.Scatter(
        x=forecast_x,
        y=forecast_y,
        mode="lines+markers",
        name="Forecast",
        line=dict(
            dash="dash"
        ),
        hovertemplate=(
            "%{x|%Y-%m}"
            "<br>Forecast: %{y:.1%}"
            "<extra></extra>"
        ),
    )
)


forecast_fig.update_layout(
    xaxis_title="Month",
    yaxis_title="Reservoir filling level",
    yaxis=dict(
        range=[
            0,
            1.05,
        ],
        tickformat=".0%",
    ),
    hovermode="x unified",
    height=520,
    margin=dict(
        l=40,
        r=20,
        t=30,
        b=40,
    ),
)


st.plotly_chart(
    forecast_fig,
    width="stretch",
)


# ---------------------------------------------------------
# Animated forecast
# ---------------------------------------------------------

st.subheader(
    "Forecast Animation"
)


animation_rows = []


for step in range(
    1,
    horizon_months + 1,
):

    for date, value in (
        history_plot.items()
    ):

        animation_rows.append(
            {
                "date": date,
                "fill_level": value,
                "series": "Observed",
                "step": step,
            }
        )


    for date, row in (
        future_forecast
        .iloc[:step]
        .iterrows()
    ):

        animation_rows.append(
            {
                "date": date,
                "fill_level": (
                    row[
                        "predicted_fill_level"
                    ]
                ),
                "series": "Forecast",
                "step": step,
            }
        )


animation_data = (
    pd.DataFrame(
        animation_rows
    )
)


animation_fig = px.line(
    animation_data,
    x="date",
    y="fill_level",
    color="series",
    animation_frame="step",
    markers=True,
    labels={
        "date": "Month",
        "fill_level": (
            "Reservoir filling level"
        ),
        "series": "",
        "step": "Forecast step",
    },
)


animation_fig.update_yaxes(
    range=[
        0,
        1.05,
    ],
    tickformat=".0%",
)


animation_fig.update_xaxes(
    range=[
        history_plot.index.min(),
        future_forecast.index.max(),
    ]
)


animation_fig.update_layout(
    height=520,
    hovermode="x unified",
)


st.plotly_chart(
    animation_fig,
    width="stretch",
)


# ---------------------------------------------------------
# Future exogenous assumptions
# ---------------------------------------------------------

if selected_features:

    with st.expander(
        "Future exogenous assumptions"
    ):

        st.write(
            "Future weather values use historical "
            "averages for the corresponding calendar "
            "month. Currency variables use their most "
            "recent observed value."
        )


        st.dataframe(
            future_forecast[
                selected_features
            ],
            width="stretch",
        )


# ---------------------------------------------------------
# Forecast table
# ---------------------------------------------------------

with st.expander(
    "Show forecast data"
):

    columns = (
        selected_features
        + [
            "predicted_fill_level_raw",
            "predicted_fill_level",
        ]
    )


    st.dataframe(
        future_forecast[
            columns
        ],
        width="stretch",
    )


# ---------------------------------------------------------
# Method information
# ---------------------------------------------------------

with st.expander(
    "About the forecast"
):

    st.markdown(
        """
        The forecast uses River's online SNARIMAX model at
        monthly resolution.

        The model can include temperature, precipitation,
        snowfall, EUR/NOK and USD/NOK as exogenous variables.

        Historical weather observations are retrieved at daily
        resolution from ERA5 and aggregated to monthly values.
        Multiple sampled geographical locations are retrieved in
        a single Open-Meteo request to reduce API usage.

        Since actual future exogenous observations are not
        available, weather variables use historical monthly
        averages and currency variables use the latest observed
        value. These should therefore be interpreted as scenario
        assumptions rather than separate forecasts.

        Reservoir filling is physically constrained to the
        interval 0–1. Raw SNARIMAX predictions are retained,
        while displayed forecasts are clipped to this valid
        range.
        """
    )