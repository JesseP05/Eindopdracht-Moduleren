"""
    Helper module used by some of my scripts.
    Author: Jesse Postma
"""


import os

def dictionary_replace_csv(main_df, sub_df, tbindex_header, replace_header, replacing_header = None):
    """Function that handles mapping of pandas dataframes.

    Args:
        main_df (DataFrame): The dataframe that the map should be applied to.
        sub_df (DataFrame): The dataframe that contains mapping information.
        tbindex_header (str): The header of the column that the sub_df
        dataframe should be indexed on.
        replace_header (str): The header of the column in main_df
        of which the values will be replaced.
        replacing_header (str, optional): Optional specific interest header.
        Use when only interested in a a,b type situation. Defaults to None.

    Returns:
        DataFrame: Mapped main_df. 
    """
    lookup_df = None
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
    dirpath = os.path.dirname(os.path.realpath(__file__))
    data_dir = dirpath + '/data'
    data_dir_exists = os.path.exists(data_dir)

    if not data_dir_exists:
        raise DirectoryNotFoundError('The "data" directory is missing from the project.')

    files = os.listdir(data_dir)
    validator = expected_files - set(files)

    if len(validator) > 0:
        print(f'Files missing: {validator}')
        raise FileNotFoundError(f'File {validator} not found..')
    print('Project structure succesfully validated.')

class DirectoryNotFoundError(Exception):
    """Custom exception for directories not found.

    Args:
        message : Explanation of the error.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)
