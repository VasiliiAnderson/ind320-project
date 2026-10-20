import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


def _get_mongodb_uri():
    """Get MongoDB URI from Streamlit secrets or local .env."""

    try:
        uri = st.secrets["MONGODB_URI"]
    except Exception:
        uri = os.getenv("MONGODB_URI")

    if not uri:
        raise RuntimeError(
            "MONGODB_URI is not configured."
        )

    return uri


@st.cache_resource
def get_mongo_collection():
    """Return the MongoDB collection used by the dashboard."""

    client = MongoClient(_get_mongodb_uri())

    database = client["ind320"]

    return database["entsoe_physical_flow"]


@st.cache_data(ttl=3600)
def get_connections():
    """Return available cross-border connections."""

    collection = get_mongo_collection()

    return sorted(
        collection.distinct("connection")
    )


@st.cache_data(ttl=3600)
def get_years(connection):
    """Return available years for a connection."""

    collection = get_mongo_collection()

    years = collection.distinct(
        "year",
        {"connection": connection},
    )

    return sorted(years)


@st.cache_data(ttl=3600)
def get_annual_totals(connection, year):
    """Return annual import/export energy totals."""

    collection = get_mongo_collection()

    pipeline = [
        {
            "$match": {
                "connection": connection,
                "year": year,
            }
        },
        {
            "$group": {
                "_id": "$direction",
                "total_mwh": {
                    "$sum": "$energy_mwh"
                },
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        },
    ]

    rows = list(
        collection.aggregate(pipeline)
    )

    return pd.DataFrame(
        [
            {
                "direction": row["_id"],
                "total_mwh": row["total_mwh"],
            }
            for row in rows
        ]
    )


@st.cache_data(ttl=3600)
def get_monthly_flow(
    connection,
    year,
    months,
):
    """Return physical-flow observations for selected months."""

    collection = get_mongo_collection()

    query = {
        "connection": connection,
        "year": year,
        "month": {
            "$in": list(months)
        },
    }

    projection = {
        "_id": 0,
        "timestamp_utc": 1,
        "direction": 1,
        "quantity_mw": 1,
    }

    rows = list(
        collection.find(
            query,
            projection,
        ).sort(
            "timestamp_utc",
            1,
        )
    )

    df = pd.DataFrame(rows)

    if not df.empty:
        df["timestamp_utc"] = pd.to_datetime(
            df["timestamp_utc"]
        )

    return df