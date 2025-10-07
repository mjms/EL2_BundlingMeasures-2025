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

def run_land_calcs(fp):
    # TODO: clean up nan handling for items that don't exist. 
    
    data_dir = '/'.join(fp.split('/')[:-1])
    output_dir = pjoin(data_dir,'land')
    check_path(output_dir)

    df = pd.read_csv(fp,index_col=0)#.drop(columns=['index'])
    base_filename = fp.split('/')[-1].split('.csv')[0]

    variables = ['LAND']
    cols = ['model','scenario','variable','region','unit','year','item','value']
    fdf = df[df.variable.isin(variables)][cols]

    model_dict_fp = "../applepy/template/model_land.json"
    with open(model_dict_fp) as json_data:
        model_dict = json.load(json_data)
        json_data.close()
    models = list(set(df.model.unique()).intersection(set(model_dict.keys())))

    if len(models)>0:
        for k in models:#model_dict.keys():
            model_dict[k]["ref_year"] = df[df.model==k].BAU_ref_year.values[0]

        ffdf = pd.DataFrame()

        for model in models:
            years = [model_dict[model]['ref_year'], model_dict[model]['end_year']]
            item = model_dict[model]['item']
            model_fdf = fdf[(fdf.model==model) &
                            (fdf.item.isin(item)) ]
                            # & (fdf.year.isin(years))]
            ffdf = pd.concat([ffdf,model_fdf])


        ffdf = ffdf.pivot_table(index=['model','scenario','region','year'], columns='item',values='value').reset_index()

        required_cols = ['model','scenario','region','year', 'AGR', 'CRP','LSP','GRS','ONV','FOR','ECP']
        ffdf = ffdf.reindex(columns=required_cols)
        try:
            # Some models do not report AGR (only CRP and GRS), catch this exception. This throws an error only if there are no agr values at all, so usually when processing all the models, it doesn't result in an error
            ffdf['AGR_added'] = ffdf['CRP'] + ffdf['GRS']
            ffdf['AGR_diff'] = ffdf['AGR'] - ffdf['AGR_added']
            # ffdf['AGR_median'] = ffdf['AGR'] - ffdf['AGR_added']
        except Exception as e:
            print(f"Error: {e}")
        
        ffdf['ONV_added'] = ffdf['FOR'].fillna(0)  + ffdf['ONV'].fillna(0) 
        ffdf['LAND_tot'] = ffdf['AGR_added'] + ffdf['ONV_added']

        ffdf['AGR_share'] = ffdf['AGR_added']/ffdf['LAND_tot']
        ffdf['CRP_share'] = ffdf['CRP']/ffdf['LAND_tot']
        ffdf['GRS_share'] = ffdf['GRS']/ffdf['LAND_tot']
        ffdf['CRP_AGR_share'] = ffdf['CRP']/ffdf['AGR_added']
        ffdf['GRS_AGR_share'] = ffdf['GRS']/ffdf['AGR_added']

        ffdf['ONV_share'] = ffdf['ONV_added']/ffdf['LAND_tot']

        filename = pjoin(output_dir,base_filename+'_LAND-calcs-w.csv')
        print(f"\n>> Saving wide DataFrame to {filename}")
        ffdf.to_csv(filename, index=False)

        df_land = ffdf.melt(id_vars=['model', 'scenario', 'region', 'year'], value_vars = ['AGR_added','CRP','GRS','ONV_added','LAND_tot'], var_name = 'item',value_name='value')
        df_land['variable'] = 'LAND_added'
        df_land['unit'] = '1000 ha'

        df_shares = ffdf.melt(id_vars=['model', 'scenario', 'region', 'year'], value_vars = ['ONV_share','AGR_share','CRP_share','GRS_share','CRP_AGR_share','GRS_AGR_share'], var_name = 'item',value_name='value')
        df_shares['variable'] = 'LAND_share'
        df_shares['unit'] = 'share'
        df_shares.head()

        dc_df = pd.concat([df_land,df_shares])

        filename = pjoin(output_dir,base_filename+'_LAND-calcs.csv')
        print(f">> Saving long DataFrame to {filename}")
        dc_df.to_csv(filename,index=False)

        print(">> Running percentage change calculations...")
        pc_diff_interp(filename,output_dir)
    else:
        print("DataFrame has no valid entries for land calcs!")

