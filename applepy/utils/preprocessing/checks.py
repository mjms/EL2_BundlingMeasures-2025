import pandas as pd
import numpy as np

def check_duplicates(df, save_df=False):
    """
    Check a pandas DataFrame for duplicated entries

    Parameters
    ----------
    df   : pandas DataFrame
        DataFrame to check for duplicated entries. Must have columns: 'scenario','region','variable', 'item','unit','year'
    save_df : False or str 
        False, or file path for save file

    Returns
    -------
    pandas DataFrame
        DataFrame with duplicated entries (duplicates are kept)

    """
    # keep only one duplicate if value is the same
    clean_df = df.drop_duplicates(subset=['model','scenario','region','variable', 'item','unit','year','value'])

    # check remaining duplicates
    duplicates_idx = clean_df.duplicated(subset=['model','scenario','region','variable', 'item','unit','year'], keep=False)
    duplicates_df = clean_df[duplicates_idx]
    clean_df = clean_df[~duplicates_idx]

    print(f"Found {len(df)-len(clean_df)} duplicated entries")
    print(f"...{len(duplicates_df)} of them have conflicting values...")

    if save_df:
        assert type(save_df)==str,"save_df should be a filepath, or False"
        duplicates_df.to_csv(save_df)
    return clean_df, duplicates_df

def check_overrides(df, overrides_fp):
    col_names = ['label','column','status']
    overrides_df = pd.read_csv(overrides_fp,names=col_names)
    overrides_df.column = [x.lower() for x in overrides_df.column] # columns in all processing codes/dfs are in lowercase
    overrides_df['status'] = overrides_df['status'].replace({'TRUE': True, 'FALSE': False})

    overrides_idx = []
    keep_idx = []
    for _,x in overrides_df.iterrows():
        # deal with False, treat manual as False...
        # change status to lower case in case manual checker mis-typed the value
        if (x.status == False):# or (x.status.lower() == 'manual'):
            overrides_idx.append(df[df[x.column]==x.label].index.values)

        # deal with True, also prevent the template checker from removing this (so we are setting them aside in a separate file)
        elif x.status == True:
            keep_idx.append(df[df[x.column]==x.label].index.values)

        # if the value is not True, False, or manual, this is a replacement case
        else:
            df.loc[df[x.column]==x.label,x.column] = x.status

    try:     
        overrides_idx = np.sort(np.unique(np.hstack(overrides_idx)))
    except:
        pass
    try:
        keep_idx = np.sort(np.unique(np.hstack(keep_idx)))
    except:
        pass
    
    keep_idx = [x for x in keep_idx if x not in overrides_idx]
    clean_df = df[~df.index.isin(np.hstack([overrides_idx,keep_idx]))]
    overrides_df = df[df.index.isin(overrides_idx)]
    keep_df = df[df.index.isin(keep_idx)]

    print(f"Overrides removed : {len(overrides_df)}")
    print(f"Overrides kept: {len(keep_df)}")

    return clean_df,overrides_df,keep_df

def check_template(df,template_fp,save_exceptions = False):
    ## template check, this actually refers to the RulesTables in myGeoHub, which should be consistent with the AgMIP reporting template for this project
    
    # get template variables and units
    VariableUnitValueTable = pd.read_excel(template_fp,'VariableUnitValueTable')

    # double check that all variables in df are in VariableUnitValueTable.Variable
    # set(df.variable.unique()).issubset(set(variables))
    variables = VariableUnitValueTable.Variable.values
    clean_df = df[df.variable.isin(variables)]

    keep_idx = []
    for variable in clean_df.variable.unique():
        expected_unit = VariableUnitValueTable[VariableUnitValueTable.Variable==variable].Unit.values
        keep_idx.append(clean_df[(clean_df.variable==variable) & (clean_df.unit.isin(expected_unit))].index.values)
    try:
        keep_idx = np.sort(np.unique(np.hstack(keep_idx)))
    except:
        keep_idx = []
    except_df = clean_df[~clean_df.index.isin(keep_idx)]
    clean_df = clean_df[clean_df.index.isin(keep_idx)]

    print(f"Template exceptions removed: {len(except_df)}")

    return clean_df,except_df