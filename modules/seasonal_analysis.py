import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import spectrogram
from statsmodels.tsa.seasonal import STL


def plot_stl(
    series,
    seasonal=13,
    trend=53,
    robust=True,
):
    """
    Perform STL decomposition of weekly reservoir filling-level data.
    """

    stl = STL(
        series,
        period=52,
        seasonal=seasonal,
        trend=trend,
        robust=robust,
    )

    result = stl.fit()

    # Create a compact layout that works well in Streamlit
    fig, axes = plt.subplots(
        4,
        1,
        figsize=(11, 8),
        sharex=True,
    )

    axes[0].plot(series.index, result.observed)
    axes[0].set_ylabel("Observed")

    axes[1].plot(series.index, result.trend)
    axes[1].set_ylabel("Trend")

    axes[2].plot(series.index, result.seasonal)
    axes[2].set_ylabel("Seasonal")

    axes[3].plot(series.index, result.resid)
    axes[3].set_ylabel("Residual")
    axes[3].set_xlabel("Date")

    fig.suptitle(
        "STL Decomposition of Reservoir Filling Level",
        fontsize=14,
    )

    fig.tight_layout()

    return fig


def plot_spectrogram(
    series,
    window_length=104,
    overlap=52,
):
    """
    Create a spectrogram of weekly reservoir filling-level data.

    Parameters
    ----------
    series : pd.Series
        Weekly filling-level observations.
    window_length : int
        Number of observations in each analysis window.
    overlap : int
        Number of overlapping observations between windows.

    Returns
    -------
    matplotlib.figure.Figure
        Spectrogram plot.
    """

    values = series.to_numpy(dtype=float)

    frequencies, times, power = spectrogram(
        values,
        fs=52,
        nperseg=window_length,
        noverlap=overlap,
    )

    fig, ax = plt.subplots(figsize=(11, 5))

    mesh = ax.pcolormesh(
        times,
        frequencies,
        power,
        shading="auto",
    )

    ax.set_title("Spectrogram of Reservoir Filling Level")
    ax.set_xlabel("Time (years from start)")
    ax.set_ylabel("Frequency (cycles per year)")
    ax.set_ylim(0, 5)

    fig.colorbar(
        mesh,
        ax=ax,
        label="Power",
    )

    fig.tight_layout()

    return fig