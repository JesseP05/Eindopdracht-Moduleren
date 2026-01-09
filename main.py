"""
    Eindopdracht moduleren; Een visualisatie van reported crime in Los Angeles.

    Author: Jesse Postma
    Version: 0.2
"""


import numpy as np
import pandas as pd
from datetime import datetime
import helper, grapher


def parse_mocodes(cell, map):
    """Parses a mocode string eg: 1300 0344 1606 2032 to a list of translated mocode(s)

    Args:
        cell : pandas cell with mocodes
        map: dictionary for mocode -> discription of the mocode

    Returns:
        mocodes[str]: Translated values for the mocode(s)
    """
    if pd.isna(cell):
        return cell
    codes = cell.split(" ")
    codes = [int(code) for code in codes]
    translated = [str(map.get(c, c)) for c in codes]
    mocodes = ', '.join(translated)
    return mocodes


def process_data(files : list[str]):
    """Load and process the data files.

    Args:
        files set(str): names of files in the data folder
    """
    # prepend data/ to filenames
    for i, org_file in enumerate(files):
        file = f'data/{org_file}'
        files[i] = file
    
    lapd_df = pd.read_csv(files[0], engine='pyarrow', dtype={'TIME OCC': str})
    lapd_df['DATE OCC'] = pd.to_datetime(lapd_df['DATE OCC'], format=r"%m/%d/%Y %I:%M:%S %p", errors='coerce') # fix formatting
    lapd_df['TIME OCC'] = lapd_df['TIME OCC'].str.zfill(4) # fill with leading zeros
    lapd_df = lapd_df.sort_values(by='DATE OCC') # sort by date of incident
    
    crim_cd_df = pd.read_csv(files[1], engine='pyarrow') # translation for criminal codes into classes
    rep_ds_df = pd.read_csv(files[2], engine='pyarrow') # gives info about bureau, type of unit
    stat_cd_df = pd.read_csv(files[3], engine='pyarrow') # translation for report status codes
    mcode_df = pd.read_csv(files[4], engine='pyarrow', dtype={"MO Code": int}) # information about what has reportedly happened in the event

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
    mocode_map = dict(zip(mcode_df["MO Code"].astype(int), mcode_df["Description"]))
    # parse mocodes to readable desription
    lapd_df["Mocodes Readable"] = lapd_df["Mocodes"].apply(parse_mocodes, args=(mocode_map,)) # trailing comma because of tuple req
    
    # add racial clarification
    race_mapping = {
    'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian',
    'F': 'Filipino', 'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican',
    'I': 'American Indian/Alaskan Native', 'J': 'Japanese', 'K': 'Korean',
    'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander', 'S': 'Samoan',
    'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
    } # zo veel wtf

    lapd_df['Vict Descent'] = lapd_df['Vict Descent'].map(race_mapping)

    return lapd_df


def graph_dates(dates: list[str]):
    """Plot average number of incidents by date of occurrence.

    Args:
        dates (list[str]): List of date strings
    """
    dates_dict = {}
    for date in dates:
        try:
            dates_dict[date] = dates_dict.setdefault(date, 0) + 1
        except Exception as e:
            print(f"Invalid date format: {date}")
            continue
    grapher.date_events_plot(dates_dict, 
                             x_label='Date', 
                             y_label='Avg No. of Incidents', 
                             p_title='Daily incidents by date of occurrence', 
                             p_label='Average daily incidents',
                             heatmap=True, 
                             heatmap_lbl='Avg No. of Incidents', 
                             heatmap_title ='Average Daily Activity Heatmap (Day of Week vs. Week of Year)',
                             caption = 'Note: Reason for major spike(s) on january 1st(s) is a trait of the dataset..',
                             average_years=True, tick_rotation=45, r_window=30)


def graph_times(times: list[str]):
    """Plot number of incidents by time of occurrence.

    Args:
        times (list[str]): List of time strings
    """
    times_dict = {}
    for time in times:
        try:
            hour = int(time[:2]) # get hour from time string
            times_dict[hour] = times_dict.setdefault(hour, 0) + 1
        except Exception as e:
            print(f"Invalid time format: {time}")
            continue
    grapher.generic_bar_plot(times_dict,
                             x_label='Hour of the day',
                             y_label='Total Number of Incidents',
                             p_title='Incidents by time of occurrence',
                             p_label='Total Incidents',
                             no_x_ticks=24,
                             tick_step=2)


def main():
    """
    Main Function that handles code calling and small logic.
    """

    expected_files = ['Crime_Data_from_2020_to_Present.csv','criminal_codes.csv',
                    'LAPD_Reporting_District.csv', 'LAPD_Status_Codes.csv', 'mocodes.csv']
    helper.validate_project_structure(set(expected_files))
    
    data = process_data(expected_files)
    
    # Function calls for specific graph we want
    dates = data['DATE OCC'].astype(str).tolist()
    graph_dates(dates) # graph report count per day (switch between occ and rptd? prob just occ)

    times = data['TIME OCC'].tolist()
    graph_times(times) # graph incident occ count per time on hourly interval
    

    with open('debug_out.txt', 'w') as f:
        data.head(150).to_string(f)

    # graph_dang_area() # bar chart for most dangerous areas -> count of rep/area (area name)
    # graph_victim_age() # bar chart
    # graph_charge() # bar chart


if __name__ == "__main__":
    main()
