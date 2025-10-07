import sys
import os
from os.path import join as pjoin
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import time

from .basic import *
from .bias_correction import *
from ..helper import *

def run_emissions_calcs(fp):
    data_dir = '/'.join(fp.split('/')[:-1])
    output_dir = pjoin(data_dir,'emissions')
    check_path(output_dir)

    df = pd.read_csv(fp,index_col=0)#.drop(columns=['index'])
    base_filename = fp.split('/')[-1].split('.csv')[0]

    model_dict_fp = "../applepy/template/model_emissions.json"
    with open(model_dict_fp) as json_data:
        model_dict = json.load(json_data)
        json_data.close()
    models = list(set(df.model.unique()).intersection(set(model_dict.keys())))

    if len(models)>0:
        for k in models:#model_dict.keys():
            model_dict[k]["ref_year"] = df[df.model==k].BAU_ref_year.values[0]
            
        variables = ['ECH4',
                    'ECO2',
                    'EMIS',
                    'EN2O',]
        cols = ['model','scenario','variable','region','unit','year','item','value']
        fdf = df[df.variable.isin(variables)][cols]

        #filter fdf using model dict for statistics
        ffdf = pd.DataFrame()

        for model in models:#model_dict.keys():
            years = [model_dict[model]['ref_year'], model_dict[model]['end_year']]
            item = model_dict[model]['item']
            model_fdf = fdf[(fdf.model==model) &
                            (fdf.item==item) ]
                            # & (fdf.year.isin(years))]
            ffdf = pd.concat([ffdf,model_fdf])
            
        ffdf = ffdf.pivot_table(index=['model','scenario','region','year'], columns='variable',values='value').reset_index().fillna(0)

        # check that all the gases are present as columns
        # Add missing columns ('ECO2', 'ECH4', 'EN2O') with NaNs if they don't exist
        for col in ['ECO2', 'ECH4', 'EN2O']:
            if col not in ffdf.columns:
                ffdf[col] = 0

        ffdf['EMIS_added'] = ffdf['ECH4'] + ffdf['ECO2'] + ffdf['EN2O']
        ffdf['EMIS_nonCO2'] = ffdf['ECH4'] + ffdf['EN2O']
        ffdf['EMIS_diff'] = ffdf['EMIS'] - (ffdf['ECH4'] + ffdf['ECO2'] + ffdf['EN2O'])

        ffdf['ECH4_share'] = ffdf['ECH4']/ffdf['EMIS_added']
        ffdf['ECO2_share'] = ffdf['ECO2']/ffdf['EMIS_added']
        ffdf['EN2O_share'] = ffdf['EN2O']/ffdf['EMIS_added']
        ffdf['nonCO2_share'] = ffdf['EMIS_nonCO2']/ffdf['EMIS_added']

        print("\nStatistics on the difference between added emissions (CH4, N2O, and CO2) and total emisisons reported")
        print(ffdf.groupby(['model'])['EMIS_diff'].describe())

        filename = pjoin(output_dir,base_filename+'_EMIS-calcs-w.csv')
        print(f"\n>> Saving wide DataFrame to {filename}")
        ffdf.to_csv(filename, index=False)

        df_emis = ffdf.melt(id_vars=['model', 'scenario', 'region', 'year'], value_vars = ['EMIS_added', 'EMIS_nonCO2'], var_name = 'variable',value_name='value')
        df_emis['item'] = 'AGR'
        df_emis['unit'] = 'MtCO2e'

        df_shares = ffdf.melt(id_vars=['model', 'scenario', 'region', 'year'], value_vars = ['ECH4_share', 'ECO2_share', 'EN2O_share', 'nonCO2_share'], var_name = 'variable',value_name='value')
        df_shares['item'] = 'AGR'
        df_shares['unit'] = 'share'

        dc_df = pd.concat([df_emis,df_shares])

        filename = pjoin(output_dir,base_filename+'_EMIS-calcs.csv')
        print(f">> Saving long DataFrame to {filename}")
        dc_df.to_csv(filename,index=False)

        print(">> Running percentage change calculations...")
        pc_diff_interp(filename,output_dir)
    else:
        print("DataFrame has no valid entries for emissions calcs!")