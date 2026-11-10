# IND320 Project

Project for **IND320 – Data to Decision** at NMBU.

This repository contains the work for the IND320 compulsory assignments.
The project has been developed progressively from reservoir data
exploration into an interactive energy and weather analysis dashboard.

## Compulsory Assignment 3

Compulsory Assignment 3 extends the existing Streamlit application with:

- geographical data from NVE shapefiles
- random sampling of locations within Norwegian regions
- historical ERA5 weather data from Open-Meteo
- precipitation outlier detection using DCT and Statistical Process Control
- temperature anomaly detection using Local Outlier Factor
- STL decomposition of reservoir filling levels
- spectrogram analysis
- shared geographical selection across Streamlit pages

## Streamlit Application

The Streamlit application contains seven pages:

- **Home** – introduction and navigation
- **Reservoir Data** – explore reservoir statistics from NVE
- **Reservoir Plots** – interactive reservoir visualisations
- **Seasonal Analysis** – STL decomposition and spectrogram
- **Weather Analysis** – precipitation/SPC and temperature/LOF analysis
- **Cross-Border Flows** – electricity imports and exports
- **About** – project information, data sources and methods

### Live application

https://vasilii-ind320.streamlit.app/

## Data Sources

### NVE Magasinstatistikk

Reservoir statistics are retrieved directly from the
NVE Magasinstatistikk API.

The data include:

- reservoir filling level
- storage capacity
- stored energy
- geographical area type and area number
- ISO year and week
- weekly changes in filling level

### NVE Geographical Data

NVE shapefiles are used to represent:

- Norwegian electricity bidding areas NO1–NO5
- NVE geographical regions used to construct the VASS areas

The geographical polygons are processed with GeoPandas and used to
sample reproducible weather locations.

### Open-Meteo

Historical hourly weather observations are retrieved from the
Open-Meteo Historical Weather API using the **ERA5 reanalysis model**.

The project retrieves:

- temperature
- precipitation
- snowfall

For the required analysis, weather data for NO3 during 2024 are used.

### ENTSO-E Transparency Platform

The ENTSO-E API is used to retrieve physical cross-border electricity
flow data for Norwegian bidding zones and neighbouring areas.

These data were introduced in Compulsory Assignment 2 and remain part
of the Streamlit application.

## Analysis Methods

### Precipitation Outliers

Average precipitation is analysed using a Discrete Cosine Transform
high-pass filter.

The seasonally adjusted variation is used together with robust
Statistical Process Control boundaries to identify outliers.

The DCT frequency cut-off and number of standard deviations are
configurable parameters.

### Temperature Anomalies

Temperature anomalies are detected using the
**Local Outlier Factor (LOF)** method.

The expected proportion of anomalies is configurable and defaults to 1%.

### STL Decomposition

Reservoir filling-level data are decomposed using
**Seasonal-Trend decomposition using LOESS (STL)**.

The application allows the user to control:

- seasonal smoother
- trend smoother
- robust fitting

### Spectrogram

A spectrogram is used to analyse how the frequency content of reservoir
filling-level data changes over time.

The window length and overlap are configurable.

## Data Pipelines

### Reservoir data

```text
NVE Magasinstatistikk API
        ↓
Pandas
        ↓
Analysis / Streamlit
```

### Weather data

```text
NVE shapefiles
        ↓
GeoPandas
        ↓
Sampled geographical locations
        ↓
Open-Meteo ERA5 API
        ↓
DCT / SPC / LOF
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

## Project Structure

```text
ind320-project/
├── data/
│   ├── reservoirs.csv
│   └── shapefiles/
│       ├── elspot/
│       └── nve_regions/
├── modules/
│   ├── area_selector.py
│   ├── data_loader.py
│   ├── mongodb_loader.py
│   ├── seasonal_analysis.py
│   └── weather_analysis.py
├── notebooks/
│   ├── compulsory_1.ipynb
│   ├── compulsory_2.ipynb
│   └── compulsory_3.ipynb
├── pages/
│   ├── 01_Home.py
│   ├── 02_Data.py
│   ├── 03_Plots.py
│   ├── 04_Cross_Border.py
│   ├── 05_About.py
│   ├── 05_Seasonal_Analysis.py
│   └── 06_Weather_Analysis.py
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

The project uses **Python 3.12** and `uv` for dependency management.

Clone the repository:

```bash
git clone https://github.com/VasiliiAnderson/ind320-project.git
cd ind320-project
```

Install dependencies:

```bash
uv sync
```

Run the Streamlit application:

```bash
uv run streamlit run main.py
```

Start JupyterLab:

```bash
uv run jupyter lab
```

## Jupyter Notebook

The notebook for Compulsory Assignment 3 is located at:

```text
notebooks/compulsory_3.ipynb
```

It documents:

- NVE geographical shapefiles
- random geographical sampling
- Open-Meteo ERA5 retrieval
- precipitation DCT/SPC analysis
- temperature LOF analysis
- STL decomposition
- spectrogram analysis
- Streamlit implementation
- AI usage
- project work log

## Security

API tokens, database credentials and connection strings are not stored
in the GitHub repository.

Local credentials are handled using environment variables, while
Streamlit Community Cloud uses Streamlit Secrets where required.