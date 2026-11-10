from pathlib import Path
import time

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

    # ---------------------------------------------------------
    # Electricity areas: EL1 -> NO1, ..., EL5 -> NO5
    # ---------------------------------------------------------
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

        gdf = gpd.read_file(shapefiles[0])

        gdf["region"] = (
            gdf["budomr"]
            .astype(str)
            .str.replace(" ", "", regex=False)
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

    # ---------------------------------------------------------
    # Precipitation / reservoir regions
    # ---------------------------------------------------------
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

        gdf = gpd.read_file(shapefiles[0])

        # Mapping from Magasinstatistikk VASS areas
        # to NVE administrative regions.
        vass_mapping = {
            1: ["RS", "RØ"],
            2: ["RV"],
            3: ["RM", "RN"],
        }

        regions = vass_mapping[
            int(area_number)
        ]

        selected = gdf[
            gdf["REGION"].isin(regions)
        ]

        geometry = selected.geometry.union_all()
        crs = gdf.crs

    # ---------------------------------------------------------
    # Norway as a whole
    # ---------------------------------------------------------
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

        gdf = gpd.read_file(shapefiles[0])

        # Combine all NVE regions to represent Norway
        geometry = gdf.geometry.union_all()
        crs = gdf.crs

    else:
        raise ValueError(
            f"Unsupported area type: {area_type}"
        )

    # ---------------------------------------------------------
    # Sample locations inside selected polygon
    # ---------------------------------------------------------
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
        n=min(n_locations, len(locations)),
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
            "hourly": ",".join(WEATHER_VARIABLES),
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

        hourly = pd.DataFrame(data["hourly"])
        hourly["time"] = pd.to_datetime(
            hourly["time"]
        )

        hourly["location_id"] = location_id

        weather_frames.append(hourly)

        time.sleep(0.2)

    weather = pd.concat(
        weather_frames,
        ignore_index=True,
    )

    # Calculate regional hourly averages
    hourly_average = (
        weather
        .groupby("time", as_index=False)
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


def _samples_per_year(index):
    """Estimate number of observations per year."""

    step = pd.Series(index).diff().median()

    return pd.Timedelta(days=365.25) / step


def spc_outliers(
    series,
    cutoff=12,
    n_sd=3,
):
    """
    Detect precipitation outliers using DCT high-pass
    filtering and robust SPC boundaries.
    """

    x = series.to_numpy(dtype=float)
    n = len(x)

    samples_per_year = _samples_per_year(
        series.index
    )

    k = int(
        round(
            2 * n * cutoff / samples_per_year
        )
    )

    coefficients = dct(
        x,
        type=2,
        norm="ortho",
    )

    coefficients[:k] = 0

    # Seasonally adjusted variation
    satv = idct(
        coefficients,
        type=2,
        norm="ortho",
    )

    seasonal_level = x - satv

    centre = np.median(satv)

    robust_sd = (
        1.4826
        * median_abs_deviation(satv)
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

    fig, ax = plt.subplots(
        figsize=(11, 4)
    )

    ax.plot(
        series.index,
        x,
        linewidth=0.7,
        label="Precipitation",
    )

    ax.plot(
        series.index,
        upper,
        linestyle="--",
        linewidth=0.8,
        label="SPC boundaries",
    )

    ax.plot(
        series.index,
        lower,
        linestyle="--",
        linewidth=0.8,
    )

    ax.scatter(
        series.index[is_outlier],
        x[is_outlier],
        s=10,
        label="Outliers",
    )

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Precipitation (mm)")
    ax.legend()

    fig.tight_layout()

    summary = {
        "n_outliers": int(
            is_outlier.sum()
        ),
        "share": float(
            is_outlier.mean()
        ),
    }

    return fig, summary


def temperature_lof(
    series,
    contamination=0.01,
    n_neighbors=20,
):
    """
    Detect temperature anomalies using Local Outlier Factor.
    """

    X = series.to_numpy().reshape(-1, 1)

    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
    )

    labels = lof.fit_predict(X)

    is_anomaly = labels == -1

    fig, ax = plt.subplots(
        figsize=(11, 4)
    )

    ax.plot(
        series.index,
        series,
        linewidth=0.7,
        label="Temperature",
    )

    ax.scatter(
        series.index[is_anomaly],
        series[is_anomaly],
        s=15,
        label="LOF anomalies",
    )

    ax.set_xlabel("Time (UTC)")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()

    fig.tight_layout()

    summary = {
        "n_anomalies": int(
            is_anomaly.sum()
        ),
        "share": float(
            is_anomaly.mean()
        ),
    }

    return fig, summary