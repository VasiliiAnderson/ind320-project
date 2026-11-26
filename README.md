# IND320 Project

Project for **IND320 – Data to Decision** at the Norwegian University of Life Sciences (NMBU).

This repository contains the work developed throughout the IND320 compulsory assignments. The project combines Norwegian reservoir, weather, electricity-market and exchange-rate data in an interactive Streamlit dashboard for exploration, analysis and forecasting.

## Streamlit Application

The application follows the workflow:

**Explore → Analyse → Predict**

### Explore

- **Map & Data Overview** – interactive geographical exploration of Norwegian reservoir and ERA5 weather data
- **Energy & Markets** – cross-border electricity flows and EUR/NOK and USD/NOK exchange rates

### Analyse

- **Seasonal Patterns** – STL decomposition and spectrogram analysis
- **Weather & Anomalies** – SATV/SPC and Local Outlier Factor for temperature, precipitation and snowfall
- **Weather–Reservoir Correlation** – sliding-window correlations with selectable weather variable, lag and window length

### Predict

- **Reservoir Forecast** – monthly reservoir filling forecasts using River SNARIMAX with selectable model parameters and exogenous variables

### Information

- **About** – project information, methods and data sources

## Live Application

https://vasilii-ind320.streamlit.app/

## Compulsory Assignment 4

Compulsory Assignment 4 extends the project with:

- EUR/NOK and USD/NOK exchange-rate data from Norges Bank
- investigation and handling of timezones across the different data sources
- monthly reservoir forecasting using River SNARIMAX
- testing of model parameters, training-history length, forecast horizon and exogenous variables
- sliding-window correlation analysis between weather and reservoir conditions
- an interactive GeoJSON map with reservoir and ERA5 weather overlays
- redesigned Streamlit navigation based on Explore → Analyse → Predict
- shared geographical selections using Streamlit session state
- interactive Plotly visualisations
- caching, loading indicators and error handling

## Data Sources

### NVE Magasinstatistikk

NVE reservoir statistics provide information about:

- reservoir filling level
- storage capacity
- stored energy
- weekly changes in filling level
- geographical area type and area number

### NVE Geographical Data

NVE shapefiles are used to represent Norwegian electricity price areas and water regions. The polygons are also used for geographical sampling of weather locations.

### Open-Meteo / ERA5

Historical weather observations are retrieved using the Open-Meteo Historical Weather API with ERA5 reanalysis data.

The project uses:

- temperature
- precipitation
- snowfall

Weather timestamps are requested and processed in UTC.

### ENTSO-E Transparency Platform

Physical cross-border electricity-flow data are retrieved from an existing project pipeline and stored in MongoDB for use in the Streamlit application.

The timestamps are represented in UTC.

### Norges Bank

The Norges Bank open data API is used to retrieve daily:

- EUR/NOK
- USD/NOK

exchange rates.

The exchange rates are aggregated to monthly averages for use as potential exogenous variables in reservoir forecasting.

## Analysis Methods

The project includes:

- DCT-based seasonal adjustment
- Statistical Process Control (SPC)
- Local Outlier Factor (LOF)
- STL decomposition
- spectrogram analysis
- sliding-window correlation
- River SNARIMAX forecasting

### Reservoir Forecasting

Reservoir filling level is forecast at monthly resolution.

Weekly reservoir observations are converted to month-end values, while ERA5 weather variables and Norges Bank exchange rates are aggregated to monthly resolution.

The SNARIMAX model can use:

- historical reservoir filling
- temperature
- precipitation
- snowfall
- EUR/NOK
- USD/NOK

as predictors.

Future weather variables use historical calendar-month averages, while future exchange rates use the latest observed value. These are treated as scenario assumptions rather than separate forecasts.

Raw SNARIMAX predictions are retained, while displayed reservoir filling forecasts are clipped to the physically valid interval `[0, 1]`.

## Project Structure

```text
ind320-project/
├── data/
│   ├── reservoirs.csv
│   └── shapefiles/
│
├── modules/
│   ├── area_selector.py
│   ├── correlation_analysis.py
│   ├── currency_loader.py
│   ├── data_loader.py
│   ├── forecasting.py
│   ├── map_utils.py
│   ├── mongodb_loader.py
│   ├── seasonal_analysis.py
│   └── weather_analysis.py
│
├── notebooks/
│   ├── compulsory_1.ipynb
│   ├── compulsory_2.ipynb
│   ├── compulsory_3.ipynb
│   └── compulsory_4.ipynb
│
├── pages/
│   ├── 01_Home.py
│   ├── 02_Map_Overview.py
│   ├── 04_Cross_Border.py
│   ├── 05_Seasonal_Analysis.py
│   ├── 06_Correlation.py
│   ├── 06_Weather_Analysis.py
│   ├── 07_Forecast.py
│   └── 07_About.py
│
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

## Compulsory Assignment 4 Notebook

The final notebook is located at:

```text
notebooks/compulsory_4.ipynb
```

It documents the Norges Bank API integration, timezone investigation, forecasting data preparation, SNARIMAX modelling and testing, sliding-window correlation analysis, Streamlit redesign, AI usage and project work log.

## Security

API tokens, database credentials and connection strings are not stored in the GitHub repository.

Local credentials are handled through environment variables, while Streamlit Community Cloud uses Streamlit Secrets where required.