# IND320 Project

Project for **IND320 – Data to Decision** at NMBU.

This repository contains the work for the IND320 compulsory
assignments. Compulsory Assignment 2 extends the reservoir dashboard
from Part 1 by introducing API-based data retrieval, Cassandra,
Apache Spark, MongoDB Atlas and cross-border electricity flow data.

## Compulsory Assignment 2

The project combines two energy-related datasets:

- Norwegian reservoir statistics from the **NVE Magasinstatistikk API**
- Cross-border physical electricity flows from the
  **ENTSO-E Transparency Platform API**

The project demonstrates a data pipeline from external APIs through
database storage and processing to an interactive Streamlit
application.

## Streamlit Application

The Streamlit application contains five pages:

- **Home** – introduction and navigation
- **Reservoir Data** – explore reservoir statistics retrieved from
  the NVE API
- **Reservoir Plots** – visualise reservoir measurements across
  geographical areas and time periods
- **Cross-Border Flows** – analyse physical electricity imports and
  exports between Norway and neighbouring areas
- **About** – information about the project, data sources and
  processing pipeline

### Live application

Add the URL of the Compulsory Assignment 2 Streamlit deployment here:

```text
https://ind320-project-hzlq3wqrpcpwplubvuksiy-compulsory-2.streamlit.app/
```

## Data Sources

### NVE Magasinstatistikk

Reservoir statistics are retrieved directly from the NVE
Magasinstatistikk API.

The Streamlit application no longer relies on the local CSV file used
in Compulsory Assignment 1.

The reservoir data include information such as:

- reservoir fill level
- storage capacity
- stored energy
- geographical area type and area number
- ISO year and week
- weekly changes in fill level

### ENTSO-E Transparency Platform

The ENTSO-E API is used to retrieve physical cross-border electricity
flow data for Norwegian bidding zones and neighbouring areas.

The dataset covers the latest two-year period and contains both import
and export observations for several cross-border connections.

## Data Pipeline

The project uses two main data flows.

### Reservoir data

```text
NVE Magasinstatistikk API
        ↓
Pandas
        ↓
Streamlit
```

### Cross-border electricity data

```text
ENTSO-E Transparency Platform API
        ↓
Cassandra
        ↓
Apache Spark
        ↓
MongoDB Atlas
        ↓
Streamlit
```

ENTSO-E XML responses are parsed and converted into structured
observations containing timestamps, physical flow in MW, direction and
calculated energy in MWh.

The data are stored locally in Cassandra before Spark is used to read,
clean and prepare the relevant columns. The processed dataset is then
stored in MongoDB Atlas and accessed directly by the Streamlit
application.

## Project Structure

```text
ind320-project/
├── data/
│   └── reservoirs.csv
├── modules/
│   ├── data_loader.py
│   └── mongodb_loader.py
├── notebooks/
│   ├── compulsory_1.ipynb
│   └── compulsory_2.ipynb
├── pages/
│   ├── 01_Home.py
│   ├── 02_Data.py
│   ├── 03_Plots.py
│   ├── 04_Cross_Border.py
│   └── 05_About.py
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

The CSV file in `data/` belongs to the Part 1 implementation.
Compulsory Assignment 2 retrieves reservoir data directly from the
NVE API instead.

## Setup

The project uses **Python 3.12** and `uv` for dependency management.

Clone the repository:

```bash
git clone https://github.com/VasiliiAnderson/ind320-project.git
cd ind320-project
```

Install the project dependencies:

```bash
uv sync
```

## Environment Variables

Sensitive credentials are not stored in GitHub.

For local development, create a `.env` file in the project root with:

```text
ENTSOE_TOKEN=your_entsoe_api_token
MONGODB_URI=your_mongodb_connection_string
```

The actual values must never be committed to the repository.

For Streamlit Community Cloud, the MongoDB connection string is stored
using Streamlit Secrets.

## Cassandra

Cassandra is used as the local database for ENTSO-E data and runs
locally using Docker.

The Cassandra instance is exposed on:

```text
localhost:9042
```

The notebook creates the required keyspace and tables and tests the
connection before the ENTSO-E data are written.

## Apache Spark

Apache Spark is used to:

- connect to Cassandra
- read ENTSO-E data from Cassandra
- select and prepare relevant columns
- aggregate data for analysis
- prepare the dataset before it is stored in MongoDB Atlas

The project uses the DataStax Spark Cassandra Connector.

On Windows, the local Spark setup also requires Java and a compatible
Hadoop configuration.

## MongoDB Atlas

MongoDB Atlas is used as the remote database for the processed
cross-border electricity dataset.

The Streamlit Cross-Border Flows page reads the required observations
directly from MongoDB instead of accessing Cassandra.

The MongoDB connection string is stored securely and is not included
in the repository.

## Run the Streamlit Application

Start the application locally with:

```bash
uv run streamlit run main.py
```

The application will then be available through the local Streamlit
URL shown in the terminal.

## Jupyter Notebook

The notebook for Compulsory Assignment 2 is located at:

```text
notebooks/compulsory_2.ipynb
```

Start JupyterLab with:

```bash
uv run jupyter lab
```

The notebook documents the complete workflow, including:

- NVE API retrieval
- Cassandra and Spark setup
- ENTSO-E API retrieval and XML parsing
- cross-border data preparation
- storage in Cassandra
- Spark filtering and analysis
- required visualisations
- MongoDB Atlas storage
- Streamlit integration
- AI usage
- project work log

## Security

API tokens, database credentials and connection strings must not be
committed to GitHub.

The project uses local `.env` variables during development and
Streamlit Secrets for the deployed application.