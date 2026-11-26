import pandas as pd


def prepare_correlation_data(
    reservoir_data,
    weather_data,
    area_type,
    area_number,
):
    """
    Prepare monthly reservoir and weather data
    for correlation analysis.
    """

    # -----------------------------------------------------
    # Reservoir data
    # -----------------------------------------------------

    reservoir = (
        reservoir_data[
            (
                reservoir_data["area_type"]
                == area_type
            )
            & (
                reservoir_data["area_number"]
                == area_number
            )
        ][
            [
                "date",
                "fill_level",
            ]
        ]
        .dropna()
        .sort_values("date")
        .copy()
    )

    reservoir_monthly = (
        reservoir
        .set_index("date")[
            "fill_level"
        ]
        .resample("ME")
        .last()
        .rename("fill_level")
        .to_frame()
    )

    # Monthly change in reservoir filling
    reservoir_monthly[
        "fill_change"
    ] = (
        reservoir_monthly[
            "fill_level"
        ].diff()
    )

    # -----------------------------------------------------
    # Weather data
    # -----------------------------------------------------

    weather = (
        weather_data
        .copy()
        .set_index("time")
    )

    weather_monthly = (
        weather
        .resample("ME")
        .agg(
            avg_temperature=(
                "avg_temperature",
                "mean",
            ),
            total_precipitation=(
                "avg_precipitation",
                "sum",
            ),
            total_snowfall=(
                "avg_snowfall",
                "sum",
            ),
        )
    )

    # Weather timestamps are UTC-aware.
    # Timezone is not required after monthly aggregation.
    if (
        weather_monthly.index.tz
        is not None
    ):
        weather_monthly.index = (
            weather_monthly.index
            .tz_localize(None)
        )

    # -----------------------------------------------------
    # Combine sources
    # -----------------------------------------------------

    combined = (
        reservoir_monthly
        .join(
            weather_monthly,
            how="inner",
        )
        .sort_index()
    )

    return combined


def sliding_window_correlation(
    data,
    weather_property,
    reservoir_property="fill_change",
    lag=1,
    window=12,
):
    """
    Calculate rolling correlation between a weather
    property and reservoir filling.

    Positive lag means that weather occurs before the
    reservoir observation.
    """

    if weather_property not in data.columns:
        raise ValueError(
            f"Unknown weather property: "
            f"{weather_property}"
        )

    if reservoir_property not in data.columns:
        raise ValueError(
            f"Unknown reservoir property: "
            f"{reservoir_property}"
        )

    if window < 3:
        raise ValueError(
            "Window length must be at least "
            "3 months."
        )

    result = data[
        [
            reservoir_property,
            weather_property,
        ]
    ].copy()

    result[
        "weather_lagged"
    ] = (
        result[
            weather_property
        ]
        .shift(lag)
    )

    result[
        "correlation"
    ] = (
        result[
            reservoir_property
        ]
        .rolling(window)
        .corr(
            result[
                "weather_lagged"
            ]
        )
    )

    return result.dropna(
        subset=[
            "weather_lagged",
            "correlation",
        ]
    )