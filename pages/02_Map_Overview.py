import json

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from modules.data_loader import load_data
from modules.map_utils import load_area_geodata
from modules.weather_analysis import (
    get_weather_map_summary,
    latest_era5_date,
)


st.title(
    "Map & Data Overview"
)

st.write(
    "Explore Norwegian reservoir statistics geographically "
    "and select an area for use across the dashboard."
)


# ---------------------------------------------------------
# Load reservoir data
# ---------------------------------------------------------

df = load_data()


# ---------------------------------------------------------
# Area type
# ---------------------------------------------------------

area_type_labels = {
    "EL": "Price areas",
    "VASS": "Water regions",
    "NO": "Norway",
}


available_types = [
    area_type
    for area_type in [
        "EL",
        "VASS",
        "NO",
    ]
    if area_type
    in df["area_type"].unique()
]


if (
    "selected_area_type"
    not in st.session_state
    or st.session_state[
        "selected_area_type"
    ]
    not in available_types
):
    st.session_state[
        "selected_area_type"
    ] = "EL"


selected_area_type = st.radio(
    "Area type",
    options=available_types,
    format_func=lambda x: (
        area_type_labels[x]
    ),
    index=available_types.index(
        st.session_state[
            "selected_area_type"
        ]
    ),
    horizontal=True,
)


# Reset selected area when
# the geographical type changes.
if (
    selected_area_type
    != st.session_state[
        "selected_area_type"
    ]
):

    st.session_state[
        "selected_area_type"
    ] = selected_area_type

    st.session_state.pop(
        "selected_area_number",
        None,
    )

else:

    st.session_state[
        "selected_area_type"
    ] = selected_area_type


# ---------------------------------------------------------
# Filter reservoir data
# ---------------------------------------------------------

area_data = (
    df[
        df["area_type"]
        == selected_area_type
    ]
    .sort_values("date")
    .copy()
)


area_data["month"] = (
    area_data["date"]
    .dt.to_period("M")
    .astype(str)
)


# ---------------------------------------------------------
# Valid areas
# ---------------------------------------------------------

valid_areas = sorted(
    area_data[
        "area_number"
    ]
    .dropna()
    .unique()
    .tolist()
)


if (
    "selected_area_number"
    not in st.session_state
    or st.session_state[
        "selected_area_number"
    ]
    not in valid_areas
):

    st.session_state[
        "selected_area_number"
    ] = valid_areas[0]


selected_area = (
    st.session_state[
        "selected_area_number"
    ]
)


# ---------------------------------------------------------
# Map metric
# ---------------------------------------------------------

metric_options = {
    "Fill Level": (
        "fill_level"
    ),
    "Stored Energy (TWh)": (
        "stored_energy_twh"
    ),
    "Capacity (TWh)": (
        "capacity_twh"
    ),
    "Average Temperature (°C)": (
        "avg_temperature"
    ),
    "Total Precipitation (mm)": (
        "total_precipitation"
    ),
    "Total Snowfall (cm)": (
        "total_snowfall"
    ),
}


selected_metric_label = (
    st.selectbox(
        "Colour areas by",
        options=list(
            metric_options.keys()
        ),
    )
)


selected_metric = (
    metric_options[
        selected_metric_label
    ]
)


metric_labels = {
    "fill_level": (
        "Fill level"
    ),
    "stored_energy_twh": (
        "Stored energy (TWh)"
    ),
    "capacity_twh": (
        "Capacity (TWh)"
    ),
    "avg_temperature": (
        "Average temperature (°C)"
    ),
    "total_precipitation": (
        "Total precipitation (mm)"
    ),
    "total_snowfall": (
        "Total snowfall (cm)"
    ),
}


weather_metrics = {
    "avg_temperature",
    "total_precipitation",
    "total_snowfall",
}


# ---------------------------------------------------------
# Time interval
# ---------------------------------------------------------

month_options = (
    area_data["month"]
    .drop_duplicates()
    .sort_values()
    .tolist()
)


# Weather overlays can only use months
# for which ERA5 observations are available.
if (
    selected_metric
    in weather_metrics
):

    latest_weather_month = (
        latest_era5_date()
        .to_period("M")
        .strftime("%Y-%m")
    )

    available_month_options = [
        month
        for month in month_options
        if month
        <= latest_weather_month
    ]

else:

    available_month_options = (
        month_options
    )


default_start = max(
    0,
    len(
        available_month_options
    )
    - 12,
)


start_month, end_month = (
    st.select_slider(
        "Time period",
        options=(
            available_month_options
        ),
        value=(
            available_month_options[
                default_start
            ],
            available_month_options[
                -1
            ],
        ),
    )
)


# Avoid excessively large Open-Meteo
# requests for weather overlays.
if (
    selected_metric
    in weather_metrics
):

    weather_months = (
        pd.Period(
            end_month,
            freq="M",
        )
        - pd.Period(
            start_month,
            freq="M",
        )
    ).n + 1


    if weather_months > 24:

        st.warning(
            "Weather overlays are limited "
            "to a maximum period of 24 months "
            "to reduce Open-Meteo API usage "
            "and loading time. Please select "
            "a shorter period."
        )

        st.stop()


# Save period globally.
st.session_state[
    "selected_start_month"
] = start_month

st.session_state[
    "selected_end_month"
] = end_month


# ---------------------------------------------------------
# Filter reservoir observations
# ---------------------------------------------------------

period_data = area_data[
    (
        area_data["month"]
        >= start_month
    )
    & (
        area_data["month"]
        <= end_month
    )
].copy()


# ---------------------------------------------------------
# Latest reservoir values
# ---------------------------------------------------------

latest_area_values = (
    period_data
    .sort_values("date")
    .groupby(
        "area_number",
        as_index=False,
    )
    .last()
)


# ---------------------------------------------------------
# Load geographical polygons
# ---------------------------------------------------------

geo = load_area_geodata(
    selected_area_type
)


# ---------------------------------------------------------
# Create map data
# ---------------------------------------------------------

if (
    selected_metric
    in weather_metrics
):

    requested_start_date = (
        pd.Period(
            start_month,
            freq="M",
        )
        .start_time
    )

    requested_end_date = (
        pd.Period(
            end_month,
            freq="M",
        )
        .end_time
    )

    available_end_date = (
        latest_era5_date()
    )


    # Prevent requests for ERA5
    # observations that are not
    # available yet.
    weather_end_date = min(
        requested_end_date,
        available_end_date,
    )


    start_date = (
        requested_start_date
        .strftime("%Y-%m-%d")
    )

    end_date = (
        weather_end_date
        .strftime("%Y-%m-%d")
    )


    # The latest ERA5 month may only
    # contain observations for part
    # of the month.
    if (
        requested_end_date
        > available_end_date
    ):

        st.info(
            "ERA5 data are currently "
            "available through "
            f"{available_end_date:%Y-%m-%d}. "
            "Weather values are therefore "
            "calculated only up to this date."
        )


    if (
        requested_start_date
        > available_end_date
    ):

        st.warning(
            "The selected period does not "
            "contain currently available "
            "ERA5 observations."
        )

        st.stop()


    with st.spinner(
        "Loading historical weather data..."
    ):

        try:

            weather_summary = (
                get_weather_map_summary(
                    area_type=(
                        selected_area_type
                    ),
                    area_numbers=tuple(
                        valid_areas
                    ),
                    start_date=start_date,
                    end_date=end_date,
                    n_locations=3,
                )
            )

        except requests.exceptions.RequestException:

            st.error(
                "Weather data could not be "
                "retrieved from Open-Meteo. "
                "Try a shorter period or try "
                "again later."
            )

            st.stop()


    map_data = geo.merge(
        weather_summary[
            [
                "area_number",
                selected_metric,
            ]
        ],
        on="area_number",
        how="left",
    )

else:

    map_data = geo.merge(
        latest_area_values[
            [
                "area_number",
                selected_metric,
            ]
        ],
        on="area_number",
        how="left",
    )


# ---------------------------------------------------------
# Convert geographical data to GeoJSON
# ---------------------------------------------------------

geojson = json.loads(
    map_data.to_json()
)


# ---------------------------------------------------------
# Main choropleth map
# ---------------------------------------------------------

fig = px.choropleth(
    map_data,
    geojson=geojson,
    locations="area_name",
    featureidkey=(
        "properties.area_name"
    ),
    color=selected_metric,
    hover_name="area_name",
    hover_data={
        "area_number": True,
        selected_metric: ":.3f",
    },
    labels={
        selected_metric:
        metric_labels[
            selected_metric
        ],
    },
)


fig.update_geos(
    fitbounds="locations",
    visible=False,
)


fig.update_traces(
    marker_line_width=1.5,
    marker_line_color="gray",
    marker_opacity=0.75,
)


# ---------------------------------------------------------
# Highlight selected area
# ---------------------------------------------------------

selected_geo = map_data[
    map_data[
        "area_number"
    ]
    == selected_area
].copy()


if not selected_geo.empty:

    selected_geojson = (
        json.loads(
            selected_geo.to_json()
        )
    )

    fig.add_trace(
        go.Choropleth(
            geojson=(
                selected_geojson
            ),
            locations=(
                selected_geo[
                    "area_name"
                ]
            ),
            featureidkey=(
                "properties.area_name"
            ),
            z=[
                1
            ]
            * len(
                selected_geo
            ),
            colorscale=[
                [
                    0,
                    "rgba(0,0,0,0)",
                ],
                [
                    1,
                    "rgba(0,0,0,0)",
                ],
            ],
            showscale=False,
            marker_line_width=4,
            marker_line_color=(
                "black"
            ),
            hoverinfo="skip",
        )
    )


fig.update_layout(
    margin=dict(
        l=0,
        r=0,
        t=20,
        b=0,
    ),
    height=600,
)


# ---------------------------------------------------------
# Display interactive map
# ---------------------------------------------------------

map_event = st.plotly_chart(
    fig,
    width="stretch",
    key="reservoir_map",
    on_select="rerun",
    selection_mode="points",
)


# ---------------------------------------------------------
# Map explanation
# ---------------------------------------------------------

if (
    selected_metric
    in weather_metrics
):

    st.caption(
        "Weather colours represent aggregated "
        "ERA5 weather conditions over the "
        "selected period. Three reproducible "
        "sample locations per region are used "
        "to reduce API usage and loading time."
    )

else:

    st.caption(
        "Reservoir colours represent the "
        "latest available observation within "
        "the selected period."
    )


# ---------------------------------------------------------
# Store clicked area
# ---------------------------------------------------------

selected_points = (
    map_event.selection.points
    if map_event
    else []
)


if selected_points:

    point = (
        selected_points[0]
    )

    clicked_location = (
        point.get(
            "location"
        )
    )


    if (
        clicked_location
        is not None
    ):

        matching_area = (
            map_data.loc[
                map_data[
                    "area_name"
                ]
                == clicked_location,
                "area_number",
            ]
        )


        if not matching_area.empty:

            clicked_area = int(
                matching_area.iloc[0]
            )


            if (
                clicked_area
                != st.session_state[
                    "selected_area_number"
                ]
            ):

                st.session_state[
                    "selected_area_number"
                ] = clicked_area

                st.rerun()


# ---------------------------------------------------------
# Current selected area
# ---------------------------------------------------------

selected_area = (
    st.session_state[
        "selected_area_number"
    ]
)


selected_name_match = (
    map_data.loc[
        map_data[
            "area_number"
        ]
        == selected_area,
        "area_name",
    ]
)


if not selected_name_match.empty:

    selected_name = (
        selected_name_match.iloc[0]
    )

else:

    selected_name = (
        f"{selected_area_type}"
        f"{selected_area}"
    )


st.success(
    f"Selected area: "
    f"**{selected_name}**"
)


# ---------------------------------------------------------
# Selected-area reservoir data
# ---------------------------------------------------------

selected_data = (
    period_data[
        period_data[
            "area_number"
        ]
        == selected_area
    ]
    .sort_values("date")
    .copy()
)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

if not selected_data.empty:

    latest = (
        selected_data.iloc[-1]
    )

    col1, col2, col3 = (
        st.columns(3)
    )


    col1.metric(
        "Fill level",
        (
            f"{latest['fill_level']:.1%}"
        ),
    )


    col2.metric(
        "Stored energy",
        (
            f"{latest['stored_energy_twh']:.2f} "
            "TWh"
        ),
    )


    col3.metric(
        "Capacity",
        (
            f"{latest['capacity_twh']:.2f} "
            "TWh"
        ),
    )


# ---------------------------------------------------------
# Reservoir development
# ---------------------------------------------------------

st.subheader(
    "Reservoir Development"
)


measurement_options = {
    "Fill Level": (
        "fill_level"
    ),
    "Stored Energy (TWh)": (
        "stored_energy_twh"
    ),
    "Capacity (TWh)": (
        "capacity_twh"
    ),
    "Weekly Change": (
        "change_in_fill_level"
    ),
}


measurement_label = (
    st.selectbox(
        "Measurement",
        options=list(
            measurement_options.keys()
        ),
    )
)


measurement = (
    measurement_options[
        measurement_label
    ]
)


line_fig = px.line(
    selected_data,
    x="date",
    y=measurement,
    markers=True,
    labels={
        "date": "Date",
        measurement:
        measurement_label,
    },
)


line_fig.update_layout(
    xaxis_title="Date",
    yaxis_title=measurement_label,
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20,
    ),
    hovermode="x unified",
)


st.plotly_chart(
    line_fig,
    width="stretch",
)


# ---------------------------------------------------------
# Reservoir data table
# ---------------------------------------------------------

with st.expander(
    "Show reservoir data"
):

    st.dataframe(
        selected_data[
            [
                "date",
                "area_type",
                "area_number",
                "fill_level",
                "capacity_twh",
                "stored_energy_twh",
                "change_in_fill_level",
            ]
        ],
        hide_index=True,
        width="stretch",
    )