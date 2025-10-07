import sys
import os
from os.path import join as pjoin
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import logging
import time
pd.set_option("mode.copy_on_write", True)

from .basic import *
from ..helper import *
from ..preprocessing.interpolation import *


def pc_diff(fp,output_dir=None,base_year=2020):
    """
    Processes a dataset to calculate percent change and differences relative to a baseline scenario and year.

    This function reads a CSV file, processes it to calculate the percent change and absolute differences
    relative to a specified baseline scenario and year. The results are saved to a new CSV file. Optionally, logs
    are generated to keep track of errors and processing steps.

    Parameters:
    -----------
    fp (str): The file path of the CSV file to be processed.
    output_dir (str, optional): The directory where the output files will be saved. If None, an 'output' directory is created in the same location as the input file. Defaults to None.
    base_year (int, optional): The base year for calculating percent changes and differences. Defaults to 2020.

    Returns:
    --------
    None

    Notes:
    ------
    - The function creates a new DataFrame with additional columns for storing percent changes and differences.
    - Grouping is done based on 'model', 'variable', 'item', 'region', and 'unit' columns.
    - Logging is set up to record errors during processing.
    - Percent changes and differences are calculated for three scenarios: 'BAU' relative to the base year, 'BAU' for the same year, and 'ELM' for the same year.
    - The results are saved to a CSV file in the specified or default output directory.
    """

    # load dataset
    df = pd.read_csv(fp)

    # set up output directory
    base_filename = fp.split('/')[-1].split('.csv')[-2]

    print(f'Processing file: {base_filename}')

    if output_dir==None:
        output_dir = '/'.join(fp.split('/')[:-1])+'/output'
        check_path(output_dir)

    log_dir = pjoin(output_dir,'logs')
    check_path(log_dir)


    # create a new df with empty columns to populate
    df_pc = df.copy()
    df_pc.reset_index(inplace=True)
    df_pc['BAU_ref_year'] = np.nan
    df_pc['percent_change_BAU_ref_year'] = np.nan
    df_pc['diff_BAU_ref_year'] = np.nan

    df_pc['percent_change_BAU'] = np.nan
    df_pc['diff_BAU'] = np.nan

    df_pc['percent_change_ELM'] = np.nan
    df_pc['diff_ELM'] = np.nan

    df_pc['index'] = df_pc.index

    grouped = df_pc.groupby(['model','variable','item','region','unit'])

    logging.basicConfig(filename=pjoin(log_dir,base_filename+
            '_pc-diff_'+
            time.strftime('%y%m%d-%H%M%S', time.localtime())+'.log'),
            encoding='utf-8',
            level=logging.DEBUG)
    # base_year = 2020
    for k in tqdm(list(grouped.groups.keys())):
        # status(k)
        try:
            k_df = grouped.get_group(k)
            for scenario in k_df.scenario.unique():
                model_base_year = find_nearest(k_df.year.unique(),base_year)[0]
                for year in k_df.year.unique():
                    val =     k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year) , 'value'].values
                    
                    # percent change to BAU 2020
                    try:
                        ref =  k_df.loc[(k_df.scenario=='BAU') &
                                    (k_df.year==model_base_year), 'value'].values
                        
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'percent_change_BAU_ref_year'] = percent_change(ref,val)
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'diff_BAU_ref_year'] = val-ref
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'BAU_ref_year'] = model_base_year

                    except Exception as e:
                        logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())}, {k},{scenario},{year},{model_base_year},'percent_change_BAU_2020',{e}")

                    # percent change BAU, same year
                    try:

                        ref =  k_df.loc[(k_df.scenario=='BAU') &
                                    (k_df.year==year), 'value'].values
                        
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'percent_change_BAU'] = percent_change(ref,val)
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'diff_BAU'] = val-ref

                    except Exception as e:
                        logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())}, {k},{scenario},{year},'percent_change_BAU',{e}")
                    
                    # percent change ELM, same year
                    try:
                        ref =  k_df.loc[(k_df.scenario=='ELM') &
                                    (k_df.year==year), 'value'].values
                        
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'percent_change_ELM'] = percent_change(ref,val)
                        df_pc.loc[k_df[(k_df.scenario==scenario) & (k_df.year==year)].index, 'diff_ELM'] = val-ref

                    except Exception as e:
                        logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())},{k},{scenario},{year},'percent_change_ELM',{e}")
        except Exception as e:
            logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())}, {k},{scenario},{year},'key error'")
    
    
    save_filename = pjoin(output_dir,base_filename+'_pc-diff.csv')
    print(f"Done. Saving file to {save_filename}")
    df_pc.to_csv(save_filename,)



def pc_diff_interp(fp,output_dir,base_year=2020):
    """
    Processes a dataset to calculate percent change and differences relative to a baseline scenario and year,
    including interpolation if the base year is missing from the dataset.

    This function reads a CSV file, processes it to calculate the percent change and absolute differences
    relative to a specified baseline scenario and year. If the base year is not present in the data, it performs
    linear interpolation to estimate values for the base year. The results are saved to a new CSV file. Optionally,
    logs are generated to keep track of errors and processing steps.

    Parameters:
    -----------
    fp (str): The file path of the CSV file to be processed.
    output_dir (str, optional): The directory where the output files will be saved. If None, an 'output' directory is created in the same location as the input file. Defaults to None.
    base_year (int, optional): The base year for calculating percent changes and differences. Defaults to 2020.

    Returns:
    --------
    None

    Notes:
    ------
    - The function creates a new DataFrame with additional columns for storing percent changes and differences.
    - Grouping is done based on 'model', 'variable', 'item', 'region', and 'unit' columns.
    - Logging is set up to record errors during processing.
    - Percent changes and differences are calculated for three scenarios: 'BAU' relative to the base year, 'BAU' for the same year, and 'ELM' for the same year.
    - If the base year is not present in the data, linear interpolation is used to estimate the values.
    - The results are saved to a CSV file in the specified or default output directory.
    """

    # load dataset
    df = pd.read_csv(fp)

    # set up output directory
    base_filename = fp.split('/')[-1].split('.csv')[-2]

    print(f'Processing file: {base_filename}')

    if output_dir==None:
        output_dir = '/'.join(fp.split('/')[:-1])+'/output'
        check_path(output_dir)

    log_dir = pjoin(output_dir,'logs')
    check_path(log_dir)


    # create a new df with empty columns to populate
    df_pc = pd.DataFrame()

    grouped = df.groupby(['model','variable','item','region','unit'])

    logging.basicConfig(filename=pjoin(log_dir,base_filename+
            '_pc-diff_'+
            time.strftime('%y%m%d-%H%M%S', time.localtime())+'.log'),
            encoding='utf-8',
            level=logging.DEBUG)

    for k in tqdm(list(grouped.groups.keys())):
        # status(k)
        try:
            k_df = grouped.get_group(k)

            # patch k_df if model does not report base_year (this is the same as ref_year). 
            # do a linear interpolation between the two nearest years
            if base_year not in k_df.year.unique():
                k_df = interp_base_year(k_df,base_year)
            
            # create new columns
            k_df.loc[:,'BAU_ref_year'] = np.nan
            k_df.loc[:,'percent_change_BAU_ref_year'] = np.nan
            k_df.loc[:,'diff_BAU_ref_year'] = np.nan

            k_df.loc[:,'percent_change_BAU'] = np.nan
            k_df.loc[:,'diff_BAU'] = np.nan

            k_df.loc[:,'percent_change_ELM'] = np.nan
            k_df.loc[:,'diff_ELM'] = np.nan
            

            for scenario in k_df.scenario.unique():
                for year in k_df.year.unique():   
                    val =   k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year) , 'value'].values
                    # percent change to BAU 2020
                    try:
                        ref =  k_df.loc[(k_df.scenario=='BAU') &
                                    (k_df.year==base_year), 'value'].values
                        # print(k,scenario,year,val,ref,percent_change(ref,val))
                        
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'percent_change_BAU_ref_year'] = percent_change(ref,val)
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'diff_BAU_ref_year'] = val-ref
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'BAU_ref_year'] = base_year

                    except Exception as e:
                        logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())}, {k},{scenario},{year},{base_year},'percent_change_BAU_2020',{e}")

                    # percent change BAU, same year
                    try:

                        ref =  k_df.loc[(k_df.scenario=='BAU') &
                                    (k_df.year==year), 'value'].values
                        
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'percent_change_BAU'] = percent_change(ref,val)
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'diff_BAU'] = val-ref

                    except Exception as e:
                        logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())}, {k},{scenario},{year},'percent_change_BAU',{e}")
                    
                    # percent change ELM, same year
                    try:
                        ref =  k_df.loc[(k_df.scenario=='ELM') &
                                    (k_df.year==year), 'value'].values
                        
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'percent_change_ELM'] = percent_change(ref,val)
                        k_df.loc[(k_df.scenario==scenario) &
                                    (k_df.year==year),'diff_ELM'] = val-ref

                    except Exception as e:
                        logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())},{k},{scenario},{year},'percent_change_ELM',{e}")
        except Exception as e:
            logging.error(f"{time.strftime('%y%m%d-%H%M%S', time.localtime())}, {k},{scenario},{year},'key error'")

        df_pc = pd.concat([df_pc,k_df])

    save_filename = pjoin(output_dir,base_filename+f'_pc-diff_interp-{base_year}.csv')
    print(f"Done. Saving file to {save_filename}")
    df_pc.to_csv(save_filename,)
