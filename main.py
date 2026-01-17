"""
    Eindopdracht moduleren; Een visualisatie van reported crime in Los Angeles.

    Author: Jesse Postma
    Version: 0.4
"""


import pandas as pd
import streamlit as st

import helper, grapher
from grapher import SORT_TYPE, PLOT_TYPE


EXPECTED_FILES = ['Crime_Data_from_2020_to_Present.csv','criminal_codes.csv',
                    'LAPD_Reporting_District.csv', 'LAPD_Status_Codes.csv', 'mocodes.csv']


def parse_mocodes(cell, mapping) -> str:
    """Parses a mocode string eg: 1300 0344 1606 2032 to a list of translated mocode(s)

    Args:
        cell : pandas cell with mocodes
        mapping: dictionary for mocode -> discription of the mocode

    Returns:
        mocodes[str]: Translated values for the mocode(s)
    """
    if pd.isna(cell):
        return cell
    codes = cell.split(' ')
    codes = [int(code) for code in codes]
    translated = [str(mapping.get(c, c)) for c in codes]
    mocodes = ', '.join(translated)
    return mocodes


def process_data(files : list[str]) -> pd.DataFrame:
    """Load and process the data files.

    Args:
        files set(str): names of files in the data folder
    """
    # prepend data/ to filenames
    for i, org_file in enumerate(files):
        file = f'data/{org_file}'
        files[i] = file
    
    lapd_df = pd.read_csv(files[0], engine='pyarrow', dtype={'TIME OCC': str})

    lapd_df['DATE OCC'] = pd.to_datetime(lapd_df['DATE OCC'], format=r'%m/%d/%Y %I:%M:%S %p', errors='coerce') # fix formatting
    lapd_df['TIME OCC'] = lapd_df['TIME OCC'].str.zfill(4) # fill with leading zeros
    lapd_df = lapd_df.sort_values(by='DATE OCC') # sort by date of incident
    
    crim_cd_df = pd.read_csv(files[1], engine='pyarrow') # translation for criminal codes into classes
    rep_ds_df = pd.read_csv(files[2], engine='pyarrow') # gives info about bureau, type of unit
    stat_cd_df = pd.read_csv(files[3], engine='pyarrow') # translation for report status codes
    mcode_df = pd.read_csv(files[4], engine='pyarrow', dtype={'MO Code': int}) # information about what has reportedly happened in the event

    # Map criminal codes to classes
    crim_cd_df = crim_cd_df.drop_duplicates(subset=['Criminal Code'])

    # reparse reporting district to numeric and drop duplicates
    rep_ds_df['REPDIST'] = pd.to_numeric(rep_ds_df['REPDIST'])
    rep_ds_df = rep_ds_df.drop_duplicates(subset=['REPDIST'])
    
    # new column for authority instead of overwriting rpt dist no
    lapd_df['Authority Type'] = lapd_df['Rpt Dist No'] # adding a column for type of unit (eg. sheriff or police)
    
    # replace codes with descriptive values
    lapd_df = helper.dictionary_replace_csv(lapd_df, crim_cd_df, 'Criminal Code', 'Crm Cd', 'Class')
    lapd_df = helper.dictionary_replace_csv(lapd_df, rep_ds_df, 'REPDIST', 'Rpt Dist No', 'BUREAU')
    lapd_df = helper.dictionary_replace_csv(lapd_df, rep_ds_df, 'REPDIST', 'Authority Type', 'S_TYPE')
    lapd_df = helper.dictionary_replace_csv(lapd_df, stat_cd_df, 'status_code', 'Status', 'description')
    
    
    # mocode parsing is a bit harder because it can contain more than one code per cell
    # initialize a lookup map for mocodes
    mocode_map = dict(zip(mcode_df['MO Code'].astype(int), mcode_df['Description']))

    # parse mocodes to readable desription
    lapd_df['Mocodes Readable'] = lapd_df['Mocodes'].apply(parse_mocodes, args=(mocode_map,)) # trailing comma because of tuple req
    
    # add racial mapping
    race_mapping = {
    'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian',
    'F': 'Filipino', 'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican',
    'I': 'American Indian/Alaskan Native', 'J': 'Japanese', 'K': 'Korean',
    'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander', 'S': 'Samoan',
    'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
    }

    lapd_df['Vict Descent'] = lapd_df['Vict Descent'].map(race_mapping)

    return lapd_df


def graph_dates(dates: list[str]):
    """Plot average number of incidents by date of occurrence.

    Args:
        dates (list[str]): List of date strings
    
    Returns:
        Figure: The matplotlib figure object
    """
    dates_dict = {}
    for date in dates:
        try:
            dates_dict[date] = dates_dict.setdefault(date, 0) + 1
        except Exception:
            print(f'Invalid date format: {date}')
            continue
    return grapher.date_events_plot(dates_dict, 
                             x_label='Date', 
                             y_label='Avg No. of Incidents', 
                             p_title='Daily incidents by date of occurrence', 
                             p_label='Average daily incidents',
                             heatmap=True, 
                             heatmap_lbl='Avg No. of Incidents', 
                             heatmap_title ='Average Daily Activity Heatmap (Day of Week vs. Week of Year)',
                             caption = '',
                             average_years=True, tick_rotation=45, r_window=30)


def graph_times(times: list[str]):
    """Plot number of incidents by time of occurrence.

    Args:
        times (list[str]): List of time strings
    
    Returns:
        Figure: The matplotlib figure object
    """
    times_dict = {}
    for time in times:
        try:
            hour = int(time[:2]) # get hour from time string
            times_dict[hour] = times_dict.setdefault(hour, 0) + 1
        except Exception:
            print(f'Invalid time format: {time}')
            continue
    return grapher.generic_bar_plot(times_dict,
                             x_label='Hour of the day',
                             y_label='Total Number of Incidents',
                             p_title='Incidents by time of occurrence',
                             p_label='Total Incidents',
                             no_x_ticks=24,
                             tick_step=2)


def graph_dangerous_areas(areas: list[str], num_areas: int =10):
    """Graph total number of events per area, sorted descending

    Args:
        areas (list[str]): List of areas from the dataset
        num_areas (int, optional): Number of top areas to display, zero-indexed. Defaults to 10.

    Returns:
        Figure: The matplotlib figure object
    """    
    area_dict = {}
    for area in areas:
        try:
            area_dict[area] = area_dict.setdefault(area, 0) + 1
        except Exception:
            print(f'Invalid area format: {area}')
            continue
    return grapher.generic_bar_plot(area_dict,
                             x_label='Area',
                             y_label='Total Number of Incidents',
                             p_title=f'Incidents by top {num_areas} areas',
                             p_label='Total Incidents',
                             no_x_ticks=0,
                             tick_step=1,
                             tick_rotation = 65,
                             color='#f08080',
                             max_bars=num_areas,
                             sort_type=SORT_TYPE.VALUE_BASED)


def graph_vict_age(ages: pd.Series):
    """Bins ages into ranges and returns figure.

    Args:
        ages (pd.Series): Series of ages
    Returns:
        Figure: The matplotlib figure object
    """    
    bins = [0, 14, 21, 34, 44, 54, 64, ages.max()]
    labels = ['0-14', '15-21', '22-34', '35-44', '45-54', '55-64', '65+']
    binned_ages = pd.cut(ages, bins, labels=labels, ordered=True).dropna()

    counts = binned_ages.value_counts().sort_index()
    return grapher.plot(counts, 'Age range', 'No. of Incidents', 'Victim Age distribution','', color='#92BE49', plot_type=PLOT_TYPE.BAR)


def render_plots(figures: list):
    """Function that renders the streamlit page with predefined plots

    Args:
        figures (list): The matplotlib figures to render
    """    
    columns = st.slider('Amount of chart columns.',1,5,2,1)
    cols = st.columns(columns)

    for i, figure in enumerate(figures):
        current_col = cols[i % columns]
        with current_col:
            st.pyplot(figure)

def main():
    """
    Main Function that handles code calling and small logic.
    """

    helper.validate_project_structure(set(EXPECTED_FILES))

    data = process_data(EXPECTED_FILES)

    # predefine figure collection
    figures = []

    # Function calls for specific graph we want
    dates = data['DATE OCC'].astype(str).tolist()
    figures.append(graph_dates(dates)) # graph report count per day (switch between occ and rptd? prob just occ)

    times = data['TIME OCC'].tolist()
    figures.append(graph_times(times)) # graph incident occ count per time on hourly interval

    areas = data['AREA NAME'].tolist()
    figures.append(graph_dangerous_areas(areas, num_areas=15))

    figures.append(graph_vict_age(data['Vict Age']))

    with open('debug_out.txt', 'w') as f:
        data.head(150).to_string(f)

    render_plots(figures)

    # graph_charge() # TODO: bar chart probably


if __name__ == '__main__':
    main()
