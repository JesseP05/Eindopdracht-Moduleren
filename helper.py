"""
    Helper module used by Eindopdracht moduleren.
    Author: Jesse Postma
"""


import os
import pandas as pd


class DirectoryNotFoundError(Exception):
    """Custom exception for directories not found.

    Args:
        message : Explanation of the error.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def replace_csv_col(main_df, sub_df, tbindex_header, replace_header, replacing_header = None):
    """Function that handles mapping of pandas dataframes.

    Args:
        main_df (DataFrame): The dataframe that the map should be applied to.
        
        sub_df (DataFrame): The dataframe that contains mapping information.
        
        index_header (str): The column that the sub_df dataframe is indexed on.
        
        replace_header (str): The column in main_df which will be replaced.
        
        replacing_header (str, optional): Optional specific interest header. Defaults to None.

    Returns:
        DataFrame: Mapped main_df. 
    """
    if replacing_header:
        lookup_df = sub_df.set_index(tbindex_header)[replacing_header]
    else:
        lookup_df = sub_df.set_index(tbindex_header)
    main_df[replace_header] = main_df[replace_header].map(lookup_df)

    return main_df


def validate_project_structure(expected_files: set):
    """Validates the project structure to check if the data is present and in the right place.

    Args:
        expected_files (set): File names of files expected to be in the projects data folder.

    Raises:
        DirectoryNotFoundError: Error raised if the data dir is not found.
        FileNotFoundError: Error raised if any of the expected files are not found.
    """

    print('Validating project structure...')
    dirpath = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(dirpath, 'data')
    data_dir_exists = os.path.exists(data_dir)

    if not data_dir_exists:
        raise DirectoryNotFoundError('The "data" directory is missing from the project.')

    files = os.listdir(data_dir)
    validator = expected_files - set(files)

    if validator:
        print(f'Files missing: {validator}')
        raise FileNotFoundError(f'File {validator} not found..')
    print('Project structure successfully validated.')


def calculate_yearly_average(df: pd.DataFrame):
    """Calculate daily averages over years from date event data.
    
    Args:
        df (DataFrame): DataFrame with 'date' and 'count' columns.
    
    Returns:
        DataFrame: DataFrame with averaged data using a dummy year (2000).
    """
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    years = df['date'].dt.year.nunique()
    
    daily_average = df.groupby(['month', 'day'])['count'].sum() / years
    plot_avg = daily_average.reset_index()
    
    plot_avg['date'] = pd.to_datetime(
        {'year': 2000, 'month': plot_avg['month'], 'day': plot_avg['day']}
    )
    plot_avg = plot_avg.sort_values(by='date')
    return plot_avg


def prepare_heatmap_data(plot_avg: pd.DataFrame, use_rolling_avg: bool = False, r_window: int = 30):
    """Prepare data for a weekday/week heatmap.
    
    Args:
        plot_avg (pd.DataFrame): DataFrame with 'date' and 'count' columns.
        use_rolling_avg (bool, optional): Use rolling average. Defaults to False.
        r_window (int, optional): Window size for the rolling average. Defaults to 30.
    
    Returns:
        DataFrame: Table with days of week as index and weeks as columns
    """
    plot_avg['Day of the week'] = plot_avg['date'].dt.day_name()
    plot_avg['Week'] = plot_avg['date'].dt.isocalendar().week
    
    if use_rolling_avg:
        plot_avg['count'] = plot_avg['count'].rolling(window=r_window, center=True).mean()
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    heatmap_data = plot_avg.pivot_table(
        index='Day of the week',
        columns='Week',
        values='count'
    )
    heatmap_data = heatmap_data.reindex(days)
    return heatmap_data


if __name__ == "__main__":
    print(f"This file {__file__} is not meant to be run directly.")
