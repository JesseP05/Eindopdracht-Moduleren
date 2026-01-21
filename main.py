"""
    Eindopdracht moduleren; Een visualisatie van reported crime in Los Angeles.

    Author: Jesse Postma
    Version: 0.9
"""


import pandas as pd
import streamlit as st

import helper
import grapher
from grapher import SortType, PlotType


EXPECTED_FILES = ['Crime_Data_from_2020_to_Present.csv','criminal_codes.csv',
                    'LAPD_Reporting_District.csv', 'LAPD_Status_Codes.csv', 'mocodes.csv']

RACE_MAPPING = {
    'A': 'Other Asian', 'B': 'Black', 'C': 'Chinese', 'D': 'Cambodian',
    'F': 'Filipino', 'G': 'Guamanian', 'H': 'Hispanic/Latin/Mexican',
    'I': 'American Indian/Alaskan Native', 'J': 'Japanese', 'K': 'Korean',
    'L': 'Laotian', 'O': 'Other', 'P': 'Pacific Islander', 'S': 'Samoan',
    'U': 'Hawaiian', 'V': 'Vietnamese', 'W': 'White', 'X': 'Unknown', 'Z': 'Asian Indian'
    }


@st.cache_data
def process_data(files: list[str]) -> pd.DataFrame:
    """Load and process the data files.

    Args:
        files set(str): names of files in the data folder
    """
    filepaths = []
    # prepend data/ to filenames
    for org_file in files:
        file = f'data/{org_file}'
        filepaths.append(file)

    lapd_df = pd.read_csv(filepaths[0], engine='pyarrow', dtype={'TIME OCC': str})

    # fix formatting
    date_form = r'%m/%d/%Y %I:%M:%S %p'
    lapd_df['DATE OCC'] = pd.to_datetime(lapd_df['DATE OCC'], format=date_form)
    lapd_df['TIME OCC'] = lapd_df['TIME OCC'].str.zfill(4) # fill with leading zeros
    lapd_df = lapd_df.sort_values(by='DATE OCC')

    crim_cd_df = pd.read_csv(filepaths[1], engine='pyarrow') # translation for criminal codes
    rep_ds_df = pd.read_csv(filepaths[2], engine='pyarrow') # gives info about bureau, type of unit
    stat_cd_df = pd.read_csv(filepaths[3], engine='pyarrow') # translation for report status codes

    # Map criminal codes to classes
    crim_cd_df = crim_cd_df.drop_duplicates(subset=['Criminal Code'])

    # reparse reporting district to numeric and drop duplicates
    rep_ds_df['REPDIST'] = pd.to_numeric(rep_ds_df['REPDIST'])
    rep_ds_df = rep_ds_df.drop_duplicates(subset=['REPDIST'])

    # new column for authority instead of overwriting rpt dist no
    lapd_df['Authority Type'] = lapd_df['Rpt Dist No']

    # replace codes with descriptive values
    lapd_df = helper.replace_csv_col(lapd_df, crim_cd_df, 'Criminal Code', 'Crm Cd', 'Class')
    lapd_df = helper.replace_csv_col(lapd_df, rep_ds_df, 'REPDIST', 'Rpt Dist No', 'BUREAU')
    lapd_df = helper.replace_csv_col(lapd_df, rep_ds_df, 'REPDIST', 'Authority Type', 'S_TYPE')
    lapd_df = helper.replace_csv_col(lapd_df, stat_cd_df, 'status_code', 'Status', 'description')

    # add racial mapping
    lapd_df['Vict Descent'] = lapd_df['Vict Descent'].map(RACE_MAPPING)

    return lapd_df


def graph_dates(dates: pd.Series, caption: str):
    """Plot average number of incidents by date of occurrence.

    Args:
        dates (pd.Series): Series of date strings
        caption (str): Caption for the figure
    
    Returns:
        tuple: (Figure, caption)
    """
    counts = dates.value_counts().sort_index()
    
    # Create DataFrame directly from Series
    df = counts.reset_index()
    df.columns = ['date', 'count']
    
    plot_avg = helper.calculate_yearly_average(df)
    heatmap_data = helper.prepare_heatmap_data(plot_avg, use_rolling_avg=False, r_window=30)
    
    return grapher.date_series(
                            plot_data=plot_avg,
                            heatmap_data=heatmap_data,
                            x_label='Date',
                            y_label='Avg No. of Incidents',
                            p_title='Daily incidents by date of occurrence',
                            p_label='Daily Incidents',
                            heatmap=True,
                            heatmap_title='Average Daily Activity Heatmap',
                            heatmap_xlabel='Week',
                            heatmap_ylabel='Day of the week',
                            caption='',
                            tick_rotation=45,
                            r_window=30), caption


def graph_times(times: pd.Series, caption: str):
    """Plot number of incidents by hour of occurrence.

    Args:
        times (pd.Series): Series of time strings
        caption (str): Caption for the figure
    
    Returns:
        tuple: (Figure, caption)
    """
    hours = times.str[:2].astype(int)
    counts = hours.value_counts().sort_index()
    return grapher.plot(counts,
                             x_label='Hour of the day',
                             y_label='Total Number of Incidents',
                             p_title='Incidents by hour of occurrence',
                             x_max=24,
                             tick_step=2,
                             color= "#eccf98",
                             plot_type=PlotType.BAR), caption


def graph_dangerous_areas(areas: pd.Series, caption: str, num_areas: int = 10):
    """Graph total number of events per area, sorted descending

    Args:
        areas (pd.Series): Series of areas from the dataset
        caption (str): Caption for the figure
        num_areas (int, optional): Number of top areas to display. Zero-indexed. Defaults to 10.

    Returns:
        tuple: (Figure, caption)
    """
    counts = areas.value_counts().head(num_areas)
    return grapher.plot(counts,
                             x_label='Area',
                             y_label='Total Number of Incidents',
                             p_title=f'Incidents by top {num_areas} areas',
                             tick_rotation=65,
                             color='#f08080',
                             plot_type=PlotType.BAR), caption


def graph_vict_age(ages: pd.Series, caption: str):
    """Bins ages into ranges and returns figure.

    Args:
        ages (pd.Series): Series of ages
        caption (str): Caption for the figure
    Returns:
        tuple: (Figure, caption)
    """
    bins = [0, 14, 21, 34, 44, 54, 64, ages.max()]
    labels = ['0-14', '15-21', '22-34', '35-44', '45-54', '55-64', '65+']
    binned_ages = pd.cut(ages, bins, labels=labels, ordered=True).dropna()

    counts = binned_ages.value_counts().sort_index()

    colors = ['#d4f0f0', '#a9e1e1', '#7ed2d2', '#53c3c3', '#28b4b4', '#009999', '#007777']
    return grapher.plot(counts,
                            'Age range', 
                            'Percentage of Victims',
                            'Victim Age distribution',
                            color=colors,
                            plot_type=PlotType.PIE), caption


def graph_descent(descents: pd.Series, caption: str):
    """Graphs victim descent distribution as a pie chart.
    Args:
        descents (pd.Series): Series of victim descent strings
        caption (str): Caption for the figure
    Returns:
        tuple: (Figure, caption)
    """
    counts = descents.value_counts().sort_index()

    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c4e17f',
              '#f7c6c7','#b3b3b3','#ff6666','#669999','#ffb366','#b3ff66','#6666ff',
              '#ff99e6','#99e6ff','#66ffb3','#cccccc','#ff4d4d','#4d79ff'] # evenveel als race_map
    return grapher.plot(counts,
                            'Victim Descent', 
                            'Percentage of Victims',
                            'Victim Descent distribution',
                            color=colors,
                            plot_type=PlotType.PIE,
                            threshold=2.0), caption


def graph_charges(charges: pd.Series, caption: str):
    """Graphs charges as a bar chart.

    Args:
        charges (pd.Series): Series of charge classes
        caption (str): Caption for the figure
    Returns:
        tuple: (Figure, caption)
    """
    counts = charges.value_counts().sort_index() / 1000
    return grapher.plot(counts,
                             x_label='Charge Class',
                             y_label='Total Number of Incidents\nx1000',
                             p_title='Incidents by Charge Class',
                             tick_rotation=55,
                             color="#f0c363",
                             plot_type=PlotType.BAR,
                             sort_type=SortType.VALUE_DESCENDING,
                             grid=True,
                             grid_direction='y'), caption


def graph_vict_sex(gender: pd.Series, caption: str):
    """Graphs gender as a pie chart.

    Args:
        gender (pd.Series): Series of gender values
        caption (str): Caption for the figure
    Returns:
        tuple: (Figure, caption)
    """
    counts = gender.value_counts().sort_index()

    colors = ['#ff9999','#66b3ff', '#99ff99'] # f,m,x
    return grapher.plot(counts,
                             x_label='Gender',
                             y_label='Percentage of Victims',
                             p_title='Sex distribution of Victims',
                             color=colors,
                             plot_type=PlotType.PIE,
                             threshold=1.0,
                             use_other=False), caption


def graph_premis_desc(premises: pd.Series, caption: str, max_items: int, trun_len: int):
    """Graphs premise description as a bar chart.

    Args:
        premises (pd.Series): Series of premise description values.
        caption (str): Caption for the figure
        max_items (int): Maximum number of items to display.
        trun_len (int): Length to truncate premise descriptions to.
    Returns:
        tuple: (Figure, caption)
    """
    counts = premises.value_counts().head(max_items) / 1000
    counts.index = counts.index.map(
        lambda x: str(x)[:trun_len] + '...' if len(str(x)) > trun_len else str(x)) # truncate
    return grapher.plot(counts,
                             x_label='Premise Description',
                             y_label='Total Number of Incidents\nx1000',
                             p_title='Incidents by Premise Description',
                             tick_rotation=55,
                             color="#a8d5e2",
                             plot_type=PlotType.BAR,
                             sort_type=SortType.NONE,
                             grid=False,
                             grid_direction='y'), caption


def graph_weapons(weapons: pd.Series, caption: str, max_items: int, hide_unar: bool, trun_len: int):
    """Graphs weapon description as a bar chart.

    Args:
        weapons (pd.Series): Series of weapon description values.
        caption (str): Caption for the figure
        max_items (int): Maximum number of items to display.
        hide_unar (bool): Whether to hide strong arm entries.
        trun_len (int): Length to truncate weapon descriptions to.
    Returns:
        tuple: (Figure, caption)
    """
    # strong arm is een hele grote groep en vertekent de rest, maar is wel interessant
    if hide_unar:
        weapons = weapons[weapons != 'STRONG-ARM (HANDS, FIST, FEET OR BODILY FORCE)']

    counts = weapons.value_counts().head(max_items) / 1000
    counts.index = counts.index.map(
        lambda x: str(x)[:trun_len] + '...' if len(str(x)) > trun_len else str(x)) # truncate
    return grapher.plot(counts,
                             x_label='Weapon Description',
                             y_label='Total Number of Incidents\nx1000',
                             p_title='Weapons used in incidents',
                             tick_rotation=55,
                             color="#a8d5e2",
                             plot_type=PlotType.BAR,
                             sort_type=SortType.NONE,
                             grid=False,
                             grid_direction='y'), caption


def graph_report_status(statuses: pd.Series, caption: str):
    """Graphs report status description as a pie chart.

    Args:
        statuses (pd.Series): Series of report status description values.
        caption (str): Caption for the figure
    Returns:
        tuple: (Figure, caption)
    """
    counts = statuses.value_counts().sort_index()

    colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99','#c2c2f0','#ffb3e6','#c4e17f',
              '#f7c6c7','#b3b3b3','#ff6666','#669999','#ffb366','#b3ff66'] 
    return grapher.plot(counts,
                            'Case Status', 
                            'Percentage of cases',
                            'Status of the case',
                            color=colors,
                            caption='Only ~19% of reports are closed.',
                            plot_type=PlotType.PIE,
                            threshold=2.0), caption


@st.cache_resource
def graph_location_heatmap(locations: pd.DataFrame, caption: str):
    """Graphs location heatmap of incidents.
    Args:
        locations (pd.DataFrame): DataFrame with LAT and LON columns.
        caption (str): Caption for the figure
    Returns:
        tuple: (Figure, caption)
    """
    return grapher.location_heatmap(locations,
                                    title='Incident Location Heatmap in Los Angeles',
                                    caption='Minimum incidents threshold set at 200',
                                    min_count=200), caption


def render_plots(fig_cap: list):
    """Function that renders the streamlit page with predefined plots

    Args:
        figures (list): List of tuples containing (Figure, caption)
    """
    st.set_page_config(layout='centered')
    st.write('LAPD Crime Data Visualization by Jesse Postma')
    
    page_lyt = st.selectbox('Select page layout', ['Centered', 'Fullscreen'])
    if page_lyt == 'Fullscreen':
        st.set_page_config(layout='wide')

    md_intro = st.checkbox('Show project intro', value=False)
    if md_intro:
        with open('README.md', 'r', encoding='utf-8') as f:
            md_content = f.read()
        st.markdown(md_content, unsafe_allow_html=True)
        st.write('---')

    columns = st.slider('Amount of chart columns.',1,5,2,1)
    cols = st.columns(columns)

    for i, (figure, caption) in enumerate(fig_cap):
        current_col = cols[i % columns]
        with current_col:
            st.pyplot(figure, width='content')
            st.write(f'Figure {i+1}: {caption}') # caption

def main():
    """
    Main Function that handles calling and small logic.
    """

    helper.validate_project_structure(set(EXPECTED_FILES))

    data = process_data(EXPECTED_FILES)

    fig_cap = []

    # function calls for graphs we want
    fig_cap.append(graph_dates(data['DATE OCC'],
                               'Average daily incidents over the year.'))

    fig_cap.append(graph_times(data['TIME OCC'],
                               'Distribution of incidents by hour of the day.'))

    fig_cap.append(graph_dangerous_areas(data['AREA NAME'],
                                         'Top areas with the most reported incidents.',
                                         num_areas=15))

    fig_cap.append(graph_vict_age(data['Vict Age'],
                                  'Age distribution of victims grouped into ranges.'))

    fig_cap.append(graph_descent(data['Vict Descent'],
                                 'Race distribution of victims.'))

    fig_cap.append(graph_charges(data['Crm Cd'],
                                 'Distribution of incidents by charge class.'))

    fig_cap.append(graph_vict_sex(data['Vict Sex'],
                                  'Gender distribution of victims.'))

    fig_cap.append(graph_premis_desc(data['Premis Desc'],
                                     'Top premises where incidents occur.',
                                     max_items=15, trun_len=20))

    fig_cap.append(graph_weapons(data['Weapon Desc'],
                                     'Showcase of which weapons are most commonly used.',
                                     max_items=15, hide_unar=True, trun_len=20))

    fig_cap.append(graph_report_status(data['Status'],
                                      'Distribution of report status.'))

    fig_cap.append(graph_location_heatmap(data[['LAT', 'LON']].dropna(),
                                          'Heatmap of incident locations in Los Angeles.'))

    render_plots(fig_cap)


if __name__ == '__main__':
    main()
