from io import StringIO

import pandas as pd
import requests
import streamlit as st


NB_API_URL = (
    "https://data.norges-bank.no/api/data/EXR"
)


@st.cache_data(ttl=3600)
def download_exchange_rates(
    currencies=("EUR", "USD"),
    start_date="2024-01-01",
    end_date="2024-12-31",
):
    """
    Download NOK exchange rates from the Norges Bank API.

    Parameters
    ----------
    currencies : tuple
        Currency codes to retrieve, e.g. ("EUR", "USD").
    start_date : str
        First date in YYYY-MM-DD format.
    end_date : str
        Last date in YYYY-MM-DD format.

    Returns
    -------
    pd.DataFrame
        Long-format exchange-rate data containing date,
        currency and exchange_rate.
    """

    frames = []

    for currency in currencies:

        series_key = (
            f"B.{currency}.NOK.SP"
        )

        url = (
            f"{NB_API_URL}/"
            f"{series_key}"
        )

        params = {
            "format": "csv",
            "startPeriod": start_date,
            "endPeriod": end_date,
            "locale": "en",
        }

        response = requests.get(
            url,
            params=params,
            timeout=60,
        )

        response.raise_for_status()

        df = pd.read_csv(
            StringIO(
                response.text
            ),
            sep=None,
            engine="python",
        )

        df.columns = [
            column
            .strip()
            .upper()
            for column in df.columns
        ]

        required_columns = {
            "TIME_PERIOD",
            "OBS_VALUE",
        }

        if not required_columns.issubset(
            df.columns
        ):
            raise ValueError(
                "Unexpected Norges Bank API response. "
                f"Columns returned: "
                f"{df.columns.tolist()}"
            )

        exchange_rate = (
            df[
                [
                    "TIME_PERIOD",
                    "OBS_VALUE",
                ]
            ]
            .copy()
        )

        exchange_rate.columns = [
            "date",
            "exchange_rate",
        ]

        exchange_rate["date"] = (
            pd.to_datetime(
                exchange_rate["date"]
            )
        )

        exchange_rate[
            "exchange_rate"
        ] = pd.to_numeric(
            exchange_rate[
                "exchange_rate"
            ],
            errors="coerce",
        )

        exchange_rate[
            "currency"
        ] = currency

        frames.append(
            exchange_rate
        )

    rates = pd.concat(
        frames,
        ignore_index=True,
    )

    return (
        rates
        .sort_values(
            [
                "date",
                "currency",
            ]
        )
        .reset_index(
            drop=True
        )
    )