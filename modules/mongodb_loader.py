import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient


# Load environment variables from a local .env file when
# the application is run outside Streamlit Community Cloud.
load_dotenv()


def _get_mongodb_uri():
    """
    Retrieve the MongoDB connection string.

    Streamlit Secrets are used for the deployed application,
    while the local .env file provides the connection string
    during local development.
    """

    try:
        uri = st.secrets["MONGODB_URI"]
    except Exception:
        uri = os.getenv("MONGODB_URI")

    # Stop execution if no MongoDB connection string is available.
    if not uri:
        raise RuntimeError(
            "MONGODB_URI is not configured."
        )

    return uri


@st.cache_resource
def get_mongo_collection():
    """
    Return the MongoDB collection used by the dashboard.

    The database connection is cached as a Streamlit resource
    so a new MongoDB client is not created on every app rerun.
    """

    # Create a connection to MongoDB Atlas.
    client = MongoClient(_get_mongodb_uri())

    # Select the database used for the IND320 project.
    database = client["ind320"]

    # Return the collection containing the processed
    # ENTSO-E physical-flow observations.
    return database["entsoe_physical_flow"]


@st.cache_data(ttl=3600)
def get_connections():
    """
    Return the available cross-border connections.

    The result is cached for one hour because the underlying
    collection changes much less frequently than Streamlit reruns.
    """

    collection = get_mongo_collection()

    # Retrieve all distinct connection identifiers
    # and sort them for consistent display in Streamlit.
    return sorted(
        collection.distinct("connection")
    )


@st.cache_data(ttl=3600)
def get_years(connection):
    """
    Return the years available for a selected connection.

    Parameters
    ----------
    connection : str
        Name of the selected cross-border connection.
    """

    collection = get_mongo_collection()

    # Retrieve distinct years only for the selected connection.
    years = collection.distinct(
        "year",
        {"connection": connection},
    )

    return sorted(years)


@st.cache_data(ttl=3600)
def get_annual_totals(connection, year):
    """
    Calculate annual import and export energy totals.

    MongoDB performs the aggregation before the small result
    is returned to Streamlit.
    """

    collection = get_mongo_collection()

    # MongoDB aggregation pipeline:
    # 1. Keep only the selected connection and year.
    # 2. Group observations by import/export direction.
    # 3. Sum transferred energy in MWh.
    # 4. Sort the result by direction.
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

    # Execute the aggregation pipeline in MongoDB.
    rows = list(
        collection.aggregate(pipeline)
    )

    # Convert the small aggregation result to a Pandas
    # DataFrame for plotting in the Streamlit application.
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
    """
    Return physical-flow observations for selected months.

    Only the fields needed by the Streamlit line plot are
    retrieved from MongoDB.
    """

    collection = get_mongo_collection()

    # Filter the collection by connection, year and the
    # months selected by the user in the Streamlit interface.
    query = {
        "connection": connection,
        "year": year,
        "month": {
            "$in": list(months)
        },
    }

    # Limit the returned document fields to those needed
    # for the physical-flow visualisation.
    projection = {
        "_id": 0,
        "timestamp_utc": 1,
        "direction": 1,
        "quantity_mw": 1,
    }

    # Retrieve the matching observations and sort them
    # chronologically before converting them to Pandas.
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

    # Ensure timestamps use a Pandas datetime type before plotting.
    if not df.empty:
        df["timestamp_utc"] = pd.to_datetime(
            df["timestamp_utc"]
        )

    return df