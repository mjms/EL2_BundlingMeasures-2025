import numpy as np
np.seterr(divide='ignore', invalid='ignore')

def percent_change(old,new):
    """
    Gets the percent change between a new value and an old value

    Parameters
    ----------
    old (numeric): The initial value.
    new (numeric): The new value.

    Returns
    -------
    numeric
    """
    return (new-old)/old * 100

def symmetric_percent_change(old, new):
    """
    Calculates the symmetric percent change between two values.

    Parameters
    ----------
    old (numeric): The initial value.
    new (numeric): The new value.

    Returns
    -------
    numeric: The symmetric percent change between the old and new values.
    """
    return (new-old)/(new+old) * 100

def cagr(start_val,end_val,years):
    """
    Calculate the Compound Annual Growth Rate (CAGR) between a start value and an end value over a given number of years.

    Parameters
    ----------
        start_val (float): The initial value.
        end_val (float): The final value.
        years (int): The number of years over which the growth occurred.

    Returns
    -------
        float: The calculated Compound Annual Growth Rate (CAGR).

    Formula
    -------
        CAGR = ((end_val / start_val) ** (1 / years)) - 1

    Note:
        CAGR represents the geometric progression rate at which the initial value must grow to reach the final value over the given period.
    """
    try:
        return (end_val/start_val)**(1/years)-1
    except:
        return np.nan

def agr(start_val,end_val,years):
    """
    Calculate the annual growth rate (AGR) given the starting value, ending value, and number of years.

    Parameters
    ----------
        start_val (float): The initial value.
        end_val (float): The final value.
        years (int): The number of years over which the growth occurred.

    Returns
    -------
        float: The annual growth rate (AGR).

    Note:
        AGR is calculated as ((end_val/start_val) - 1) / years.
        If any error occurs during calculation, returns NaN (Not a Number).
    """
    try:
        return ((end_val/start_val)-1)/years
    except:
        return np.nan