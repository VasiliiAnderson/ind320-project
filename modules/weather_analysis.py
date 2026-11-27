from pathlib import Path
import time

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import streamlit as st

from scipy.fft import dct, idct
from scipy.stats import median_abs_deviation
from sklearn.neighbors import LocalOutlierFactor


ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

WEATHER_VARIABLES = [
    "temperature_2m",
    "precipitation",
    "snowfall",
]


# ---------------------------------------------------------
# Weather coordinates
# ---------------------------------------------------------

@st.cache_data
def load_weather_coordinates(
    area_type,
    area_number,
    n_points=1000,
    random_state=42,
):
    """
    Sample weather locations for the selected Magasinstatistikk area.

    EL areas use the NVE electricity bidding-area shapefile.
    VASS areas use combinations of the NVE regional shapefile.
    NO represents the combined Norwegian NVE regions.
    """

    project_root = Path(__file__).resolve().parents[1]

    if area_type == "EL":

        shapefile_dir = (
            project_root
            / "data"
            / "shapefiles"
            / "elspot"
        )

        shapefiles = list(
            shapefile_dir.glob("*.shp")
        )

        if not shapefiles:
            raise FileNotFoundError(
                "No electricity-area shapefile found."
            )

        gdf = gpd.read_file(
            shapefiles[0]
        )

        gdf["region"] = (
            gdf["budomr"]
            .astype(str)
            .str.replace(
                " ",
                "",
                regex=False,
            )
        )

        target_region = f"NO{int(area_number)}"

        selected = gdf[
            gdf["region"] == target_region
        ]

        if selected.empty:
            raise ValueError(
                f"No polygon found for {target_region}."
            )

        geometry = selected.geometry.union_all()
        crs = gdf.crs

    elif area_type == "VASS":

        shapefile_dir = (
            project_root
            / "data"
            / "shapefiles"
            / "nve_regions"
        )

        shapefiles = list(
            shapefile_dir.glob("*.shp")
        )

        if not shapefiles:
            raise FileNotFoundError(
                "No NVE region shapefile found."
            )

        gdf = gpd.read_file(
            shapefiles[0],
            encoding="utf-8",
        )

        vass_mapping = {
            1: ["RS", "RØ"],
            2: ["RV"],
            3: ["RM", "RN"],
        }

        regions = vass_mapping[
            int(area_number)
        ]

        missing_regions = (
            set(regions)
            - set(gdf["REGION"].unique())
        )

        if missing_regions:
            raise ValueError(
                f"Missing NVE regions: {missing_regions}"
            )

        selected = gdf[
            gdf["REGION"].isin(regions)
        ]

        geometry = selected.geometry.union_all()
        crs = gdf.crs

    elif area_type == "NO":

        shapefile_dir = (
            project_root
            / "data"
            / "shapefiles"
            / "nve_regions"
        )

        shapefiles = list(
            shapefile_dir.glob("*.shp")
        )

        if not shapefiles:
            raise FileNotFoundError(
                "No NVE region shapefile found."
            )

        gdf = gpd.read_file(
            shapefiles[0],
            encoding="utf-8",
        )

        geometry = gdf.geometry.union_all()
        crs = gdf.crs

    else:
        raise ValueError(
            f"Unsupported area type: {area_type}"
        )

    geometry_series = gpd.GeoSeries(
        [geometry],
        crs=crs,
    )

    sampled_points = (
        geometry_series
        .sample_points(
            size=n_points,
            random_state=random_state,
        )
        .to_crs(epsg=4326)
    )

    coordinates = []

    for point in sampled_points.iloc[0].geoms:
        coordinates.append(
            {
                "latitude": point.y,
                "longitude": point.x,
            }
        )

    return pd.DataFrame(coordinates)


# ---------------------------------------------------------
# Hourly weather download
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def download_weather(
    area_type,
    area_number,
    start_date,
    end_date,
    n_locations=10,
    random_state=42,
):
    """
    Download hourly ERA5 weather data for the selected
    Magasinstatistikk area.
    """

    locations = load_weather_coordinates(
        area_type=area_type,
        area_number=area_number,
        n_points=1000,
        random_state=random_state,
    )

    selected_points = locations.sample(
        n=min(
            n_locations,
            len(locations),
        ),
        random_state=random_state,
    )

    weather_frames = []

    for location_id, (_, point) in enumerate(
        selected_points.iterrows()
    ):

        params = {
            "latitude": point["latitude"],
            "longitude": point["longitude"],
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ",".join(
                WEATHER_VARIABLES
            ),
            "models": "era5",
            "timezone": "UTC",
        }

        response = requests.get(
            ARCHIVE_URL,
            params=params,
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        hourly = pd.DataFrame(
            data["hourly"]
        )

        hourly["time"] = pd.to_datetime(
            hourly["time"],
            utc=True,
        )

        hourly["location_id"] = (
            location_id
        )

        weather_frames.append(
            hourly
        )

        time.sleep(0.2)

    weather = pd.concat(
        weather_frames,
        ignore_index=True,
    )

    hourly_average = (
        weather
        .groupby(
            "time",
            as_index=False,
        )
        .agg(
            avg_temperature=(
                "temperature_2m",
                "mean",
            ),
            avg_precipitation=(
                "precipitation",
                "mean",
            ),
            avg_snowfall=(
                "snowfall",
                "mean",
            ),
        )
    )

    return hourly_average

# ---------------------------------------------------------
# Daily weather download
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def download_daily_weather(
    area_type,
    area_number,
    start_date,
    end_date,
    n_locations=5,
    random_state=42,
):
    """
    Download daily ERA5 weather observations for
    correlation analysis.

    Multiple geographical locations are retrieved in
    one Open-Meteo request to reduce API usage.
    """

    locations = load_weather_coordinates(
        area_type=area_type,
        area_number=area_number,
        n_points=1000,
        random_state=random_state,
    )

    selected_points = locations.sample(
        n=min(
            n_locations,
            len(locations),
        ),
        random_state=random_state,
    )

    # Send all selected coordinates in one API request.
    latitudes = ",".join(
        selected_points[
            "latitude"
        ].astype(str)
    )

    longitudes = ",".join(
        selected_points[
            "longitude"
        ].astype(str)
    )

    params = {
        "latitude": latitudes,
        "longitude": longitudes,
        "start_date": start_date,
        "end_date": end_date,
        "daily": (
            "temperature_2m_mean,"
            "precipitation_sum,"
            "snowfall_sum"
        ),
        "models": "era5",
        "timezone": "UTC",
    }

    response = requests.get(
        ARCHIVE_URL,
        params=params,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    # Multiple coordinates return a list of
    # location-specific response objects.
    if isinstance(data, dict):
        data = [data]

    weather_frames = []

    for location_id, location_data in enumerate(
        data
    ):

        daily = pd.DataFrame(
            location_data["daily"]
        )

        daily["time"] = pd.to_datetime(
            daily["time"],
            utc=True,
        )

        daily["location_id"] = (
            location_id
        )

        weather_frames.append(
            daily
        )

    if not weather_frames:

        raise ValueError(
            "No ERA5 weather observations "
            "were returned."
        )

    weather = pd.concat(
        weather_frames,
        ignore_index=True,
    )

    # Average weather conditions across
    # the sampled geographical locations.
    daily_average = (
        weather
        .groupby(
            "time",
            as_index=False,
        )
        .agg(
            avg_temperature=(
                "temperature_2m_mean",
                "mean",
            ),
            avg_precipitation=(
                "precipitation_sum",
                "mean",
            ),
            avg_snowfall=(
                "snowfall_sum",
                "mean",
            ),
        )
    )

    return daily_average

# ---------------------------------------------------------
# Latest safe ERA5 date
# ---------------------------------------------------------

def latest_era5_date():
    """
    Return a conservative latest date expected to be
    available from ERA5.

    ERA5 normally has around a five-day delay.
    A seven-day buffer is used to avoid requesting
    observations that have not yet been published.
    """

    return (
        pd.Timestamp.now(
            tz="UTC"
        )
        .normalize()
        .tz_localize(None)
        - pd.Timedelta(days=7)
    )


# ---------------------------------------------------------
# Weather summary for map
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def get_weather_map_summary(
    area_type,
    area_numbers,
    start_date,
    end_date,
    n_locations=3,
    random_state=42,
):
    """
    Calculate aggregated daily ERA5 weather values for
    areas displayed on the interactive map.

    Daily data are used instead of hourly observations
    because the map only requires aggregated values.
    """

    start_date = pd.Timestamp(
        start_date
    )

    end_date = pd.Timestamp(
        end_date
    )

    available_end = (
        latest_era5_date()
    )

    safe_end_date = min(
        end_date,
        available_end,
    )

    if start_date > safe_end_date:
        raise ValueError(
            "The selected period is newer than the "
            "currently available ERA5 data."
        )

    rows = []

    for area_number in area_numbers:

        locations = load_weather_coordinates(
            area_type=area_type,
            area_number=area_number,
            n_points=1000,
            random_state=random_state,
        )

        selected_points = (
            locations.sample(
                n=min(
                    n_locations,
                    len(locations),
                ),
                random_state=random_state,
            )
        )

        location_summaries = []

        for _, point in (
            selected_points.iterrows()
        ):

            params = {
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "start_date": (
                    start_date.strftime(
                        "%Y-%m-%d"
                    )
                ),
                "end_date": (
                    safe_end_date.strftime(
                        "%Y-%m-%d"
                    )
                ),
                "daily": (
                    "temperature_2m_mean,"
                    "precipitation_sum,"
                    "snowfall_sum"
                ),
                "models": "era5",
                "timezone": "UTC",
            }

            response = requests.get(
                ARCHIVE_URL,
                params=params,
                timeout=120,
            )

            if not response.ok:
                raise requests.exceptions.HTTPError(
                    (
                        f"Open-Meteo returned "
                        f"{response.status_code}: "
                        f"{response.text}"
                    ),
                    response=response,
                )

            data = response.json()

            daily = pd.DataFrame(
                data["daily"]
            )

            location_summaries.append(
                {
                    "avg_temperature": (
                        daily[
                            "temperature_2m_mean"
                        ].mean()
                    ),
                    "total_precipitation": (
                        daily[
                            "precipitation_sum"
                        ].sum()
                    ),
                    "total_snowfall": (
                        daily[
                            "snowfall_sum"
                        ].sum()
                    ),
                }
            )

            time.sleep(0.2)

        location_summary = pd.DataFrame(
            location_summaries
        )

        rows.append(
            {
                "area_number": area_number,
                "avg_temperature": (
                    location_summary[
                        "avg_temperature"
                    ].mean()
                ),
                "total_precipitation": (
                    location_summary[
                        "total_precipitation"
                    ].mean()
                ),
                "total_snowfall": (
                    location_summary[
                        "total_snowfall"
                    ].mean()
                ),
            }
        )

    return pd.DataFrame(rows)


# ---------------------------------------------------------
# Helper for yearly sampling frequency
# ---------------------------------------------------------

def _samples_per_year(index):
    """
    Estimate the number of observations per year.
    """

    step = (
        pd.Series(index)
        .diff()
        .median()
    )

    return (
        pd.Timedelta(
            days=365.25
        )
        / step
    )


# ---------------------------------------------------------
# DCT / SPC anomaly detection
# ---------------------------------------------------------

def spc_outliers(
    series,
    cutoff=12,
    n_sd=3,
    variable_label="Temperature",
    unit="°C",
):
    """
    Detect anomalies using DCT high-pass filtering and
    robust SPC boundaries.

    Works with temperature, precipitation and snowfall.
    """

    clean_series = (
        series
        .dropna()
        .sort_index()
    )

    x = clean_series.to_numpy(
        dtype=float
    )

    n = len(x)

    if n < 10:
        raise ValueError(
            "Not enough observations for SPC analysis."
        )

    samples_per_year = (
        _samples_per_year(
            clean_series.index
        )
    )

    k = int(
        round(
            2
            * n
            * cutoff
            / samples_per_year
        )
    )

    # Avoid removing all DCT coefficients.
    k = min(
        max(k, 1),
        n - 1,
    )

    coefficients = dct(
        x,
        type=2,
        norm="ortho",
    )

    coefficients[:k] = 0

    # Seasonally adjusted time variation (SATV)
    satv = idct(
        coefficients,
        type=2,
        norm="ortho",
    )

    seasonal_level = (
        x - satv
    )

    centre = np.median(
        satv
    )

    robust_sd = (
        1.4826
        * median_abs_deviation(
            satv
        )
    )

    # Fallback when the robust deviation is zero.
    if robust_sd == 0:
        robust_sd = np.std(
            satv
        )

    upper = (
        seasonal_level
        + centre
        + n_sd * robust_sd
    )

    lower = (
        seasonal_level
        + centre
        - n_sd * robust_sd
    )

    is_outlier = (
        (x > upper)
        | (x < lower)
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=[
            f"{variable_label} with SPC boundaries",
            "Seasonally Adjusted Time Variation (SATV)",
        ],
    )

    # Original weather series
    fig.add_trace(
        go.Scatter(
            x=clean_series.index,
            y=x,
            mode="lines",
            name=variable_label,
        ),
        row=1,
        col=1,
    )

    # Upper boundary
    fig.add_trace(
        go.Scatter(
            x=clean_series.index,
            y=upper,
            mode="lines",
            name="Upper SPC boundary",
            line=dict(
                dash="dash"
            ),
        ),
        row=1,
        col=1,
    )

    # Lower boundary
    fig.add_trace(
        go.Scatter(
            x=clean_series.index,
            y=lower,
            mode="lines",
            name="Lower SPC boundary",
            line=dict(
                dash="dash"
            ),
        ),
        row=1,
        col=1,
    )

    # Outliers
    fig.add_trace(
        go.Scatter(
            x=clean_series.index[
                is_outlier
            ],
            y=x[
                is_outlier
            ],
            mode="markers",
            name="Outliers",
        ),
        row=1,
        col=1,
    )

    # SATV
    fig.add_trace(
        go.Scatter(
            x=clean_series.index,
            y=satv,
            mode="lines",
            name="SATV",
        ),
        row=2,
        col=1,
    )

    fig.update_yaxes(
        title_text=unit,
        row=1,
        col=1,
    )

    fig.update_yaxes(
        title_text="Variation",
        row=2,
        col=1,
    )

    fig.update_xaxes(
        title_text="Time (UTC)",
        row=2,
        col=1,
    )

    fig.update_layout(
        height=650,
        hovermode="x unified",
        margin=dict(
            l=40,
            r=20,
            t=70,
            b=40,
        ),
    )

    summary = {
        "n_outliers": int(
            is_outlier.sum()
        ),
        "share": float(
            is_outlier.mean()
        ),
    }

    return fig, summary


def lof_outliers(
    series,
    contamination=0.01,
    n_neighbors=20,
    variable_label="Temperature",
    unit="°C",
):
    """
    Detect anomalies using Local Outlier Factor.

    Works with temperature, precipitation and snowfall.
    """

    clean_series = (
        series
        .dropna()
        .sort_index()
    )

    if len(clean_series) < 3:
        raise ValueError(
            "Not enough observations for LOF analysis."
        )

    # LOF requires fewer neighbours than observations.
    safe_neighbors = min(
        n_neighbors,
        len(clean_series) - 1,
    )

    X = (
        clean_series
        .to_numpy()
        .reshape(-1, 1)
    )

    lof = LocalOutlierFactor(
        n_neighbors=safe_neighbors,
        contamination=contamination,
    )

    labels = lof.fit_predict(
        X
    )

    is_anomaly = (
        labels == -1
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=clean_series.index,
            y=clean_series,
            mode="lines",
            name=variable_label,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=clean_series.index[
                is_anomaly
            ],
            y=clean_series[
                is_anomaly
            ],
            mode="markers",
            name="LOF anomalies",
        )
    )

    fig.update_layout(
        title=(
            f"LOF Anomalies – "
            f"{variable_label}"
        ),
        xaxis_title="Time (UTC)",
        yaxis_title=unit,
        hovermode="x unified",
        height=500,
        margin=dict(
            l=40,
            r=20,
            t=70,
            b=40,
        ),
    )

    summary = {
        "n_anomalies": int(
            is_anomaly.sum()
        ),
        "share": float(
            is_anomaly.mean()
        ),
    }

    return fig, summary


# Keep backwards compatibility with earlier notebook code.
def temperature_lof(
    series,
    contamination=0.01,
    n_neighbors=20,
):
    return lof_outliers(
        series,
        contamination=contamination,
        n_neighbors=n_neighbors,
        variable_label="Temperature",
        unit="°C",
    )