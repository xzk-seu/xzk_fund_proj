import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from kats.consts import TimeSeriesData


def plot(
        data: TimeSeriesData,
        fcst: pd.DataFrame,
        include_history=False,
        title=None
):
    """plot method for forecasting models

    This method provides the plotting functionality for all forecasting models

    Args:
        data: `TimeSeriesData`, the historical time series data set
        fcst: forecasted results from forecasting models
        include_history: if include the historical data when plotting, default as False

    Returns:
        None. The method simply plots the results
        :param title:
    """
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(facecolor="w", figsize=(10, 6))
    # plt.title(title)
    fig.suptitle(title)
    ax = fig.add_subplot(111)
    ax.plot(pd.to_datetime(data.time), data.value, "k")

    last_date = data.time.max()
    steps = fcst.shape[0]
    freq = pd.infer_freq(data.time)
    dates = pd.date_range(start=last_date, periods=steps + 1, freq=freq)

    dates_to_plot = dates[dates != last_date]  # Return correct number of periods

    fcst_dates = dates_to_plot.to_pydatetime()

    if include_history:
        ax.plot(fcst.time, fcst.fcst, ls="-", c="#4267B2")

        if ("fcst_lower" in fcst.columns) and ("fcst_upper" in fcst.columns):
            ax.fill_between(
                fcst.time,
                fcst.fcst_lower,
                fcst.fcst_upper,
                color="#4267B2",
                alpha=0.2,
            )
    else:
        ax.plot(fcst_dates, fcst.fcst, ls="-", c="#4267B2")

        if ("fcst_lower" in fcst.columns) and ("fcst_upper" in fcst.columns):
            ax.fill_between(
                fcst_dates,
                fcst.fcst_lower,
                fcst.fcst_upper,
                color="#4267B2",
                alpha=0.2,
            )

    ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
    ax.set_xlabel(xlabel="time")
    # ax.set_ylabel(ylabel="y")
    fig.tight_layout()

    return fig
