"""
    Graphing module used by some of my scripts.
    Author: Jesse Postma
    version 0.4
"""

__version__ = '0.4'


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
    cb.set_label('Count of Points')

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


def date_events_plot(
    date_dict: dict[str, float],
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    average_years: bool = False,
    tick_rotation: int = 45,
    heatmap: bool = False,
    heatmap_avg: bool = False,
    heatmap_title: str = 'Heatmap',
    caption: str = '',
    r_window: int = 30,
    rolling_avg: bool = True,
    grid: bool = True
):
    """Function that i should split up into parts because its a lot but im lazy.
    Function that trivializes plotting number of events by date.

    Args:
        date_dict (dict[str, float]): Dictionary with date strings as keys
        x_label (str): x axis label
        y_label (str): y axis label
        
        p_title (str): plot title
        p_label (str): plot label
        caption (str): plot caption
        
        average_years (bool, optional): Whether or not to plot the average. Defaults to False.
        
        tick_rotation (int, optional): Rotation of the tick. Defaults to 45.
        
        heatmap (bool, optional): Whether or not to generate a heatmap. Defaults to False.
        
        r_window (int, optional): Window for the rolling average. Defaults to 30 (one month).
        
        heatmap_avg (bool, optional): Show rolling average on heatmap. Defaults to False.
        
        heatmap_title (str, optional): Title of the heatmap plot. Defaults to 'Heatmap'.
        grid (bool, optional): Whether or not to show grid lines. Defaults to True.
    Returns:
        Figure: A matplotlib figure
    """

    if (not average_years) and heatmap: # doesnt make sense together
        print('Beware that heatmaps won\'t be made when average_years is set to False.')

    df = pd.DataFrame(list(date_dict.items()), columns=['date', 'count'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    if not average_years:
        # regular plotting
        fig, ax = plt.subplots()
        ax.plot(df['date'], df['count'], label=p_label, color='skyblue', alpha=0.8)

        if rolling_avg:
            r_average = df['count'].rolling(window=r_window, center=True).mean()
            r_label = f'{r_window}-day trend'
            ax.plot(df['date'], r_average, label=r_label, color='navy', linewidth=2)
        ax.set_title(p_title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if grid:
            ax.grid(True, which='both', linestyle='--', alpha=0.6)
        ax.legend()

        fig.text(0.5, 0.01, caption, ha='center')
        return fig

    # average over years plotting
    df['month'] = df['date'].dt.month # month
    df['day'] = df['date'].dt.day # dotm
    years = df['date'].dt.year.nunique() # how many years of data (use nunique instead of unique )

    daily_average = df.groupby(['month', 'day'])['count'].sum() / years # average by years
    plot_avg = daily_average.reset_index()

    # create the data
    plot_avg['date'] = pd.to_datetime(
        {'year':2000, 'month':plot_avg['month'], 'day':plot_avg['day']}
    ) # 2000 dummy year
    plot_avg = plot_avg.sort_values(by='date')

    # create the plots
    plots = 1 if not heatmap else 2 # seperate plot for the heatmap
    fig, ax = plt.subplots(nrows=1, ncols=plots, figsize=(6 * plots, 6), layout='constrained')

    ax[0].plot(plot_avg['date'], plot_avg['count'], label=p_label, color='skyblue', alpha=0.8)

    if rolling_avg:
        r_average = plot_avg['count'].rolling(window=r_window, center=True).mean()
        r_label = f'{r_window}-day trend'
        ax[0].plot(plot_avg['date'], r_average, label=r_label, color='navy', linewidth=2)

    ax[0].set_title(p_title)

    # remove dummy year again
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax[0].xaxis.set_major_locator(mdates.MonthLocator())

    ax[0].set_xlabel(x_label)
    ax[0].set_ylabel(y_label)

    ax[0].tick_params(axis='x', rotation=tick_rotation)
    plt.setp(ax[0].get_xticklabels(), ha='right', rotation_mode='anchor') # set alignment

    if grid:
        ax[0].grid(True, which='both', linestyle='--', alpha=0.6)
    ax[0].legend()

    if heatmap:
        plot_avg['Day of the week'] = plot_avg['date'].dt.day_name() # get dates weekday
        plot_avg['Week'] = plot_avg['date'].dt.isocalendar().week # get dates week nr

        # plot average structure:
        # date, count, month, day, day_otw, week
        if heatmap_avg:
            plot_avg['count'] = plot_avg['count'].rolling(window=r_window, center=True).mean()

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        heatmap_data = plot_avg.pivot_table(index='Day of the week',
                                            columns='Week',
                                            values='count') # create pivot table

        heatmap_data = heatmap_data.reindex(days) # re-sort

        simple_heatmap(heatmap_data,
                       xlabel='Week',
                       ylabel='Day of the week',
                       ax=ax[1], x_tick_step=2, heatmap_title=heatmap_title)
    fig.text(0.5, 0.001, caption, ha='center')
    return fig


def simple_bar_plot(frequency_dict: dict[int, int],
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
    **kwargs
):
    """Makes a simple bar plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and label
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
        **kwargs: Additional arguments (ignored).

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


def simple_line_plot(frequency_dict: dict[int, int],
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
    **kwargs
):
    """Makes a simple line plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and label
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
        **kwargs: Additional arguments (ignored).
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


def simple_pie_plot(frequency_dict: dict[int, int],
    x_label: str,
    p_title: str,
    color: list[str] = None,
    sort_type: SortType = SortType.NONE,
    caption: str = '',
    threshold: float = 0,
    use_other: bool = True,
    **kwargs
):
    """Makes a simple pie plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and label
        x_label (str): Label for legend title
        p_title (str): Plot title
        color (list[str], optional): Colors of the pie. Defaults to auto.
        sort_type (SortType, optional): sort type. Defaults to SortType.NONE.
        caption (str, optional): plot caption. Defaults to ''.
        threshold (float, optional): Minimum percentage to be included. Defaults to 0.
        use_other (bool, optional): Should group small values into 'other'. Defaults to True.
        **kwargs: Additional arguments (ignored).
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
    """Easily define plot types
    """
    BAR = simple_bar_plot
    LINE = simple_line_plot
    PIE = simple_pie_plot


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
