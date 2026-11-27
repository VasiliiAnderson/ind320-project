import pandas as pd
import streamlit as st

from river import time_series

from modules.currency_loader import (
    download_exchange_rates,
)
from modules.weather_analysis import (
    download_daily_weather,
    latest_era5_date,
)


WEATHER_FEATURES = {
    "avg_temperature",
    "total_precipitation",
    "total_snowfall",
}

CURRENCY_FEATURES = {
    "eur_nok",
    "usd_nok",
}


# ---------------------------------------------------------
# Monthly weather data
# ---------------------------------------------------------

@st.cache_data(ttl=3600)
def download_monthly_weather(
    area_type,
    area_number,
    start_date,
    end_date,
    n_locations=5,
    random_state=42,
):
    """
    Download daily ERA5 weather observations and aggregate
    them to monthly values for forecasting.

    The underlying daily-weather function retrieves multiple
    geographical locations in a single Open-Meteo request to
    reduce API usage.
    """

    start_date = pd.Timestamp(
        start_date
    )

    end_date = pd.Timestamp(
        end_date
    )

    safe_end = min(
        end_date,
        latest_era5_date(),
    )

    if start_date > safe_end:

        raise ValueError(
            "The selected forecast training period "
            "is newer than the available ERA5 data."
        )


    daily_weather = (
        download_daily_weather(
            area_type=area_type,
            area_number=area_number,
            start_date=(
                start_date.strftime(
                    "%Y-%m-%d"
                )
            ),
            end_date=(
                safe_end.strftime(
                    "%Y-%m-%d"
                )
            ),
            n_locations=n_locations,
            random_state=random_state,
        )
    )


    regional_daily = (
        daily_weather
        .set_index("time")
        .sort_index()
    )


    # Aggregate daily regional weather to months.
    monthly = (
        regional_daily
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


    # Reservoir and currency data use timezone-naive
    # month-end indexes.
    if (
        monthly.index.tz
        is not None
    ):

        monthly.index = (
            monthly.index
            .tz_localize(None)
        )


    return monthly


# ---------------------------------------------------------
# Prepare forecasting dataset
# ---------------------------------------------------------

def prepare_forecast_data(
    reservoir_data,
    area_type,
    area_number,
    start_date,
    end_date,
    selected_features,
    n_weather_locations=5,
):
    """
    Combine monthly reservoir, weather and currency
    observations for SNARIMAX forecasting.
    """

    selected_features = list(
        selected_features
    )


    # -----------------------------------------------------
    # Reservoir target
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


    data = (
        reservoir_monthly.copy()
    )


    # -----------------------------------------------------
    # Weather features
    # -----------------------------------------------------

    weather_features = [
        feature
        for feature in selected_features
        if feature in WEATHER_FEATURES
    ]


    if weather_features:

        weather_monthly = (
            download_monthly_weather(
                area_type=area_type,
                area_number=area_number,
                start_date=start_date,
                end_date=end_date,
                n_locations=(
                    n_weather_locations
                ),
            )
        )


        data = data.join(
            weather_monthly,
            how="inner",
        )


    # -----------------------------------------------------
    # Currency features
    # -----------------------------------------------------

    currency_features = [
        feature
        for feature in selected_features
        if feature in CURRENCY_FEATURES
    ]


    if currency_features:

        exchange_rates = (
            download_exchange_rates(
                currencies=(
                    "EUR",
                    "USD",
                ),
                start_date=(
                    pd.Timestamp(
                        start_date
                    )
                    .strftime(
                        "%Y-%m-%d"
                    )
                ),
                end_date=(
                    pd.Timestamp(
                        end_date
                    )
                    .strftime(
                        "%Y-%m-%d"
                    )
                ),
            )
        )


        currency_wide = (
            exchange_rates
            .pivot(
                index="date",
                columns="currency",
                values="exchange_rate",
            )
            .rename(
                columns={
                    "EUR": "eur_nok",
                    "USD": "usd_nok",
                }
            )
        )


        currency_monthly = (
            currency_wide
            .resample("ME")
            .mean()
        )


        data = data.join(
            currency_monthly,
            how="inner",
        )


    required_columns = (
        ["fill_level"]
        + selected_features
    )


    data = (
        data[
            required_columns
        ]
        .dropna()
        .sort_index()
    )


    return data


# ---------------------------------------------------------
# Future exogenous assumptions
# ---------------------------------------------------------

def create_future_features(
    training_data,
    future_dates,
    selected_features,
):
    """
    Create assumed future exogenous variables.

    Weather:
        historical average for the corresponding month.

    Currency:
        most recent observed exchange rate.
    """

    selected_features = list(
        selected_features
    )


    future = pd.DataFrame(
        index=future_dates
    )


    for feature in selected_features:

        if feature in WEATHER_FEATURES:

            climatology = (
                training_data[
                    feature
                ]
                .groupby(
                    training_data.index.month
                )
                .mean()
            )


            overall_mean = (
                training_data[
                    feature
                ].mean()
            )


            future[feature] = [
                climatology.get(
                    date.month,
                    overall_mean,
                )
                for date
                in future_dates
            ]


        elif feature in CURRENCY_FEATURES:

            future[feature] = (
                training_data[
                    feature
                ]
                .dropna()
                .iloc[-1]
            )


    return future


# ---------------------------------------------------------
# Future SNARIMAX forecast
# ---------------------------------------------------------

def forecast_future_snarimax(
    data,
    selected_features=(),
    history_years=5,
    horizon_months=6,
    p=3,
    d=1,
    q=1,
    m=12,
    sp=1,
    sd=1,
    sq=1,
):
    """
    Train a River SNARIMAX model and forecast
    future monthly reservoir filling levels.
    """

    selected_features = list(
        selected_features
    )


    required_columns = (
        ["fill_level"]
        + selected_features
    )


    model_data = (
        data[
            required_columns
        ]
        .dropna()
        .sort_index()
        .copy()
    )


    history_months = (
        history_years * 12
    )


    training_data = (
        model_data.tail(
            history_months
        )
    )


    if len(training_data) < 24:

        raise ValueError(
            "At least 24 monthly observations "
            "are required for forecasting."
        )


    model = time_series.SNARIMAX(
        p=p,
        d=d,
        q=q,
        m=m,
        sp=sp,
        sd=sd,
        sq=sq,
    )


    # Sequential online training.
    for _, row in (
        training_data.iterrows()
    ):

        x = (
            row[
                selected_features
            ].to_dict()
            if selected_features
            else None
        )


        model.learn_one(
            y=row[
                "fill_level"
            ],
            x=x,
        )


    # -----------------------------------------------------
    # Future dates
    # -----------------------------------------------------

    future_dates = pd.date_range(
        start=(
            training_data.index.max()
            + pd.offsets.MonthEnd(1)
        ),
        periods=horizon_months,
        freq="ME",
    )


    # -----------------------------------------------------
    # Future exogenous values
    # -----------------------------------------------------

    future_features = (
        create_future_features(
            training_data=training_data,
            future_dates=future_dates,
            selected_features=(
                selected_features
            ),
        )
    )


    if selected_features:

        future_x = (
            future_features[
                selected_features
            ]
            .to_dict(
                orient="records"
            )
        )

    else:

        future_x = None


    predictions = model.forecast(
        horizon=horizon_months,
        xs=future_x,
    )


    forecast = (
        future_features.copy()
    )


    forecast[
        "predicted_fill_level_raw"
    ] = predictions


    # Reservoir filling is physically bounded.
    forecast[
        "predicted_fill_level"
    ] = (
        forecast[
            "predicted_fill_level_raw"
        ]
        .clip(
            lower=0,
            upper=1,
        )
    )


    return (
        forecast,
        training_data,
        model,
    )