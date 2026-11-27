import numpy as np
import plotly.graph_objects as go

from plotly.subplots import make_subplots
from scipy.signal import spectrogram
from statsmodels.tsa.seasonal import STL


def plot_stl(
    series,
    seasonal=13,
    trend=53,
    robust=True,
):
    """
    Perform STL decomposition of weekly reservoir
    filling-level data and return an interactive
    Plotly figure.
    """

    stl = STL(
        series,
        period=52,
        seasonal=seasonal,
        trend=trend,
        robust=robust,
    )

    result = stl.fit()

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        subplot_titles=[
            "Observed",
            "Trend",
            "Seasonal",
            "Residual",
        ],
    )

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=result.observed,
            mode="lines",
            name="Observed",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=result.trend,
            mode="lines",
            name="Trend",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=result.seasonal,
            mode="lines",
            name="Seasonal",
        ),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=result.resid,
            mode="lines",
            name="Residual",
        ),
        row=4,
        col=1,
    )

    fig.update_layout(
        title=(
            "STL Decomposition of Reservoir Filling Level"
        ),
        height=750,
        hovermode="x unified",
        showlegend=False,
        margin=dict(
            l=40,
            r=20,
            t=80,
            b=40,
        ),
    )

    fig.update_xaxes(
        title_text="Date",
        row=4,
        col=1,
    )

    fig.update_yaxes(
        title_text="Fill level",
        row=1,
        col=1,
    )

    return fig


def plot_spectrogram(
    series,
    window_length=104,
    overlap=52,
):
    """
    Create an interactive spectrogram of weekly
    reservoir filling-level data.
    """

    values = series.to_numpy(
        dtype=float
    )

    frequencies, times, power = spectrogram(
        values,
        fs=52,
        nperseg=window_length,
        noverlap=overlap,
    )

    # Only frequencies relevant for seasonal
    # reservoir patterns are displayed.
    frequency_mask = (
        frequencies <= 5
    )

    frequencies = frequencies[
        frequency_mask
    ]

    power = power[
        frequency_mask,
        :
    ]

    fig = go.Figure(
        data=go.Heatmap(
            x=times,
            y=frequencies,
            z=power,
            colorbar=dict(
                title="Power"
            ),
            hovertemplate=(
                "Time: %{x:.2f} years"
                "<br>"
                "Frequency: %{y:.2f} cycles/year"
                "<br>"
                "Power: %{z:.4f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=(
            "Spectrogram of Reservoir Filling Level"
        ),
        xaxis_title=(
            "Time (years from start)"
        ),
        yaxis_title=(
            "Frequency (cycles per year)"
        ),
        height=520,
        margin=dict(
            l=40,
            r=20,
            t=70,
            b=40,
        ),
    )

    return fig