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

    Parameters
    ----------
    series : pd.Series
        Weekly filling-level observations.
    seasonal : int
        Length of the seasonal smoother.
    trend : int
        Length of the trend smoother.
    robust : bool
        Whether robust fitting should be used.

    Returns
    -------
    matplotlib.figure.Figure
        STL decomposition plot.
    """

    stl = STL(
        series,
        period=52,
        seasonal=seasonal,
        trend=trend,
        robust=robust,
    )

    result = stl.fit()

    fig = result.plot()
    fig.set_size_inches(11, 8)
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