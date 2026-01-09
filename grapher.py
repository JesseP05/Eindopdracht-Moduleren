"""
    Graphing module used by some of my scripts.
    Author: Jesse Postma
    version 0.1
"""


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import seaborn as sns


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
        
        plt.figtext(0.5, 0.01, caption, ha='center')  
        plt.show()
        return

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
        
        sns.heatmap(heatmap_data, cmap='YlGnBu', cbar_kws={'label': heatmap_lbl}) # use seaborn for the heatmap
        plt.title(heatmap_title)
    plt.figtext(0.5, 0.001, caption, ha='center')
    plt.show()


def generic_bar_plot(times_dict: dict[int, int],
    x_label: str,
    y_label: str,
    p_title: str,
    p_label: str,
    no_x_ticks: int = 0,
    tick_step: int = 1,
    bar_color:str = 'orange',

):
    fig, ax = plt.subplots()
    ax.bar(list(times_dict.keys()), list(times_dict.values()), color=bar_color)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(p_title)
    ax.set_label(p_label)
    
    if no_x_ticks > 0 and tick_step >= 1: ax.set_xticks(range(0,no_x_ticks,tick_step))

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    print(f"This file {__file__} is not meant to be run directly.")
