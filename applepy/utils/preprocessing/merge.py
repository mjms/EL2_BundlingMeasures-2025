import pandas as pd
import time
from os.path import join as pjoin
from .checks import *
from ..helper import *

def merge_raw(fps, save = False, output_dir = None, merge_fn = None):
    """
    Merges multiple raw CSV files from different agricultural models into a single DataFrame.

    This function reads and merges multiple CSV files specified in `fps`, which are expected to be formatted according to different agricultural models' specifications. It processes each file, drops duplicates, and optionally saves the merged result to a specified directory.

    Parameters:
    -----------
    fps : list of str
        A list of file paths to the raw CSV files to be merged. Each file path should include the model name as part of the file name (before the '.csv' extension).
    save : bool, optional, default=False
        If True, the merged DataFrame will be saved as a CSV file. If False, the merged DataFrame will be returned.
    output_dir : str, optional
        The directory where the merged CSV file will be saved if `save` is True. If not specified, defaults to an 'output' subdirectory in the same directory as the first file in `fps`.
    merge_fn : str, optional
        The filename for the merged CSV file. If not specified, defaults to a name with the pattern `merged_YYMMDD.csv`, where `YYMMDD` is the current date.

    Returns:
    --------
    pandas.DataFrame
        If `save` is False, returns the merged DataFrame. If `save` is True, the function saves the DataFrame and returns None.

    Examples:
    ---------
    >>> merged_df = merge_raw(['MAGNET_2023.csv', 'MAgPIE_2023.csv'], save=False)
    >>> merged_df.head()
       model scenario region  variable   item unit  year  value
    0  ...     ...     ...      ...      ...   ...  ...   ...
    1  ...     ...     ...      ...      ...   ...  ...   ...

    >>> merge_raw(['MAGNET_2023.csv', 'MAgPIE_2023.csv'], save=True, output_dir='/path/to/output', merge_fn='merged_data.csv')
    Saving merged raw files to: /path/to/output/merged_data.csv

    Notes:
    ------
    - The function assumes that each CSV file name contains the model name before the '.csv' extension. This model name is used to determine the appropriate columns and format for reading the file.
    - Duplicates within each file are checked and will be dropped using the `check_duplicates` function.
    - The function utilizes `AgMIP_read_raw_csv` to read and process each file according to its model-specific requirements.
    - The `update_dataset` function is assumed to handle the merging of DataFrames correctly.
    - Ensure `check_path` and `pjoin` are defined and handle directory checks and path joining correctly.
    """

    # start with the first file
    old_fp = fps[0]
    old_df = AgMIP_read_raw_csv(old_fp)
    print("Duplicates will be dropped")
    check_duplicates(old_df)

    for update_fp in fps[1:]:
        # update_df = pd.read_csv(update_fp,index_col=0)
        # model = update_fp.split('/')[-1].split('.csv')[0]
        update_df = AgMIP_read_raw_csv(update_fp)
        print("Duplicates will be dropped")
        check_duplicates(update_df)
        old_df = update_dataset(old_df,update_df)

    # default update filename
    if merge_fn == None:
        merge_fn = f"merged_{time.strftime('%y%m%d')}.csv"

    if output_dir == None:
        output_dir = '/'.join(old_fp.split('/')[:-1])+'/output'
        check_path(output_dir)

    if save: 
        merge_fp = pjoin(output_dir,merge_fn)
        print(f'Saving merged raw files to: {merge_fp}')
        old_df.to_csv(merge_fp)

    else:
        return old_df

def update_dataset(old_df, new_df, full_replace = True):
    """
    Update an existing dataset with new data.

    This function updates the original dataset (`old_df`) with new data (`new_df`) by:
    1. Removing duplicate rows in the original dataset based on specified columns.
    2. Setting the index of the original and new datasets to specified columns.
    3. Concatenating the new data with the original dataset, excluding rows already present in the original dataset.
    4. Resetting the index of the resulting dataset.

    Parameters
    ----------
    - old_df (DataFrame): The original dataset to be updated.
    - new_df (DataFrame): The new data to update the original dataset with.

    Returns
    -------
    - DataFrame: Updated dataset after merging the new data with the original dataset.
    
    Note
    ----
    - The columns used for deduplication and indexing are assumed to be 'model', 'scenario', 'region', 'variable', 'item', 'unit', and 'year'.
    """
    old_df.scenario = old_df.scenario.str.upper() #there are some that report ELM_DIET as ELM_Diet
    new_df.scenario = new_df.scenario.str.upper()

    if full_replace:
        old_df = old_df.drop_duplicates(subset=['model','scenario','region','variable', 'item','unit','year'], keep=False)
        new_df = new_df.drop_duplicates(subset=['model','scenario','region','variable', 'item','unit','year'], keep=False)

        models_to_replace = new_df.model.unique()
        old_df = old_df[~old_df.model.isin(models_to_replace)]
        
        return pd.concat([new_df, old_df]).reset_index(drop=True)
    
    else:
        old_df = old_df.drop_duplicates(subset=['model','scenario','region','variable', 'item','unit','year'], keep=False)
        new_df = new_df.drop_duplicates(subset=['model','scenario','region','variable', 'item','unit','year'], keep=False)
        return pd.concat([new_df, old_df[~old_df.index.isin(new_df.index)]]).reset_index(drop=True)
    
def merge_fps(fps, save = False, output_dir = None, merge_fn = None, drop_duplicates=False):  
    base_dir = fps[0].split('/')[-2]

    merged_df = pd.concat([pd.read_csv(fp) for fp in fps],ignore_index=True)
    if drop_duplicates:
        merged_df = merged_df.drop_duplicates(subset=['model','scenario','region','variable', 'item','unit','year'], keep=False)
        # default update filename
        if merge_fn == None:
            merge_fn = f"merged-{base_dir}_duplicates-dropped_{time.strftime('%y%m%d')}.csv"
    else: 
        # default update filename
        if merge_fn == None:
            merge_fn = f"merged-{base_dir}_{time.strftime('%y%m%d')}.csv"

    if save: 
        if output_dir == None:
            output_dir = '/'.join(fps[0].split('/')[:-1])+'/output'
            check_path(output_dir)
        merge_fp = pjoin(output_dir,merge_fn)
        print(f'Saving merged files to: {merge_fp}')
        merged_df.to_csv(merge_fp)
    else:    
        return merged_df