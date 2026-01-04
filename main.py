"""
Eindopdracht moduleren; Een visualisatie van reported crime in Los Angeles.

Author: Jesse Postma
Version: 0.1
"""


import numpy as np
import pandas as pd
import helper


# def graph_dates():

def process_data(files : list[str]):
    """Load and process the data files.

    Args:
        files set(str): filepaths
    """
    for i, org_file in enumerate(files):
        file = f'data/{org_file}'
        files[i] = file
    
    lapd_df = pd.read_csv(files[0], engine='pyarrow')
    crim_cd_df = pd.read_csv(files[1], engine='pyarrow') # translation for criminal codes into classes
    rep_ds_df = pd.read_csv(files[2], engine='pyarrow') # gives info about bureau, type of unit
    stat_cd_df = pd.read_csv(files[3], engine='pyarrow') # translation for report status codes
    mcode_df = pd.read_csv(files[4], engine='pyarrow') # information about what has reportedly happened in the event

    # Map criminal codes to classified spectrums
    #crim_cd_df['Criminal Code'] = pd.to_numeric(crim_cd_df['Criminal Code'])
    crim_cd_df = crim_cd_df.drop_duplicates(subset=['Criminal Code'])

    rep_ds_df['REPDIST'] = pd.to_numeric(rep_ds_df['REPDIST'])
    rep_ds_df = rep_ds_df.drop_duplicates(subset=['REPDIST'])
    
    lapd_df['Authority Type'] = lapd_df['Rpt Dist No'] # adding a column for type of unit (eg. sheriff or police)

    lapd_df = helper.dictionary_replace_csv(lapd_df, crim_cd_df, 'Criminal Code', 'Crm Cd', 'Class')
    lapd_df = helper.dictionary_replace_csv(lapd_df, rep_ds_df, 'REPDIST', 'Rpt Dist No', 'BUREAU')
    lapd_df = helper.dictionary_replace_csv(lapd_df, rep_ds_df, 'REPDIST', 'Authority Type', 'S_TYPE')
    lapd_df = helper.dictionary_replace_csv(lapd_df, stat_cd_df, 'status_code', 'Status', 'description') # adding more info to status description
    

    print(lapd_df['Status'].head())
    print(lapd_df['Mocodes'].head())

def main():
    """
    Main Function that handles code calling and small logic.
    """
    print('Validating project structure and available data..')
    expected_files = ['Crime_Data_from_2020_to_Present.csv','criminal_codes.csv',
                    'LAPD_Reporting_District.csv', 'LAPD_Status_Codes.csv', 'mocodes.csv']
    helper.validate_project_structure(set(expected_files))
    
    process_data(expected_files)
    
    # Function calls for specific graph we want
    # graph_dates() # graph report count per day (switch between occ and rptd? prob just occ)
    # graph_timep() # graph incident occ count per time on hourly interval
    # graph_dang_area() # bar chart for most dangerous areas -> count of rep/area (area name)
    # graph_victim_age() # bar chart
    # graph_charge() # bar chart


if __name__ == "__main__":
    main()
