# IND320 Project

Project for **IND320 – Data to Decision** at NMBU.

This repository contains the work for the first compulsory assignment, including a Jupyter Notebook and a multipage Streamlit application for exploring Norwegian reservoir data.

## Streamlit Application

The Streamlit application provides an interactive dashboard for exploring the reservoir dataset.

The application contains four pages:

- **Home** – introduction and navigation
- **Data** – overview of the imported dataset and first-month sparklines
- **Plots** – interactive visualisation of selected variables and time periods
- **About** – information about the project

Live application:

https://vasilii-ind320.streamlit.app/

## Project Structure

```text
ind320-project/
├── data/
│   └── reservoirs.csv
├── modules/
│   └── data_loader.py
├── notebooks/
│   └── compulsory_1.ipynb
├── pages/
│   ├── 01_Home.py
│   ├── 02_Data.py
│   ├── 03_Plots.py
│   └── 04_About.py
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

The project uses **Python 3.12** and `uv` for dependency management.

Clone the repository and move into the project directory:

```bash
git clone https://github.com/VasiliiAnderson/ind320-project.git
cd ind320-project
```

Install the project dependencies:

```bash
uv sync
```

## Run the Streamlit App

Start the application locally with:

```bash
uv run streamlit run main.py
```

The application will then be available in your browser.

## Jupyter Notebook

The notebook for the first compulsory assignment is located at:

```text
notebooks/compulsory_1.ipynb
```

Start JupyterLab with:

```bash
uv run jupyter lab
```

The notebook loads and explores the reservoir dataset using Pandas and Matplotlib.

## Data

The project currently reads reservoir data from:

```text
data/reservoirs.csv
```

The dataset contains information about reservoir fill levels, storage capacity, stored energy, geographical areas and time-related variables.

Data loading in the Streamlit application is cached using `st.cache_data`.