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
    mocodes = ' '.join(translated)
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
    
    lapd_df = pd.read_csv(files[0], engine='pyarrow')
    lapd_df['DATE OCC'] = pd.to_datetime(lapd_df['DATE OCC'], format="%m/%d/%Y %I:%M:%S %p", errors='coerce') # fix formatting
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
    
    return lapd_df


def graph_dates(dates: list[str]):
    """_summary_

    Args:
        dates (list[str]): _description_
    """    
    dates_dict = {}
    for date in dates:
        try:
            dates_dict[date] = dates_dict.setdefault(date, 0) + 1
        except Exception as e:
            print(f"Invalid date format: {date}")
            continue
    grapher.graph_dates_bar(dates_dict, tick_interval=1, total_years=True, tick_rotation=90)


def main():
    """
    Main Function that handles code calling and small logic.
    """
    print('Validating project structure and available data..')
    expected_files = ['Crime_Data_from_2020_to_Present.csv','criminal_codes.csv',
                    'LAPD_Reporting_District.csv', 'LAPD_Status_Codes.csv', 'mocodes.csv']
    helper.validate_project_structure(set(expected_files))
    
    data = process_data(expected_files)
    
    # Function calls for specific graph we want
    dates = data['DATE OCC'].astype(str).tolist()
    graph_dates(dates) # graph report count per day (switch between occ and rptd? prob just occ)

    # graph_timep() # graph incident occ count per time on hourly interval
    # graph_dang_area() # bar chart for most dangerous areas -> count of rep/area (area name)
    # graph_victim_age() # bar chart
    # graph_charge() # bar chart


if __name__ == "__main__":
    main()
