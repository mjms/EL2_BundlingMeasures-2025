import pandas as pd
# import duckdb as ddb
import polars as pl
import numpy as np
from applepy.utils.calculations.basic import *

def individual_effect(scenario_pl, value, driver, normalized = False,use_pandas=False):
    ## using pandas is slower than using polars
    if use_pandas:
        scenario_df = scenario_pl
        baseline = scenario_df[scenario_df.scenario=='BAU'][value].values
        full = scenario_df[scenario_df.scenario=='ELM'][value].values
        driver_only = scenario_df[scenario_df.scenario=='BAU_'+driver][value].values
        if normalized:
            return (driver_only-baseline)/(full-baseline), (baseline,full,driver_only)
        else:
            return  (driver_only-baseline), (baseline,full,driver_only)
        
    # default mode and recommended using Polars    
    else:
        baseline = scenario_pl.filter(pl.col('scenario')=='BAU').select(value)
        full = scenario_pl.filter(pl.col('scenario')=='ELM').select(value)
        driver_only = scenario_pl.filter(pl.col('scenario')=='BAU_'+driver).select(value)
        if normalized:
            return (driver_only-baseline)/(full-baseline), (baseline,full,driver_only)
        else:
            return  (driver_only-baseline), (baseline,full,driver_only)

def total_effect(scenario_pl, value, driver, normalized = False,use_pandas=False):
    ## using pandas is slower than using polars
    if use_pandas:
        scenario_df = scenario_pl
        baseline = scenario_df[scenario_df.scenario=='BAU'][value].values
        full = scenario_df[scenario_df.scenario=='ELM'][value].values
        all_but_driver = scenario_df[scenario_df.scenario=='ELM_'+driver][value].values
        if normalized:
            return (full-all_but_driver)/(full-baseline), (baseline,full,all_but_driver)
        else:
            return  (full-all_but_driver), (baseline,full,all_but_driver)
        
    else:
        baseline = scenario_pl.filter(pl.col('scenario')=='BAU').select(value)
        full = scenario_pl.filter(pl.col('scenario')=='ELM').select(value)
        all_but_driver = scenario_pl.filter(pl.col('scenario')=='ELM_'+driver).select(value)
        if normalized:
            return (full-all_but_driver)/(full-baseline), (baseline,full,all_but_driver)
        else:
            return  (full-all_but_driver), (baseline,full,all_but_driver)

def decompose_driver_effect_filtered(scenario_df, value, driver, normalized = False, use_pandas = False, full_dict = False):
    individual, (baseline,full,driver_only) = individual_effect(scenario_df,value, driver,normalized,use_pandas)
    total, (baseline,full,all_but_driver) = total_effect(scenario_df, value,driver,normalized,use_pandas)
    if use_pandas:
        interaction =  total - individual
        effect_dict = {'individual':individual, 'total': total, 'interaction':interaction}
    else:      
        interaction =  total.to_numpy() - individual.to_numpy()
        effect_dict = {'individual': individual.to_numpy(), 'total': total.to_numpy(), 'interaction':interaction}

    if full_dict:
        # TODO change this to an assertion
        effect_dict['model'] = scenario_df.model.unique()[0]
        effect_dict['region'] = scenario_df.region.unique()[0]
        effect_dict['variable'] = scenario_df.variable.unique()[0]
        effect_dict['item'] = scenario_df.item.unique()[0]
        effect_dict['year'] = scenario_df.year.unique()[0]
        effect_dict['unit'] = scenario_df.unit.unique()[0]
        effect_dict['driver'] = driver
        effect_dict['normalized'] = normalized
        effect_dict['value_type'] = value
        effect_dict['ELM'] = full
        effect_dict['BAU'] = baseline
        effect_dict['EL2'] = scenario_df[scenario_df.scenario=='ELM_MITI'][value].values
        effect_dict['ELM_driver'] = all_but_driver # ELM_driver
        effect_dict['BAU_driver'] = driver_only # BAU_driver
        effect_dict['percent_change_BAU_individual'] = percent_change(baseline,individual)
        effect_dict['percent_change_BAU_total'] = percent_change(baseline,total)
        effect_dict['percent_change_BAU_interaction'] = percent_change(baseline,interaction)
         
        return effect_dict
    else:
        return effect_dict

# def individual_effect(scenario_pl, driver, normalized = False,use_pandas=False):
#     ## using pandas is slower than using polars
#     if use_pandas:
#         scenario_df = scenario_pl
#         baseline = scenario_df[scenario_df.scenario=='BAU'].value.values
#         driver_only = scenario_df[scenario_df.scenario.str.contains('BAU_'+driver, na=False, case=False)].value.values
#         if normalized:
#             full = scenario_df[scenario_df.scenario=='ELM'].value.values
#             return (driver_only-baseline)/(full-baseline)
#         else:
#             return  (driver_only-baseline)
        
#     # default mode and recommended using Polars    
#     else:
#         baseline = scenario_pl.filter(pl.col('scenario')=='BAU').select('value')
#         driver_only = scenario_pl.filter(pl.col('scenario')=='BAU_'+driver).select('value')
#         if normalized:
#             full = scenario_pl.filter(pl.col('scenario')=='ELM').select('value')
#             return (driver_only-baseline)/(full-baseline)
#         else:
#             return  (driver_only-baseline)

# def total_effect(scenario_pl, driver, normalized = False,use_pandas=False):
#     ## using pandas is slower than using polars
#     if use_pandas:
#         scenario_df = scenario_pl
#         baseline = scenario_df[scenario_df.scenario=='BAU'].value.values
#         full = scenario_df[scenario_df.scenario=='ELM'].value.values
#         all_but_driver = scenario_df[scenario_df.scenario.str.contains('ELM_'+driver, na=False, case=False)].value.values
#         if normalized:
#             full = scenario_df[scenario_df.scenario=='ELM'].value.values
#             return (full-all_but_driver)/(full-baseline)
#         else:
#             return  (full-all_but_driver)
        
#     else:
#         full = scenario_pl.filter(pl.col('scenario')=='ELM').select('value')
#         all_but_driver = scenario_pl.filter(pl.col('scenario')=='ELM_'+driver).select('value')
#         if normalized:
#             baseline = scenario_pl.filter(pl.col('scenario')=='BAU').select('value')
#             return (full-all_but_driver)/(full-baseline)
#         else:
#             return  (full-all_but_driver)


# def decompose_driver_effect(df, model, variable, item, region, year, driver, normalized = False, use_pandas = False, full_dict = False):
#     if use_pandas:
#         scenario_df = df[(df.model==model) & (df.variable==variable) & (df.region==region) & (df.item==item) & (df.year==year)]
#         individual = individual_effect(scenario_df,driver,normalized,use_pandas)
#         total = total_effect(scenario_df,driver,normalized,use_pandas)
#         interaction =  total - individual
#         effect_dict = {'individual':individual, 'total': total, 'interaction':interaction}
#     else:      
#         scenario_pl = df.filter(pl.col('model')==model,pl.col('variable')==variable,pl.col('item')==item,pl.col('region')==region,pl.col('year')==year)
#         scenario_pl = scenario_pl.with_columns(pl.col('scenario').str.to_uppercase())
#         individual = individual_effect(scenario_pl,driver, normalized,use_pandas)
#         total = total_effect(scenario_pl,driver,normalized,use_pandas)
#         interaction =  total.to_numpy() - individual.to_numpy()
#         effect_dict = {'individual': individual.to_numpy(), 'total': total.to_numpy(), 'interaction':interaction}

#     if full_dict:
#         effect_dict['model'] = model
#         effect_dict['region'] = region
#         effect_dict['variable'] = variable
#         effect_dict['item'] = item
#         effect_dict['year'] = year
#         effect_dict['driver'] = driver
#         return effect_dict
#     else:
#         return effect_dict
    
# def decompose_driver_effect_filtered(scenario_df,driver, normalized = False, use_pandas = False, full_dict = False):
#     if use_pandas:
#         individual = individual_effect(scenario_df,driver,normalized,use_pandas)
#         total = total_effect(scenario_df,driver,normalized,use_pandas)
#         interaction =  total - individual
#         effect_dict = {'individual':individual, 'total': total, 'interaction':interaction}
#     else:      
#         scenario_pl = scenario_pl.with_columns(pl.col('scenario').str.to_uppercase())
#         individual = individual_effect(scenario_pl,driver, normalized,use_pandas)
#         total = total_effect(scenario_pl,driver,normalized,use_pandas)
#         interaction =  total.to_numpy() - individual.to_numpy()
#         effect_dict = {'individual': individual.to_numpy(), 'total': total.to_numpy(), 'interaction':interaction}

#     if full_dict:
#         effect_dict['model'] = scenario_df.model.unique().values
#         effect_dict['region'] = scenario_df.region.unique().values
#         effect_dict['variable'] = scenario_df.variable.unique().values
#         effect_dict['item'] = scenario_df.item.unique().values
#         effect_dict['year'] = scenario_df.year.unique().values
#         effect_dict['driver'] = driver
#         return effect_dict
#     else:
#         return effect_dict