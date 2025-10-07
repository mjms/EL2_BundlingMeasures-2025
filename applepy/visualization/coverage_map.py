import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

def coverage_map(df):
    """
    Generates a heatmap to visualize the coverage of different models across variables and items.

    The function takes a DataFrame as input, extracts the 'model', 'variable', and 'item' columns, and 
    removes any duplicate combinations of these. It then calculates the number of unique models associated 
    with each variable-item pair and creates a pivot table with variables as rows and items as columns. 
    Finally, it generates a binary heatmap, where the presence of a model for a specific variable-item 
    combination is indicated.

    Parameters:
    -----------
    df (pd.DataFrame): A DataFrame containing at least the columns 'model', 'variable', and 'item'.

    Returns:
    --------
    None: Displays a heatmap using matplotlib and seaborn.
    """
    cols =  ['model','variable','item']
    fdf = df[cols].drop_duplicates()
    summary_df = fdf.groupby(['variable','item']).model.nunique().reset_index().pivot_table(index='variable',columns='item',values='model').reset_index().set_index('variable')
    y_label = summary_df.index
    x_label = summary_df.columns

    plt.figure(figsize=(10,10))
    sns.heatmap(summary_df,square=True,linewidths=1,cbar=False)

def template_coverage_map(df):
    """
    Generates a heatmap to visualize the coverage of variables and items based on a given template and 
    input DataFrame. The function reads in a template Excel file, processes the variable-item mappings, 
    and compares these against the input DataFrame to produce a binary heatmap indicating coverage.

    The heatmap displays which variables are associated with which items, marking existing associations 
    with an 'x' and leaving other cells blank. The binary color scheme highlights the presence or absence 
    of associations.

    Parameters:
    -----------
    df (pd.DataFrame): A DataFrame containing 'variable' and 'item' columns to compare against the template.

    Returns:
    --------
    None: Displays a heatmap using matplotlib and seaborn.
    """
    template_fp = "../applepy/template/Reporting_template_AGMIP_2024-07-11.xlsx"
    AgMIP_xl = pd.read_excel(template_fp,"Variables")
    AgMIP_extended = pd.read_excel(template_fp,"Variables_extended")
    lookup = AgMIP_xl.iloc[0,:]
    template_dict = {'variable':[],
                    'item':[]}
    variables = AgMIP_xl.Variable[1:].unique()
    extended_variables = AgMIP_extended.Variable.values
    items = AgMIP_xl.iloc[0,:].values[3:-2]
    for variable in variables:
        if variable is not np.nan:
            fdf = AgMIP_xl[AgMIP_xl.Variable==variable]
            v_item = [AgMIP_xl.iloc[0,:][col] for col in fdf.columns.drop(['Variable','Description','Unit']) if fdf[col].values[0] == 'X']
            for i in v_item:
                template_dict['variable'].append(variable)
                template_dict['item'].append(i)

    for variable in extended_variables:
        for item in items:
            template_dict['variable'].append(variable)
            template_dict['item'].append(item)

    template_df = pd.DataFrame.from_dict(template_dict)
    template_df['variable'] = pd.Categorical(template_df['variable'], categories=np.hstack([variables,extended_variables]), ordered=True)
    template_df['item'] = pd.Categorical(template_df['item'], categories=items, ordered=True)
    template_df['value'] = None
    template_df.loc[~template_df.variable.isin(extended_variables),'value'] = 1
    template_df.loc[template_df.variable.isin(extended_variables),'value'] = np.nan

    cols =  ['value','variable','item']
    fdf = template_df[cols].drop_duplicates()
    template_df_p = fdf.groupby(['variable','item']).value.nunique().reset_index().pivot_table(index='variable',columns='item',values='value').reset_index().set_index('variable')\

    annot = pd.DataFrame().reindex_like(template_df_p)
    annot[template_df_p==1] = 'x'
    annot[template_df_p==0] = ''
    annot = annot.to_numpy()

    summary_df = template_df.copy()
    summary_df['value'] = 0
    for v in df.variable.unique():
        try: 
            i = df[df.variable==v].item.unique()
            summary_df.loc[(summary_df.variable==v) & (summary_df.item.isin(i)),'value'] = 1
        except Exception as e:
            print(v,e)

    summary_df_p = summary_df.pivot_table(index='variable',columns='item',values='value').reset_index().set_index('variable')

    y_label = summary_df_p.index
    x_label = summary_df_p.columns
    plt.figure(figsize=(15,15))
    sns.heatmap(summary_df_p,square=True,cmap='binary',vmax=1, xticklabels=True, yticklabels=True,linewidths=1,annot=annot,fmt='',cbar=False)

def compare_template_coverage_map(df1,df2):   

    template_fp = "../applepy/template/Reporting_template_AGMIP_2024-07-11.xlsx"
    AgMIP_xl = pd.read_excel(template_fp,"Variables")
    AgMIP_extended = pd.read_excel(template_fp,"Variables_extended")
    lookup = AgMIP_xl.iloc[0,:]
    template_dict = {'variable':[],
                    'item':[]}
    variables = AgMIP_xl.Variable[1:].unique()
    extended_variables = AgMIP_extended.Variable.values
    items = AgMIP_xl.iloc[0,:].values[3:-2]
    for variable in variables:
        if variable is not np.nan:
            fdf = AgMIP_xl[AgMIP_xl.Variable==variable]
            v_item = [AgMIP_xl.iloc[0,:][col] for col in fdf.columns.drop(['Variable','Description','Unit']) if fdf[col].values[0] == 'X']
            for i in v_item:
                template_dict['variable'].append(variable)
                template_dict['item'].append(i)

    for variable in extended_variables:
        for item in items:
            template_dict['variable'].append(variable)
            template_dict['item'].append(item)

    template_df = pd.DataFrame.from_dict(template_dict)
    template_df['variable'] = pd.Categorical(template_df['variable'], categories=np.hstack([variables,extended_variables]), ordered=True)
    template_df['item'] = pd.Categorical(template_df['item'], categories=items, ordered=True)
    template_df['value'] = None
    template_df.loc[~template_df.variable.isin(extended_variables),'value'] = 1
    template_df.loc[template_df.variable.isin(extended_variables),'value'] = np.nan

    cols =  ['value','variable','item']
    fdf = template_df[cols].drop_duplicates()
    template_df_p = fdf.groupby(['variable','item']).value.nunique().reset_index().pivot_table(index='variable',columns='item',values='value').reset_index().set_index('variable')\

    annot = pd.DataFrame().reindex_like(template_df_p)
    annot[template_df_p==1] = 'x'
    annot[template_df_p==0] = ''
    annot = annot.to_numpy()

    summary_df = template_df.copy()
    summary_df['value'] = 0
    for v in df1.variable.unique():
        try: 
            i = df1[df1.variable==v].item.unique()
            summary_df.loc[(summary_df.variable==v) & (summary_df.item.isin(i)),'value'] = 0.5
        except Exception as e:
            print(v,e)

    for v in df2.variable.unique():
        try: 
            i = df2[df2.variable==v].item.unique()
            summary_df.loc[(summary_df.variable==v) & (summary_df.item.isin(i)),'value'] = 1
        except Exception as e:
            print(v,e)

    summary_df_p = summary_df.pivot_table(index='variable',columns='item',values='value').reset_index().set_index('variable')

    y_label = summary_df_p.index
    x_label = summary_df_p.columns
    plt.figure(figsize=(15,15))
    sns.heatmap(summary_df_p,square=True,cmap='binary', xticklabels=True, yticklabels=True,linewidths=1,annot=annot,fmt='',cbar=True)
    plt.tight_layout()