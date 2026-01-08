"""
    Graphing module used by some of my scripts.
    Author: Jesse Postma
"""


import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

# TODO: add variables for labels, titles, colors, etc.

def date_events_plot(date_dict: dict[str, float], average_years : bool = False,
                    tick_rotation: int = 45, heatmap : bool= False, r_window: int = 30):
    """Function that trivializes plotting number of events by date.

    Args:
        date_dict (dict[str, float]): Dictionary with date strings as keys and number of events as values.
        average_years (bool, optional): Whether or not to plot all years in the data, or plot the average of them all. Defaults to False.
        tick_rotation (int, optional): Rotation of the tick. Defaults to 45.
        heatmap (bool, optional): Whether or not to generate a heatmap alongside the plot. (is only generated with average_years). Defaults to False.
        r_window (int, optional): Window for the rolling average of the events. Defaults to 30 (one month).
    """

    if (not average_years) and heatmap: # doesnt make sense together
        print('heatmap is set to True while average_years is not, beware that heatmaps won\'t be made when average_years is set to False.')

    df = pd.DataFrame(list(date_dict.items()), columns=['date', 'count'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by='date')

    if not average_years:
        # regular plotting
        fig, ax = plt.subplots()
        ax.plot(df['date'], df['count'], label='Daily Incidents', color='skyblue', alpha=0.8)

        ax.plot(df['date'], df['count'].rolling(window=30, center=True).mean(), label='30-day trend', color='navy', linewidth=2)
        ax.set_title('Daily incidents by date of occurrence')
        ax.set_xlabel('Date')
        ax.set_ylabel('No. of incidents')
        ax.grid(True, which='both', linestyle='--', alpha=0.6)
        ax.legend()
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

    fig, ax = plt.subplots()
    ax.plot(plot_avg['date'], plot_avg['count'], label='Average Daily Incidents', color='skyblue', alpha=0.8)

    ax.plot(plot_avg['date'], plot_avg['count'].rolling(window=r_window, center=True).mean(), label=f'{r_window}-day trend', color='navy', linewidth=2)

    ax.set_title(f'Average daily incidents over {years} years by date of occurrence')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d')) # remove dummy year again
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    ax.set_xlabel('Date')
    ax.set_ylabel('No. of incidents')

    ax.tick_params(axis='x', rotation= tick_rotation)

    ax.grid(True, which='both', linestyle='--', alpha=0.6)
    ax.legend()
    plt.show()

    # heatmap stuff   
    # add heatmap for day otw

if __name__ == "__main__":
    print(f"This file {__file__} is not meant to be run directly.")
