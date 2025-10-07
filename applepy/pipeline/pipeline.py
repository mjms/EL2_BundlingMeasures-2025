
import pandas as pd
import time
import os
from os.path import join as pjoin
from contextlib import contextmanager
from multiprocessing import Pool, Manager
from tqdm import tqdm
from functools import partial

from ..utils.preprocessing.checks import *
from ..utils.preprocessing.interpolation import *
from ..utils.calculations.bias_correction import *
from ..utils.helper import *

def el2_pipeline(fp, template_fp = '../applepy/template/RuleTables.xlsx'):
    # TODO: 
    # - assertion that there is only one unique model in df
    # - rename all output files with model identifier  
    data_dir = '/'.join(fp.split('/')[:-1])
    overrides_fp = fp.split('.csv')[0]+'_OVERRIDES_fix.csv'
    # open file
    df = AgMIP_read_raw_csv(fp)

    # get model name
    model = df.model.unique()[0]
    base_fn = model#fp.split('/')[-1].split('.csv')[0]

    print(f"PROCESSING FILE : {base_fn}")
    print(f">> original DataFrame length: {len(df)}")
    print('\n')

    ######################
    ## DUPLICATES CHECK ##
    ######################
    # check duplicates
    print(f">> checking duplicates")
    clean_df, duplicates_df = check_duplicates(df)

    duplicates_dir = pjoin(data_dir,'duplicates')
    check_path(duplicates_dir)
    duplicates_fp = pjoin(duplicates_dir,base_fn+'_duplicates.csv')
    if len(duplicates_df)>0:
        duplicates_df.to_csv(duplicates_fp)#,index=False)
    print('\n')

    #######################
    ## VARIABLES TO KEEP ##
    #######################
    # set aside variables to keep
    print(f">> setting aside variables to keep")
    VariableUnitValueTable = pd.read_excel(template_fp,'VariableUnitValueTable')

    variables_to_keep = VariableUnitValueTable[VariableUnitValueTable.Keep==1].Variable.values
    variables_to_keep_df = clean_df[clean_df.variable.isin(variables_to_keep)]

    if len(variables_to_keep_df)==0:
        variables_to_keep_df = pd.DataFrame().reindex(columns=clean_df.columns)

    # remove variables to keep from clean df, they will be added back later
    clean_df = clean_df[~clean_df.variable.isin(variables_to_keep)]

    print(f"... set aside variables to keep. DataFrame length: {len(clean_df)}, {np.round((len(clean_df)/len(df))*100,0)}% of the original df")

    ####################
    ## OVERRIDE CHECK ##
    ####################

    # check overrides

    print(f">> checking overrides")

    if os.path.exists(overrides_fp):
        clean_df,overrides_df,keep_df = check_overrides(clean_df,overrides_fp)
    
        print(f"... overrides checked. DataFrame length: {len(clean_df)}, {np.round((len(clean_df)/len(df))*100,0)}% of the original df")

        # save overrides-removed
        overrides_dir = pjoin(data_dir,'overrides')
        check_path(overrides_dir)
        overridesRemoved_fp = pjoin(overrides_dir,base_fn+'_overrides-removed.csv')
        clean_df.to_csv(overridesRemoved_fp,index=False)

        # save updated overrides file
        overrides_list = get_group_keys(overrides_df)
        overridesList_fp = pjoin(overrides_dir,base_fn+'_overrides-list.csv')
        overrides_list.to_csv(overridesList_fp)#,index=False)
    else:
        print(f"... no overrides file found!\n")
        keep_df = pd.DataFrame().reindex(columns=clean_df.columns)
    print('\n')

    ####################
    ## TEMPLATE CHECK ##
    ####################

    print(f">> checking against template")
    clean_df,exception_df = check_template(clean_df,template_fp)

    print(f"... template checked. DataFrame length: {len(clean_df)}, {np.round((len(clean_df)/len(df))*100,0)}% of the original df")

    print(f"... concatenating template-checked DataFrame with the kept overrides and variables to keep...")
    clean_df = pd.concat([clean_df,keep_df,variables_to_keep_df],ignore_index=True)
    
    # check duplicates
    print(f">> checking duplicates again")
    clean_df, duplicates_df = check_duplicates(clean_df)

    print(f"... DataFrame length: {len(clean_df)}, {np.round((len(clean_df)/len(df))*100,0)}% of the original df")

    templateChecked_dir = pjoin(data_dir,'template-checked')
    check_path(templateChecked_dir)
    templateChecked_fp = pjoin(templateChecked_dir,base_fn+'_template-checked.csv')
    clean_df.to_csv(templateChecked_fp)#,index=False)

    # save updated template exceptions file
    exception_list = get_group_keys(exception_df)
    exceptionList_fp = pjoin(templateChecked_dir,base_fn+'_template-exceptions-list.csv')
    exception_list.to_csv(exceptionList_fp)#,index=False)
    print('\n')

    ####################
    ## PERCENT CHANGE ##
    ####################

    print(f">> calculating percentage changes")

    pcDiff_dir = pjoin(data_dir,'pc-diff')
    check_path(pcDiff_dir)
    pc_diff_interp(templateChecked_fp,output_dir=pcDiff_dir)
    print('\n')

    print(f"DONE PROCESSING : {base_fn}")


# Context manager to redirect stdout to /dev/null
@contextmanager
def suppress_output():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
# Wrapper function to suppress stdout
def el2_pipeline_silent(fp):
    with suppress_output():
        return el2_pipeline(fp)
    
# Function to update the progress bar
def update_progress_bar(pbar, result):
    pbar.update()


def el2_pipeline_multiprocess(data_dir):
    if not os.path.isdir(data_dir):
        print(f"{data_dir} is not a valid directory.")
        return
    
    fps = sorted([pjoin(data_dir,x) for x in os.listdir(data_dir) if all([(x.endswith('.csv')) and  not 
                                                                        any([(x.endswith('OVERRIDES.csv')) or (x.endswith('OVERRIDES_fix.csv'))])
                                                                        ])
                                                                        ])
    if not fps:
        print(f"No files found in {data_dir}.")
        return
    
    manager = Manager()
    with Pool(5) as p:
        with tqdm(total=len(fps)) as pbar:
            update_progress = partial(update_progress_bar, pbar)
            results = []
            for fp in fps:
                result = p.apply_async(el2_pipeline_silent, args=(fp,), callback=update_progress)
                results.append(result)
            for result in results:
                result.wait()  # Ensure all results are collected
    print([result.get() for result in results])
