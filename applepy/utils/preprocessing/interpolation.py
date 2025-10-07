import pandas as pd
import numpy as np


def interp_years_df(df,interp_years,return_type = 'df'):
    """
    Interpolate missing values in a DataFrame for specified years.

    This function interpolates the values for specific years (given by `interp_years`) that
    are not present in the input DataFrame `df`, based on the existing data. The DataFrame 
    must represent data from a single combination of model, scenario, region, variable, 
    item, and unit, as indicated by the columns.

    Parameters
    ----------
    df : pandas.DataFrame
        A DataFrame containing columns 'year' and 'value', along with metadata columns 
        'model', 'scenario', 'region', 'variable', 'item', and 'unit'. The DataFrame should 
        be grouped and filtered so that it contains data for only one unique combination 
        of these metadata columns.
        
    interp_years : array-like
        An array or list of years for which values need to be interpolated. These years 
        should lie within the range of the existing 'year' column in `df` and should not 
        already be present in `df`.
        
    return_type : str, optional
        Specifies the format of the returned interpolated data. Possible values are:
        - 'array': Returns the interpolated values as a numpy array.
        - 'df': Returns the interpolated data as a pandas DataFrame.
        - 'dict': Returns the interpolated data as a dictionary.
        - 'merged': Returns a DataFrame that includes both the original and interpolated 
          data, sorted by year.
        The default is 'df'.

    Returns
    -------
    numpy.ndarray or pandas.DataFrame or dict
        The format of the returned data depends on the `return_type` parameter:
        - If 'array', returns the interpolated values as a numpy array.
        - If 'df', returns a DataFrame with the interpolated years and values.
        - If 'dict', returns a dictionary with the interpolated data.
        - If 'merged', returns a DataFrame combining the original and interpolated data, 
          sorted by the 'year' column.
    
    Raises
    ------
    AssertionError
        If the DataFrame contains more than one unique value for any of the columns 'model', 
        'scenario', 'region', 'variable', 'item', or 'unit'.
        
    ValueError
        If `interp_years` contains years outside the range of the existing 'year' column 
        in `df`, or if an unrecognized `return_type` is specified.
    
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'model': ['Model1'],
    ...     'scenario': ['Scenario1'],
    ...     'region': ['Region1'],
    ...     'variable': ['Variable1'],
    ...     'item': ['Item1'],
    ...     'unit': ['Unit1'],
    ...     'year': [2000, 2005, 2010, 2015],
    ...     'value': [10, 20, 30, 40]
    ... })
    >>> interp_years = [2003, 2008, 2012]
    >>> result_df = interp_years_df(df, interp_years, return_type='df')
    >>> result_df
         model   scenario   region   variable   item   unit  year  value
    0  Model1  Scenario1  Region1  Variable1  Item1  Unit1  2003   16.0
    1  Model1  Scenario1  Region1  Variable1  Item1  Unit1  2008   26.0
    2  Model1  Scenario1  Region1  Variable1  Item1  Unit1  2012   33.0

    """

    # check that the df only has one value (if used within pc_diff it should be already grouped by model, scenario, region, variable, item, unit)
    cols = ['model', 'scenario', 'region', 'variable', 'item', 'unit']
    assert all(df[cols].nunique()==1), "this DataFrame has values from different sets"

    df = df.sort_values('year')
    xp = df['year'].to_numpy()
    yp = df['value'].to_numpy()
    
    # remove years in interp_years that are already evaluated in xp
    interp_years = np.delete(interp_years,np.argwhere(np.isin(interp_years,xp)))
    # check that all values in interp_years are within the bounds of the data
    assert (min(interp_years)>min(xp)) & ((max(interp_years)<max(xp))), "interp_years out of range of DataFrame years"

    y = np.interp([interp_years],xp,yp)[0]
    interp_dict = {'model' : [df.model.values[0]]*len(interp_years),
                'scenario' : [df.scenario.values[0]]*len(interp_years),
                'region':[df.region.values[0]]*len(interp_years),
                'variable':[df.variable.values[0]]*len(interp_years),
                'item':[df.item.values[0]]*len(interp_years),
                'unit':[df.unit.values[0]]*len(interp_years),
                'year': interp_years,
                'value': y
    }
    interp_df = pd.DataFrame(interp_dict)

    if return_type == 'array':
        return y
    elif return_type == 'dict':
        return interp_dict
    elif return_type == 'df':
        return interp_df
    elif return_type == 'merged':
        return pd.concat([df,interp_df],ignore_index=True).sort_values('year')
    else:
        raise ValueError("unrecognized return_type. Must be 'array','df','merged',or 'dict'.")

    
def interp_base_year(k_df,base_year):
    """
    Interpolate data for a specific base year across all scenarios in the input DataFrame.

    This function iterates through each unique scenario in the input DataFrame,
    interpolates the data for the specified base year, and adds the interpolated
    data back to the original DataFrame.

    Parameters:
    -----------
    k_df : pandas.DataFrame
        The input DataFrame containing scenario data.
    base_year : int
        The year for which to interpolate data.

    Returns:
    --------
    pandas.DataFrame
        The original DataFrame with interpolated data for the base year added.

    Notes:
    ------
    - The function uses an external 'interp_years_df' function for interpolation.
    - The interpolation is performed with 'return_type' set to 'df'.
    - The interpolated data is concatenated with the original DataFrame.
    """
        
    for s in k_df.scenario.unique():
        k_df_s = k_df[k_df.scenario==s]
        return_type = 'df' #'df', 'merged' , 'dict'
        interp_years =  [base_year]
        interp_df = interp_years_df(k_df_s,interp_years,return_type=return_type)
        k_df = pd.concat([k_df,interp_df],ignore_index=True)

    return k_df