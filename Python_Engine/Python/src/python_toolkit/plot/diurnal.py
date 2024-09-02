"""Methods for plotting diurnal profiles from time-indexed data."""

import calendar
import textwrap

import matplotlib.collections as mcollections
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from ..bhom.analytics import bhom_analytics
from .utilities import create_title


@bhom_analytics()
def diurnal(
    series: pd.Series,
    ax: plt.Axes = None,
    period: str = "daily",
    **kwargs,
) -> plt.Axes:
    """Plot a profile aggregated across days in the specified timeframe.

    Args:
        series (pd.Series):
            A time-indexed Pandas Series object.
        ax (plt.Axes, optional):
            A matplotlib Axes object. Defaults to None.
        period (str, optional):
            The period to aggregate over. Must be one of "dailyy", "weekly", or "monthly". Defaults to "daily".
        **kwargs (Dict[str, Any], optional):
            Additional keyword arguments to pass to the matplotlib plotting function.
            legend (bool, optional):
                If True, show the legend. Defaults to True.

    Returns:
        plt.Axes:
            A matplotlib Axes object.
    """

    if ax is None:
        ax = plt.gca()

    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series passed is not datetime indexed.")

    show_legend = kwargs.pop("legend", True)

    # NOTE - no checks here for missing days, weeks, or months, it should be evident from the plot

    # obtain plotting parameters
    minmax_range = kwargs.pop("minmax_range", [0.0001, 0.9999])
    if minmax_range[0] > minmax_range[1]:
        raise ValueError("minmax_range must be increasing.")
    minmax_alpha = kwargs.pop("minmax_alpha", 0.1)

    quantile_range = kwargs.pop("quantile_range", [0.05, 0.95])
    if quantile_range[0] > quantile_range[1]:
        raise ValueError("quantile_range must be increasing.")
    if quantile_range[0] < minmax_range[0] or quantile_range[1] > minmax_range[1]:
        raise ValueError("quantile_range must be within minmax_range.")
    quantile_alpha = kwargs.pop("quantile_alpha", 0.3)

    color = kwargs.pop("color", "slategray")

    # resample to hourly to ensuure hour alignment
    # TODO - for now we only resample to hourly, but this could be made more flexible by allowing any subset of period
    series = series.resample("h").mean()

    # remove nan/inf
    series = series.replace([-np.inf, np.inf], np.nan).dropna()

    # Remove outliers
    series = series[
        (series >= series.quantile(minmax_range[0]))
        & (series <= series.quantile(minmax_range[1]))
    ]

    # group data
    if period == "daily":
        group = series.groupby(series.index.hour)
        target_idx = range(24)
        major_ticks = target_idx[::3]
        minor_ticks = target_idx
        major_ticklabels = [f"{i:02d}:00" for i in major_ticks]
    elif period == "weekly":
        group = series.groupby([series.index.dayofweek, series.index.hour])
        target_idx = pd.MultiIndex.from_product([range(7), range(24)])
        major_ticks = range(len(target_idx))[::12]
        minor_ticks = range(len(target_idx))[::3]
        major_ticklabels = []
        for i in target_idx:
            if i[1] == 0:
                major_ticklabels.append(f"{calendar.day_abbr[i[0]]}")
            elif i[1] == 12:
                major_ticklabels.append("")
    elif period == "monthly":
        group = series.groupby([series.index.month, series.index.hour])
        target_idx = pd.MultiIndex.from_product([range(1, 13, 1), range(24)])
        major_ticks = range(len(target_idx))[::12]
        minor_ticks = range(len(target_idx))[::6]
        major_ticklabels = []
        for i in target_idx:
            if i[1] == 0:
                major_ticklabels.append(f"{calendar.month_abbr[i[0]]}")
            elif i[1] == 12:
                major_ticklabels.append("")
    else:
        raise ValueError("period must be one of 'daily', 'weekly', or 'monthly'")

    samples_per_timestep = group.count().mean()
    ax.set_title(
        create_title(
            kwargs.pop("title", None),
            f"Average {period} diurnal profile (≈{samples_per_timestep:0.0f} samples per timestep)",
        )
    )

    # Get values to plot
    minima = group.min()
    lower = group.quantile(quantile_range[0])
    median = group.median()
    mean = group.mean()
    upper = group.quantile(quantile_range[1])
    maxima = group.max()

    # create df for re-indexing
    df = pd.concat(
        [minima, lower, median, mean, upper, maxima],
        axis=1,
        keys=["minima", "lower", "median", "mean", "upper", "maxima"],
    ).reindex(target_idx)

    # populate plot
    for n, i in enumerate(range(len(df) + 1)[::24]):
        if n == len(range(len(df) + 1)[::24]) - 1:
            continue
        # q-q
        ax.fill_between(
            range(len(df) + 1)[i : i + 25],
            (df["lower"].tolist() + [df["lower"].values[0]])[i : i + 24]
            + [(df["lower"].tolist() + [df["lower"].values[0]])[i : i + 24][0]],
            (df["upper"].tolist() + [df["upper"].values[0]])[i : i + 24]
            + [(df["upper"].tolist() + [df["upper"].values[0]])[i : i + 24][0]],
            alpha=quantile_alpha,
            color=color,
            lw=None,
            ec=None,
            label=f"{quantile_range[0]:0.0%}-{quantile_range[1]:0.0%}ile"
            if n == 0
            else "_nolegend_",
        )
        # q-extreme
        ax.fill_between(
            range(len(df) + 1)[i : i + 25],
            (df["lower"].tolist() + [df["lower"].values[0]])[i : i + 24]
            + [(df["lower"].tolist() + [df["lower"].values[0]])[i : i + 24][0]],
            (df["minima"].tolist() + [df["minima"].values[0]])[i : i + 24]
            + [(df["minima"].tolist() + [df["minima"].values[0]])[i : i + 24][0]],
            alpha=minmax_alpha,
            color=color,
            lw=None,
            ec=None,
            label="Range" if n == 0 else "_nolegend_",
        )
        ax.fill_between(
            range(len(df) + 1)[i : i + 25],
            (df["upper"].tolist() + [df["upper"].values[0]])[i : i + 24]
            + [(df["upper"].tolist() + [df["upper"].values[0]])[i : i + 24][0]],
            (df["maxima"].tolist() + [df["maxima"].values[0]])[i : i + 24]
            + [(df["maxima"].tolist() + [df["maxima"].values[0]])[i : i + 24][0]],
            alpha=minmax_alpha,
            color=color,
            lw=None,
            ec=None,
            label="_nolegend_",
        )
        # mean/median
        ax.plot(
            range(len(df) + 1)[i : i + 25],
            (df["mean"].tolist() + [df["mean"].values[0]])[i : i + 24]
            + [(df["mean"].tolist() + [df["mean"].values[0]])[i : i + 24][0]],
            c=color,
            ls="-",
            lw=1,
            label="Average" if n == 0 else "_nolegend_",
        )
        ax.plot(
            range(len(df) + 1)[i : i + 25],
            (df["median"].tolist() + [df["median"].values[0]])[i : i + 24]
            + [(df["median"].tolist() + [df["median"].values[0]])[i : i + 24][0]],
            c=color,
            ls="--",
            lw=1,
            label="Median" if n == 0 else "_nolegend_",
        )

    # format axes
    ax.set_xlim(0, len(df))
    ax.xaxis.set_major_locator(mticker.FixedLocator(major_ticks))
    ax.xaxis.set_minor_locator(mticker.FixedLocator(minor_ticks))
    ax.set_xticklabels(
        major_ticklabels,
        minor=False,
        ha="left",
    )
    if show_legend:
        ax.legend(
            bbox_to_anchor=(0.5, -0.2),
            loc=8,
            ncol=6,
            borderaxespad=0,
        )

    ax.set_ylabel(series.name)

    return ax


@bhom_analytics()
def stacked_diurnals(
    datasets: list[pd.Series], period: str = "monthly", **kwargs
) -> plt.Figure:
    """Create a matplotlib figure with stacked diurnal profiles.

    Args:
        datasets (list[pd.Series]):
            A list of time-indexed Pandas Series objects.
        period (str, optional):
            The period to aggregate over. Must be one of "dailyy", "weekly", or "monthly". Defaults to "monthly".
        **kwargs (Dict[str, Any], optional):
            Additional keyword arguments to pass to the matplotlib plotting function.
            colors (list[str], optional):
                A list of colors to use for the plots. Defaults to None, which uses the default diurnal color.

    Returns:
        plt.Figure:
            A matplotlib Figure object.
    """

    if len(datasets) <= 1:
        raise ValueError("stacked_diurnals requires at least two datasets.")

    fig, axes = plt.subplots(
        len(datasets), 1, figsize=(12, 2 * len(datasets)), sharex=True
    )

    for n, (ax, series) in enumerate(zip(axes, datasets)):
        if "colors" in kwargs:
            kwargs["color"] = kwargs["colors"][n]
        diurnal(series, ax=ax, period=period, **kwargs)
        ax.set_title(None)
        ax.get_legend().remove()
        ax.set_ylabel(textwrap.fill(ax.get_ylabel(), 20))

    handles, labels = axes[-1].get_legend_handles_labels()
    new_handles = []
    for handle in handles:
        if isinstance(handle, mcollections.PolyCollection):
            new_handles.append(
                mpatches.Patch(
                    color="slategray", alpha=handle.get_alpha(), edgecolor=None
                )
            )
        if isinstance(handle, mlines.Line2D):
            new_handles.append(
                mlines.Line2D(
                    (0,), (0,), color="slategray", linestyle=handle.get_linestyle()
                )
            )

    plt.legend(
        new_handles, labels, bbox_to_anchor=(0.5, -0.12), loc="upper center", ncol=4
    )

    fig.suptitle(
        create_title(
            kwargs.pop("title", None),
            f"Average {period} diurnal profile" + "s" if len(datasets) > 1 else "",
        ),
        x=fig.subplotpars.left,
        ha="left",
    )

    plt.tight_layout()

    return fig
