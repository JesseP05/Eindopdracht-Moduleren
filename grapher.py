"""
    Graphing module used by some of my scripts.
    Author: Jesse Postma
"""


import matplotlib.pyplot as plt
from datetime import datetime


def graph_dates_bar(date_dict: dict[str, float], total_years : bool = False, tick_interval: int = 30, tick_rotation: int = 45, figsize: tuple[int, int] = (15,5)):
    """UGH FUCK MATPLOTLIB

    Args:
        date_dict (dict[str, float]): _description_
        total_years (bool, optional): _description_. Defaults to False.
        tick_interval (int, optional): _description_. Defaults to 30.
        tick_rotation (int, optional): _description_. Defaults to 45.
        figsize (tuple[int, int], optional): _description_. Defaults to (15,5).
    """
    if total_years:
        # average counts over years
        total_dict = {}
        for date_str, count in date_dict.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_day_str = date_obj.strftime("%m-%d")
            total_dict[month_day_str] = total_dict.setdefault(month_day_str, 0) + count
        date_dict = total_dict
        for k in date_dict:
            date_dict[k] = date_dict[k] / 1000

    fig, ax = plt.subplots(figsize=figsize)

    ax.bar(list(date_dict.keys()), list(date_dict.values()),  color='orange', edgecolor = 'black')

    ax.set_xlabel('Date')
    ax.set_ylabel('Number of incidents x1000')
    ax.set_title('Total number of incidents per date since 2020')

    ax.set_xticks(range(0, len(date_dict), tick_interval))
    ax.tick_params(axis='x', rotation=tick_rotation)
    ax.set_ylim(0, max(date_dict.values()) + 1)
    ax.set_xmargin(0.01)
    ax.grid(axis='y')

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    print(f"This file {__file__} is not meant to be run directly.")
