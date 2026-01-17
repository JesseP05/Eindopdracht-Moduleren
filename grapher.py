"""
    Graphing module used by some of my scripts.
    Author: Jesse Postma
    version 0.3
"""

from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns


class SORT_TYPE(Enum):
    KEY_BASED = 1,
    VALUE_BASED = 2,
    NONE = 3,
    KEY_DESCENDING = 4,
    VALUE_DESCENDING = 5


def date_events_plot(
    date_dict: dict[str, float],
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    average_years: bool = False,
    tick_rotation: int = 45,
    heatmap: bool = False,
    heatmap_lbl: str = 'Average daily events',
    heatmap_title: str = 'Heatmap',
    caption = '',
    r_window: int = 30,
    rolling_avg: bool = True
):
    """Function that trivializes plotting number of events by date.

    Args:
        date_dict (dict[str, float]): Dictionary with date strings as keys and number of events as values
        x_label (str): x axis label
        y_label (str): y axis label
        
        p_title (str): plot title
        p_label (str): plot label
        
        caption (str): plot caption
        
        average_years (bool, optional): Whether or not to plot all years in the data, or plot the average of them all. Defaults to False.
        
        tick_rotation (int, optional): Rotation of the tick. Defaults to 45.
        
        heatmap (bool, optional): Whether or not to generate a heatmap alongside the plot. (is only generated with average_years). Defaults to False.
        
        r_window (int, optional): Window for the rolling average of the events. Defaults to 30 (one month).
        
        heatmap_lbl (str, optional): Label for the heatmap colorbar. Defaults to 'Average daily events'.
        
        heatmap_title (str, optional): Title of the heatmap plot. Defaults to 'Heatmap'.
        
    Returns:
        Figure: A matplotlib figure
    """    

    if (not average_years) and heatmap: # doesnt make sense together
        print('heatmap is set to True while average_years is not, beware that heatmaps won\'t be made when average_years is set to False.')

    df = pd.DataFrame(list(date_dict.items()), columns=['date', 'count'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    if not average_years:
        # regular plotting
        fig, ax = plt.subplots()
        ax.plot(df['date'], df['count'], label=p_label, color='skyblue', alpha=0.8)

        if rolling_avg:
            ax.plot(df['date'], df['count'].rolling(window=r_window, center=True).mean(), label=f'{r_window}-day trend', color='navy', linewidth=2)
        ax.set_title(p_title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True, which='both', linestyle='--', alpha=0.6)
        ax.legend()
        
        fig.text(0.5, 0.01, caption, ha='center')
        return fig

    # average over years plotting
    df['month'] = df['date'].dt.month # month
    df['day'] = df['date'].dt.day # weekday
    years = df['date'].dt.year.nunique() # how many years of data (use nunique instead of unique )

    daily_average = df.groupby(['month', 'day'])['count'].sum() / years # average incidnet per day over the years
    plot_avg = daily_average.reset_index()

    # create the data
    plot_avg['date'] = pd.to_datetime({'year':2000, 'month':plot_avg['month'], 'day':plot_avg['day']}) # 2000 dummy year
    plot_avg = plot_avg.sort_values(by='date')

    # create the plots
    plots = 1 if not heatmap else 2 # seperate plot for the heatmap
    fig, ax = plt.subplots(nrows=1, ncols=plots, figsize=(6 * plots, 6), layout='constrained')
    
    ax[0].plot(plot_avg['date'], plot_avg['count'], label=p_label, color='skyblue', alpha=0.8)

    if rolling_avg:
        ax[0].plot(plot_avg['date'], plot_avg['count'].rolling(window=r_window, center=True).mean(), label=f'{r_window}-day trend', color='navy', linewidth=2)

    ax[0].set_title(p_title)

    # remove dummy year again
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b %d')) 
    ax[0].xaxis.set_major_locator(mdates.MonthLocator())

    ax[0].set_xlabel(x_label)
    ax[0].set_ylabel(y_label)

    ax[0].tick_params(axis='x', rotation= tick_rotation)
    
    ax[0].grid(True, which='both', linestyle='--', alpha=0.6)
    ax[0].legend()

    if heatmap:
        plot_avg['Day of the week'] = plot_avg['date'].dt.day_name() # get dates weelday
        plot_avg['Week'] = plot_avg['date'].dt.isocalendar().week # get dates week nr
        
        # plot average structure:
        # date, count, month, day, day_otw, week
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        heatmap_data = plot_avg.pivot_table(index='Day of the week', columns='Week', values='count') # create pivot table
        heatmap_data = heatmap_data.reindex(days) # resort
        
        axes = sns.heatmap(heatmap_data, cmap='YlGnBu', cbar_kws={'label': heatmap_lbl}) # use seaborn for the heatmap
        axes.set_title(heatmap_title)
    fig.text(0.5, 0.001, caption, ha='center')
    return fig


def generic_bar_plot(frequency_dict: dict[int, int],
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    no_x_ticks: int = 0,
    tick_step: int = 1,
    tick_rotation = 0,
    color:str = 'orange',
    max_bars: int = 0,
    sort_type:SORT_TYPE = SORT_TYPE.VALUE_BASED,
    caption: str = ''
):
    """Makes a generic bar plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and label
        x_label (str): Lable for x axis
        y_label (str): Lable for y axis
        p_title (str): Plot title
        p_label (str): Plot label
        no_x_ticks (int, optional): No. of X ticks. Defaults to 0 (auto).
        tick_step (int, optional): Steps between ticks. Defaults to 1.
        tick_rotation (int, optional): Rotation for the x ticks. Defaults to 0.
        color (str, optional): Color of the bars. Defaults to 'orange'.
        max_bars (int, optional): Maximum number of bars to display, zero-indexed. Defaults to 0 (all).
        sort_type (SORT_TYPE, optional): sort type. Defaults to SORT_TYPE.NONE.
        caption (str, optional): plot caption. Defaults to ''.

    Returns:
        Figure: A matplotlib figure
    """
    fig, ax = plt.subplots()
    if sort_type == SORT_TYPE.VALUE_BASED: # no key based sorting because why would i
        frequency_dict = dict(sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True)) # sort based on value descending
    if max_bars > 0:
        trunc_dict = {}
        for index,(key, value) in enumerate(frequency_dict.items()):
            if index > max_bars:
                frequency_dict.clear()
                frequency_dict = trunc_dict
                break
            trunc_dict[key] = value
        
    ax.bar(list(frequency_dict.keys()), list(frequency_dict.values()), color=color)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(p_title)
    ax.set_label(p_label)
    ax.tick_params('x', rotation = tick_rotation)
    if no_x_ticks > 0 and tick_step >= 1: ax.set_xticks(range(0,no_x_ticks,tick_step))

    fig.tight_layout()
    return fig


def generic_line_plot(frequency_dict: dict[int, int],
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    no_x_ticks: int = 0,
    tick_step: int = 1,
    tick_rotation = 0,
    color = 'orange',
    max_bars: int = 0,
    sort_type = SORT_TYPE.NONE,
    caption: str = ''
):
    """Makes a generic line plot

    Args:
        frequency_dict (dict[int, int]): Dictionary with a count and label
        x_label (str): Label for x axis
        y_label (str): Label for y axis
        p_title (str): Plot title
        p_label (str): Plot label
        no_x_ticks (int, optional): No. of X ticks. Defaults to 0 (auto).
        tick_step (int, optional): Steps between ticks. Defaults to 1.
        tick_rotation (int, optional): Rotation for the x ticks. Defaults to 0.
        color (str, optional): Color of the line. Defaults to 'orange'.
        max_bars (int, optional): Ignored (signature parity with bar plots). Defaults to 0.
        sort_type (SORT_TYPE, optional): sort type. Defaults to SORT_TYPE.NONE.
        caption (str, optional): plot caption. Defaults to ''.
    Returns:
        Figure: A matplotlib figure
    """
    fig, ax = plt.subplots()
    
    if sort_type == SORT_TYPE.KEY_BASED:
        # sorting by key
        frequency_dict = {k: v for k, v in sorted(frequency_dict.items(), key=lambda item: item[0])}
    elif sort_type == SORT_TYPE.VALUE_BASED:
        frequency_dict = {k: v for k, v in sorted(frequency_dict.items(), key=lambda item: item[1])}
    
    ax.plot(list(frequency_dict.keys()), list(frequency_dict.values()), color = color)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(p_title)
    ax.set_label(p_label)
    ax.tick_params('x', rotation = tick_rotation)

    if no_x_ticks > 0 and tick_step >= 1: ax.set_xticks(range(0,no_x_ticks,tick_step))

    fig.text(0.5, 0.01, caption, ha='center')
    fig.tight_layout()
    return fig


class PLOT_TYPE(Enum):
    BAR = generic_bar_plot
    LINE = generic_line_plot


def plot(series: pd.Series,
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    no_x_ticks: int = 0,
    tick_step: int = 1,
    tick_rotation: int = 0,
    color: str = 'blue',
    caption: str = '',
    max_bars: int = 0,
    sort_type: SORT_TYPE = SORT_TYPE.NONE,
    plot_type: PLOT_TYPE = PLOT_TYPE.LINE
):
    """Plots a graph of a series

    Args:
        series (pd.Series): The data
        x_label (str): Label for x axis
        y_label (str): Label for y axis
        p_title (str): Plot title
        p_label (str): Plot label
        no_x_ticks (int, optional): No. of X ticks. Defaults to 0 (auto).
        tick_step (int, optional): Steps between ticks. Defaults to 1.
        tick_rotation (int, optional): Rotation for the x ticks. Defaults to 0.
        color (str, optional): Color of the line. Defaults to 'orange'.
        caption (str, optional): plot caption. Defaults to ''.
        max_bars (int, optional): Maximum number of bars to display, zero-indexed. Defaults to 0 (all).
        sort_type (SORT_TYPE, optional): sort type. Defaults to SORT_TYPE.NONE.
        plot_type (PLOT_TYPE, optional): Plot type. Defaults to PLOT_TYPE.LINE.

    Returns:
        Figure: A matplotlib figure
    Raises:
        NotImplementedError
    """    
    # handle sorting first
    match sort_type:
        case SORT_TYPE.KEY_BASED:
            series = series.sort_index()
        case SORT_TYPE.VALUE_BASED:
            series = series.sort_values()
        case SORT_TYPE.KEY_DESCENDING:
            series = series.sort_index(ascending = False)
        case SORT_TYPE.VALUE_DESCENDING:
            series = series.sort_values(ascending = False)
        case SORT_TYPE.NONE:
            pass

    frequency_dict = series.to_dict()
    return plot_type(
        frequency_dict, x_label, y_label, p_title, p_label,
        no_x_ticks, tick_step, tick_rotation, color, max_bars,
        SORT_TYPE.NONE, caption) # dont sort again


if __name__ == "__main__":
    print(f"This file {__file__} is not meant to be run directly.")
