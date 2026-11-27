import plotly.graph_objects as go
import requests
import streamlit as st

from modules.area_selector import (
    area_selector,
)
from modules.correlation_analysis import (
    prepare_correlation_data,
    sliding_window_correlation,
)
from modules.data_loader import (
    load_data,
)
from modules.weather_analysis import (
    download_daily_weather,
)


st.title(
    "Weather–Reservoir Correlation"
)

st.write(
    "Explore how meteorological conditions are related "
    "to reservoir filling levels using rolling correlations "
    "with selectable lag and window length."
)


# ---------------------------------------------------------
# Load reservoir data
# ---------------------------------------------------------

df = load_data()


# ---------------------------------------------------------
# Shared geographical selection
# ---------------------------------------------------------

selected_area_type, selected_area = (
    area_selector(df)
)


st.caption(
    f"Analysing {selected_area_type} area "
    f"{selected_area}."
)


# ---------------------------------------------------------
# Analysis period
# ---------------------------------------------------------

start_year, end_year = st.select_slider(
    "Analysis period",
    options=list(
        range(2020, 2025)
    ),
    value=(
        2020,
        2024,
    ),
)


start_date = (
    f"{start_year}-01-01"
)

end_date = (
    f"{end_year}-12-31"
)


# ---------------------------------------------------------
# Load ERA5 weather
# ---------------------------------------------------------

with st.spinner(
    "Loading ERA5 weather data..."
):

    try:

        # Daily ERA5 data are sufficient here because
        # the correlation analysis is later aggregated
        # to monthly resolution.
        weather = (
            download_daily_weather(
                area_type=(
                    selected_area_type
                ),
                area_number=(
                    selected_area
                ),
                start_date=(
                    start_date
                ),
                end_date=(
                    end_date
                ),
                n_locations=5,
            )
        )

    except requests.exceptions.RequestException:

        st.error(
            "Weather data could not be retrieved "
            "from Open-Meteo. Please try again later "
            "or select a shorter analysis period."
        )

        st.stop()

    except ValueError as exc:

        st.warning(
            str(exc)
        )

        st.stop()


# ---------------------------------------------------------
# Prepare monthly dataset
# ---------------------------------------------------------

correlation_data = (
    prepare_correlation_data(
        reservoir_data=df,
        weather_data=weather,
        area_type=selected_area_type,
        area_number=selected_area,
    )
)


# ---------------------------------------------------------
# Analysis controls
# ---------------------------------------------------------

weather_options = {
    "Temperature": (
        "avg_temperature"
    ),
    "Precipitation": (
        "total_precipitation"
    ),
    "Snowfall": (
        "total_snowfall"
    ),
}


reservoir_options = {
    "Monthly change in filling": (
        "fill_change"
    ),
    "Filling level": (
        "fill_level"
    ),
}


col1, col2 = st.columns(2)


with col1:

    selected_weather_label = (
        st.selectbox(
            "Weather property",
            options=list(
                weather_options.keys()
            ),
            index=0,
        )
    )


with col2:

    selected_reservoir_label = (
        st.selectbox(
            "Reservoir property",
            options=list(
                reservoir_options.keys()
            ),
            index=0,
        )
    )


selected_weather = (
    weather_options[
        selected_weather_label
    ]
)


selected_reservoir = (
    reservoir_options[
        selected_reservoir_label
    ]
)


# ---------------------------------------------------------
# Lag and rolling window
# ---------------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    lag = st.slider(
        "Weather lag (months)",
        min_value=0,
        max_value=6,
        value=1,
        step=1,
        help=(
            "A lag of 2 compares current reservoir "
            "conditions with weather two months earlier."
        ),
    )


with col2:

    window = st.slider(
        "Rolling window (months)",
        min_value=6,
        max_value=24,
        value=12,
        step=1,
        help=(
            "Number of monthly observations used "
            "for each correlation calculation."
        ),
    )


# ---------------------------------------------------------
# Calculate sliding correlation
# ---------------------------------------------------------

correlation_result = (
    sliding_window_correlation(
        correlation_data,
        weather_property=(
            selected_weather
        ),
        reservoir_property=(
            selected_reservoir
        ),
        lag=lag,
        window=window,
    )
)


# ---------------------------------------------------------
# Check result
# ---------------------------------------------------------

if correlation_result.empty:

    st.warning(
        "There are not enough observations "
        "for the selected settings."
    )

    st.stop()


# ---------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------

mean_correlation = (
    correlation_result[
        "correlation"
    ].mean()
)


mean_absolute_correlation = (
    correlation_result[
        "correlation"
    ]
    .abs()
    .mean()
)


strongest_date = (
    correlation_result[
        "correlation"
    ]
    .abs()
    .idxmax()
)


strongest_correlation = (
    correlation_result.loc[
        strongest_date,
        "correlation",
    ]
)


metric1, metric2, metric3 = (
    st.columns(3)
)


metric1.metric(
    "Mean correlation",
    f"{mean_correlation:+.2f}",
)


metric2.metric(
    "Mean |correlation|",
    (
        f"{mean_absolute_correlation:.2f}"
    ),
)


metric3.metric(
    "Strongest correlation",
    (
        f"{strongest_correlation:+.2f}"
    ),
    help=(
        f"Observed around "
        f"{strongest_date:%Y-%m}"
    ),
)


# ---------------------------------------------------------
# Rolling correlation plot
# ---------------------------------------------------------

st.subheader(
    "Sliding-Window Correlation"
)


fig = go.Figure()


fig.add_trace(
    go.Scatter(
        x=correlation_result.index,
        y=correlation_result[
            "correlation"
        ],
        mode="lines",
        name="Rolling correlation",
        hovertemplate=(
            "%{x|%Y-%m}"
            "<br>Correlation: %{y:.3f}"
            "<extra></extra>"
        ),
    )
)


fig.add_hline(
    y=0,
    line_dash="dash",
)


fig.update_layout(
    title=(
        f"{selected_weather_label} vs "
        f"{selected_reservoir_label}"
    ),
    xaxis_title="Month",
    yaxis_title="Correlation",
    yaxis=dict(
        range=[
            -1,
            1,
        ]
    ),
    hovermode="x unified",
    height=500,
    margin=dict(
        l=40,
        r=20,
        t=70,
        b=40,
    ),
)


st.plotly_chart(
    fig,
    width="stretch",
)


# ---------------------------------------------------------
# Interpretation
# ---------------------------------------------------------

st.subheader(
    "Interpretation"
)


if mean_correlation > 0:

    direction = (
        "positive"
    )

elif mean_correlation < 0:

    direction = (
        "negative"
    )

else:

    direction = (
        "approximately neutral"
    )


st.write(
    f"The selected settings produce an average "
    f"**{direction} correlation of "
    f"{mean_correlation:+.2f}**. "
    f"The average absolute correlation is "
    f"**{mean_absolute_correlation:.2f}**."
)


st.info(
    "Correlation describes association, not causality. "
    "Changes in the relationship over time may reflect "
    "seasonality, snow storage and melting, hydrological "
    "delays, electricity production or other factors."
)


# ---------------------------------------------------------
# Data
# ---------------------------------------------------------

with st.expander(
    "Show monthly analysis data"
):

    st.dataframe(
        correlation_result,
        width="stretch",
    )


# ---------------------------------------------------------
# Method information
# ---------------------------------------------------------

with st.expander(
    "About the analysis"
):

    st.markdown(
        """
        Weather observations are downloaded from ERA5 at
        daily resolution and subsequently aggregated to
        monthly resolution for the correlation analysis.

        A reproducible sample of five geographical locations
        is used to represent weather conditions in the selected
        region while limiting Open-Meteo API usage.

        Reservoir filling uses the final available observation
        from each month. Monthly filling change is calculated
        as the difference from the previous month.

        A positive lag means that the meteorological variable
        occurs before the reservoir observation. For example,
        a lag of two months compares current reservoir
        conditions with weather two months earlier.

        The rolling-window length determines how many monthly
        observations are included in each correlation estimate.
        Short windows can capture changing relationships more
        quickly but are also more sensitive to noise.

        Correlation represents statistical association and
        should not be interpreted as evidence of causality.
        """
    )