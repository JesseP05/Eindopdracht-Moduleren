"""
    Graphing module used by some of my scripts.
    Author: Jesse Postma
    version 0.5
"""

__version__ = '0.5'


from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import contextily as ctx


class SortType(Enum):
    """Easily define sort types
    """
    KEY_BASED = 1
    VALUE_BASED = 2
    NONE = 3
    KEY_DESCENDING = 4
    VALUE_DESCENDING = 5


def location_heatmap(location_df: pd.DataFrame, title: str, caption: str = '',
                     xlabel: str = 'Longitude', ylabel: str = 'Latitude', min_count: int = 200):
    """Plot locations onto a map with hex tiles with a color ramp to show count of points.

    Args:
        location_df (pd.DataFrame): Dataframe with LAT and LON columns.
        title (str): Title of the plot
        caption (str, optional): Caption for the plot. Defaults to ''.
        xlabel (str, optional): Label for the x-axis. Defaults to 'Longitude'.
        ylabel (str, optional): Label for the y-axis. Defaults to 'Latitude'.
        min_count (int, optional): Minimum count of points to display in a hexbin. Defaults to 200.
    Returns:
        plt.Figure: The figure containing the plot.
    """
    fig, ax = plt.subplots(figsize=(10,10))

    location_df = location_df[location_df != 0] # remove 0,0 coords
    long = location_df['LON']
    lati = location_df['LAT']
    hb = ax.hexbin(x=long, y=lati, gridsize=50, cmap='inferno', mincnt=min_count, alpha=0.7)
    # Colorbar to explain density
    cb = fig.colorbar(hb, ax=ax, shrink=0.5)
    cb.set_label('Count')

    # Background map
    ctx.add_basemap(ax, crs='EPSG:4326', source=ctx.providers.OpenStreetMap.Mapnik)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    fig.text(0.5, 0.01, caption, ha='center')

    return fig


def simple_heatmap(
    heatmap_data: pd.DataFrame,
    xlabel: str,
    ylabel: str,
    ax: plt.Axes = None,
    x_tick_step: int = 1,
    color_map: str = 'YlGnBu',
    heatmap_title: str = 'Heatmap'
):
    """Create a heatmap using matplotlib.

    Args:
        heatmap_data (pd.DataFrame): Pivot table with data to plot
        xlabel (str): Label for x axis
        ylabel (str): Label for y axis
        ax (plt.Axes): Existing axes to use instead of new. Defaults to None.
        x_tick_step (int, optional): Step size for x ticks. Defaults to 1.
        color_map (str, optional): Colormap to use. Defaults to 'YlGnBu'.
        heatmap_title (str, optional): Title of the heatmap. Defaults to 'Heatmap'.

    Returns:
        plt.Axes: The preexisting axes now containing the heatmap
        plt.Figure: The figure containing the heatmap (if ax isnt provided)
    """
    fig = None
    if ax is None:
        fig, ax = plt.subplots()
    im = ax.imshow(heatmap_data.values, cmap=color_map, aspect='auto')


    ax.set_xticks(range(0,len(heatmap_data.columns), x_tick_step))
    ax.set_xticklabels(heatmap_data.columns[0::x_tick_step])
    ax.set_yticks(range(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)

    # Add the colorbar
    _ = ax.figure.colorbar(im, ax=ax)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(heatmap_title)

    return ax if not fig else fig


def date_series(
    plot_data: pd.DataFrame,
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    heatmap_data: pd.DataFrame = None,
    tick_rotation: int = 45,
    heatmap: bool = False,
    heatmap_title: str = 'Heatmap',
    heatmap_xlabel: str = '',
    heatmap_ylabel: str = '',
    caption: str = '',
    r_window: int = 30,
    rolling_avg: bool = True,
    grid: bool = True
):
    """Plot date series with optional heatmap.

    Args:
        plot_data (pd.DataFrame): DataFrame with 'date' and 'count' columns
        x_label (str): x axis label
        y_label (str): y axis label
        p_title (str): plot title
        p_label (str): plot label
        heatmap_data (pd.DataFrame, optional): Pivot table for heatmap. Defaults to None.
        tick_rotation (int, optional): Rotation of the tick. Defaults to 45.
        heatmap (bool, optional): Whether or not to generate a heatmap. Defaults to False.
        heatmap_title (str, optional): Title of the heatmap plot. Defaults to 'Heatmap'.
        caption (str, optional): plot caption. Defaults to ''.
        r_window (int, optional): Window for the rolling average. Defaults to 30.
        rolling_avg (bool, optional): Whether to show rolling average. Defaults to True.
        grid (bool, optional): Whether or not to show grid lines. Defaults to True.
    Returns:
        Figure: The matplotlib figure
    """

    if heatmap and heatmap_data is None:
        print('Warning: heatmap=True but no heatmap_data provided.')
        heatmap = False

    # create the plots
    plots = 1 if not heatmap else 2
    fig, ax = plt.subplots(nrows=1, ncols=plots, figsize=(6 * plots, 6), layout='constrained')

    # make ax a list so its indexable
    if not heatmap:
        ax = [ax]

    ax[0].plot(plot_data['date'], plot_data['count'], label=p_label, color='skyblue', alpha=0.8)

    if rolling_avg:
        r_average = plot_data['count'].rolling(window=r_window, center=True).mean()
        r_label = f'{r_window}-day trend'
        ax[0].plot(plot_data['date'], r_average, label=r_label, color='navy', linewidth=2)

    ax[0].set_title(p_title)

    # Format date axis
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax[0].xaxis.set_major_locator(mdates.MonthLocator())

    ax[0].set_xlabel(x_label)
    ax[0].set_ylabel(y_label)

    ax[0].tick_params(axis='x', rotation=tick_rotation)
    plt.setp(ax[0].get_xticklabels(), ha='right', rotation_mode='anchor')

    if grid:
        ax[0].grid(True, which='both', linestyle='--', alpha=0.6)
    ax[0].legend()

    if heatmap:
        simple_heatmap(heatmap_data,
                       xlabel=heatmap_xlabel,
                       ylabel=heatmap_ylabel,
                       ax=ax[1], x_tick_step=2, heatmap_title=heatmap_title)
    fig.text(0.5, 0.001, caption, ha='center')
    return fig


def simple_bar_plt(frequency_dict: dict[int, int],
    x_label: str,
    y_label: str,
    p_title: str,
    x_max: int = 0,
    tick_step: int = 1,
    tick_rotation: int = 0,
    color: str = 'orange',
    sort_type: SortType = SortType.VALUE_BASED,
    caption: str = '',
    grid: bool = False,
    grid_direction: str = 'both',
    **_
):
    """Makes a simple bar plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and index
        x_label (str): Label for x axis
        y_label (str): Label for y axis
        p_title (str): Plot title
        x_max (int, optional): Max value for X axis ticks. Defaults to 0 (auto).
        tick_step (int, optional): Steps between x ticks. Defaults to 1.
        tick_rotation (int, optional): Rotation for the x ticks. Defaults to 0.
        color (str, optional): Color of the bars. Defaults to 'orange'.
        sort_type (SortType, optional): sort type. Defaults to SortType.VALUE_BASED.
        caption (str, optional): plot caption. Defaults to ''.
        grid (bool, optional): Whether or not to show grid lines. Defaults to False.
        **_: Additional arguments (ignored).

    Returns:
        Figure: A matplotlib figure
    """
    fig, ax = plt.subplots()
    if sort_type == SortType.VALUE_BASED: # no key based sorting because why would i
        items = frequency_dict.items()
        frequency_dict = dict(sorted(items, key=lambda item: item[1], reverse=True))

    ax.bar(list(frequency_dict.keys()), list(frequency_dict.values()), color=color)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(p_title)
    ax.tick_params('x', rotation=tick_rotation)
    plt.setp(ax.get_xticklabels(), ha='right', rotation_mode='anchor') # set alignment

    if x_max > 0 and tick_step >= 1:
        ax.set_xticks(range(0, x_max, tick_step))
    if grid:
        ax.grid(True, axis=grid_direction, linestyle='--', alpha=0.6)

    fig.text(0.5, 0.01, caption, ha='center')
    fig.tight_layout()
    return fig


def simple_line_plt(frequency_dict: dict[int, int],
    x_label: str,
    y_label: str,
    p_title: str,
    x_max: int = 0,
    tick_step: int = 1,
    tick_rotation: int = 0,
    color: str = 'orange',
    sort_type: SortType = SortType.NONE,
    caption: str = '',
    grid: bool = False,
    grid_direction: str = 'both',
    **_
):
    """Makes a simple line plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and index
        x_label (str): Label for x axis
        y_label (str): Label for y axis
        p_title (str): Plot title
        x_max (int, optional): Max value for X axis ticks. Defaults to 0 (auto).
        tick_step (int, optional): Steps between x ticks. Defaults to 1.
        tick_rotation (int, optional): Rotation for the x ticks. Defaults to 0.
        color (str, optional): Color of the line. Defaults to 'orange'.
        sort_type (SortType, optional): sort type. Defaults to SortType.NONE.
        caption (str, optional): plot caption. Defaults to ''.
        grid (bool, optional): Whether or not to show grid lines. Defaults to False.
        **_: Additional arguments (ignored).
    Returns:
        Figure: A matplotlib figure
    """
    fig, ax = plt.subplots()

    if sort_type == SortType.KEY_BASED:
        # sorting by key
        frequency_dict = dict(sorted(frequency_dict.items(), key=lambda item: item[0]))
    elif sort_type == SortType.VALUE_BASED:
        frequency_dict = dict(sorted(frequency_dict.items(), key=lambda item: item[1]))

    ax.plot(list(frequency_dict.keys()), list(frequency_dict.values()), color = color)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(p_title)
    ax.tick_params('x', rotation=tick_rotation)
    plt.setp(ax.get_xticklabels(), ha='right', rotation_mode='anchor') # set alignment

    if x_max > 0 and tick_step >= 1:
        ax.set_xticks(range(0, x_max, tick_step))
    if grid:
        ax.grid(True, axis=grid_direction, linestyle='--', alpha=0.6)

    fig.text(0.5, 0.01, caption, ha='center')
    fig.tight_layout()
    return fig


def simple_pie_plt(frequency_dict: dict[int, int],
    x_label: str,
    p_title: str,
    color: list[str] = None,
    sort_type: SortType = SortType.NONE,
    caption: str = '',
    threshold: float = 0,
    use_other: bool = True,
    **_
):
    """Makes a simple pie plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and index
        x_label (str): Label for legend title
        p_title (str): Plot title
        color (list[str], optional): Colors of the pie. Defaults to auto.
        sort_type (SortType, optional): sort type. Defaults to SortType.NONE.
        caption (str, optional): plot caption. Defaults to ''.
        threshold (float, optional): Minimum percentage to be included. Defaults to 0.
        use_other (bool, optional): Should group small values into 'other'. Defaults to True.
        **_: Additional arguments (ignored).
    Returns:
        Figure: A matplotlib figure
    """
    fig, ax = plt.subplots()


    if sort_type == SortType.KEY_BASED:
        # sorting by key
        frequency_dict = dict(sorted(frequency_dict.items(), key=lambda item: item[0]))
    elif sort_type == SortType.VALUE_BASED:
        frequency_dict = dict(sorted(frequency_dict.items(), key=lambda item: item[1]))

    # calculate cutoff and group others
    total = sum(frequency_dict.values())
    for k, v in list(frequency_dict.items()):
        if (v / total) * 100 < threshold:
            if use_other:
                frequency_dict.setdefault('other', 0)
                frequency_dict['other'] += v
            del frequency_dict[k]

    indexes = list(frequency_dict.keys())
    values = list(frequency_dict.values())
    wedges, _, _ = ax.pie(values, labels=None, colors=color, autopct='%1.1f%%')

    # Use legend instead of inline labels
    ax.legend(wedges, indexes, title=x_label, loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_title(p_title)

    fig.text(0.5, 0.01, caption, ha='center')
    fig.tight_layout()
    return fig


class PlotType(Enum):
    """Easily define simple plot types
    """
    BAR = simple_bar_plt
    LINE = simple_line_plt
    PIE = simple_pie_plt


def plot(series: pd.Series,
    x_label: str,
    y_label: str,
    p_title: str,
    x_max: int = 0,
    tick_step: int = 1,
    tick_rotation: int = 0,
    color: str | list = 'blue',
    caption: str = '',
    sort_type: SortType = SortType.NONE,
    plot_type: PlotType = PlotType.LINE,
    threshold: float = 0,
    grid: bool = False,
    grid_direction: str = 'both',
    use_other: bool = True
):
    """Plots a graph of a series into one of the simple plot types.

    Args:
        series (pd.Series): The data
        x_label (str): Label for x axis
        y_label (str): Label for y axis
        p_title (str): Plot title
        x_max (int, optional): Max value for X axis ticks. Defaults to 0 (auto).
        tick_step (int, optional): Steps between x ticks. Defaults to 1.
        tick_rotation (int, optional): Rotation for the x ticks. Defaults to 0.
        color (str | list, optional): Color or sequence of colors. Defaults to 'blue'.
        caption (str, optional): plot caption. Defaults to ''.
        sort_type (SortType, optional): sort type. Defaults to SortType.NONE.
        plot_type (PlotType, optional): Plot type. Defaults to PlotType.LINE.
        threshold (float, optional): Minimum value to be included in the plot. Defaults to 0.
        grid (bool, optional): Whether or not to show grid lines. Defaults to False.
        grid_direction (str, optional): Direction of the grid lines. Defaults to 'both'.
        use_other (bool, optional): Group small values into 'other' (pie charts). Defaults to True.

    Returns:
        Figure: A matplotlib figure
    """
    # handle sorting first
    match sort_type:
        case SortType.KEY_BASED:
            series = series.sort_index()
        case SortType.VALUE_BASED:
            series = series.sort_values()
        case SortType.KEY_DESCENDING:
            series = series.sort_index(ascending = False)
        case SortType.VALUE_DESCENDING:
            series = series.sort_values(ascending = False)
        case SortType.NONE:
            pass

    if plot_type != PlotType.PIE and not isinstance(color, str):
        color = color[0]
    elif plot_type == PlotType.PIE and isinstance(color, str):
        color = None

    frequency_dict = series.to_dict()
    return plot_type(
        frequency_dict=frequency_dict,
        x_label=x_label,
        y_label=y_label,
        p_title=p_title,
        x_max=x_max,
        tick_step=tick_step,
        tick_rotation=tick_rotation,
        color=color,
        sort_type=SortType.NONE,
        caption=caption,
        threshold=threshold,
        grid=grid,
        grid_direction=grid_direction,
        use_other=use_other
    )


if __name__ == "__main__":
    print(f"This file {__file__} is not meant to be run directly.")
