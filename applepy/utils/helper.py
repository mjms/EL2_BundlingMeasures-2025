import json
import pickle
import os
import numpy as np
import pandas as pd
from IPython.display import display, clear_output

def find_nearest(array, value):
    """
    Finds the nearest value in an array to a given value.
    (adapted from : https://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array)

    Parameters
    ----------
    array (array-like): Input array of numeric values.
    value (numeric)   : Target value to find the nearest value to.

    Returns
    -------
    tuple: A tuple containing two elements:
        - The nearest value in the array to the given value.
        - The index of the nearest value in the array.
    """
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

def check_path(folder_path):
    """
    Checks if a folder path exists, and creates it if it doesn't.

    Parameters
    ----------
    folder_path (str): The path of the folder to be checked/created. Creates necessary subfolders, as needed

    Returns
    -------
    None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return print("created directory: {}".format(folder_path))
    else:
        return print("All files will be saved in: {}".format(folder_path))

def status(string):
    """
    Displays a continuous status updates (only works in IPython notebook)

    Parameters
    ----------
    string (str): The string to be displayed.

    Returns
    -------
    None
    """
    clear_output(wait=True)                
    return display(string) 

def savePickle(filepath,save_obj):
    """
    Saves an object to a pickle file.

    Parameters
    ----------
    filepath (str): The path where the pickle file will be saved.
    save_obj (object): The object to be saved.

    Returns
    -------
    None
    """
    f = open(filepath,"wb")
    pickle.dump(save_obj,f)
    f.close()

def loadPickle(filepath):
    """
    Loads an object from a pickle file.

    Parameters
    ----------
    filepath (str): The path from which the pickle file will be loaded.

    Returns
    -------
    object: The object loaded from the pickle file.
    """
    with open(filepath, 'rb') as f:
        data = pickle.load(f)   
    return data

def AgMIP_read_raw_csv(fp, model = 'myGeoHub'):
    """
    TODO: 
    Reads and processes raw CSV files for different agricultural models used in the Agricultural Model Intercomparison and Improvement Project (AgMIP).

    This function handles CSV files from various agricultural models, each with its own format and requirements. Depending on the specified model, it reads the CSV file and returns a pandas DataFrame with appropriate columns or modifications.

    Parameters:
    -----------
    fp : str
    The file path to the raw CSV file to be read.
    model : str
        The name of the agricultural model. Supported models include:
        - 'MAGNET'
        - 'MAgPIE'
        - 'AIM'
        - 'IMPACT'
        Default is 'myGeoHub'


    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the processed data from the CSV file. The structure of the DataFrame depends on the specified model:
        - For 'MAGNET', 'MAgPIE', and 'AIM': The DataFrame will have columns ['model', 'scenario', 'region', 'variable', 'item', 'unit', 'year', 'value'].
        - For 'IMPACT': The DataFrame will be read with a semicolon separator, and the 'description' column will be dropped if present.

    Raises:
    -------
    ValueError
        If the model is not one of the supported models ('MAGNET', 'MAgPIE', 'AIM', 'IMPACT').

    Examples:
    ---------
    >>> df = AgMIP_read_raw_csv('path/to/magnet_data.csv','MAGNET')
    >>> df.head()
       model scenario region  variable   item unit  year  value
    0  ...     ...     ...      ...      ...   ...  ...   ...
    1  ...     ...     ...      ...      ...   ...  ...   ...

    >>> df = AgMIP_read_raw_csv('IMPACT', 'path/to/impact_data.csv')
    >>> df.head()
       ...  ...  ...  ...  ...  ...  ...  ...
    0  ...  ...  ...  ...  ...  ...  ...  ...
    1  ...  ...  ...  ...  ...  ...  ...  ...

    Notes:
    ------
    - Ensure the CSV file format matches the expected structure for the specified model.
    - The function assumes that the first line in the CSV for 'IMPACT' contains headers separated by semicolons.

    """
    if (model=='myGeoHub') or (model == 'MAGNET') or (model=='MAgPIE') or (model=='AIM') or (model=='FARM') or (model =='GLOBIOM'):
        col_names = ['model','scenario','region','variable','item','unit','year','value']
        df = pd.read_csv(fp,names=col_names)
    
    elif model == 'IMPACT':
        df = pd.read_csv(fp,sep=';').drop(columns='description')
    
    elif model == 'IMAGE':
        # change column names to all lower case
        col_names = ['model', 'scenario', 'region', 'variable', 'item', 'unit', 'year', 'value']
        df = pd.read_csv(fp)
        df.columns = col_names
    
    return df

def get_group_keys(df,save_df=False):
    """
    Extracts unique group keys from the DataFrame and returns them as a new DataFrame.

    This function groups the input DataFrame by specified columns and extracts the unique combinations of these
    group keys. The result is returned as a new DataFrame. Optionally, the resulting DataFrame can be saved to a CSV file.

    Parameters:
    -----------
    df (pd.DataFrame): The input DataFrame to be grouped.
    save_df (bool or str): If False, the resulting DataFrame is not saved. If a string, it is treated as a file path,
                           and the resulting DataFrame is saved as a CSV file at that location.

    Returns:
    --------
    pd.DataFrame: A DataFrame containing the unique combinations of the specified group keys.

    Notes:
    ------
    - The DataFrame is grouped by the columns: 'model', 'scenario', 'region', 'variable', 'item', and 'unit'.
    - The resulting unique combinations are stored in a dictionary and then converted to a DataFrame.
    - If `save_df` is a string, the resulting DataFrame is saved as a CSV file at the specified path.
    - An assertion checks that if `save_df` is not False, it must be a string representing the file path.
    """
    grouped_dict = {'model':[], 
                    'scenario':[], 
                    'region':[], 
                    'variable':[], 
                    'item':[], 
                    'unit':[]
                    }
    grouped = list(df.groupby(['model', 'scenario', 'region', 'variable', 'item', 'unit']).groups.keys())
    for model,scenario,region,variable,item,unit in grouped:
        grouped_dict['model'].append(model)
        grouped_dict['scenario'].append(scenario)
        grouped_dict['region'].append(region)
        grouped_dict['variable'].append(variable)
        grouped_dict['item'].append(item)
        grouped_dict['unit'].append(unit)

    grouped_df = pd.DataFrame.from_dict(grouped_dict)
    
    if save_df:
        assert type(save_df)==str,"save_df should be a filepath, or False"
        grouped_df.to_csv(save_df)
    
    return grouped_df