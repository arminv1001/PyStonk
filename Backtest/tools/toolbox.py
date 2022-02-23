import numpy as np
import pandas as pd
import os

PATH = '/Users/mr.kjn/Projects/PyStonk/Backtest/'



def get_long_short_dates(master_df):
    """
    Return list of long, short dates and of excess dates

    Returns:
        np.array: array of long, short & excess dates 
    """
    long_dates = np.array(master_df[master_df == 1].index)
    short_dates = np.array(master_df[master_df == -1].index)

    long_dates_list = None
    short_dates_list = None
    excess_dates = None

    # clear excess dates
    if len(short_dates) < len(long_dates):
        excess = len(long_dates) - len(short_dates)
        long_dates_list = delete_list_by_index(long_dates, excess)
        excess_dates = long_dates[len(long_dates)-excess:]
        short_dates_list = short_dates
    elif len(long_dates) < len(short_dates):
        excess = len(short_dates) - len(long_dates)
        short_dates_list = delete_list_by_index(short_dates, excess)
        excess_dates = short_dates[len(short_dates)-excess:]
        long_dates_list = long_dates
    else:
        long_dates_list = long_dates
        short_dates_list = short_dates

    return long_dates_list, short_dates_list, excess_dates

def delete_list_by_index(del_list, excess):
    """
    Deletes last excess entries of list

    Args:
        del_list (np.array): list to be shorten
        excess (float): excess entries

    Returns:
        list: excess cleared list
    """
    end = len(del_list)
    start = end - excess
    array = np.array(del_list)
    index = [i for i in range(start, end)]
    
    return list(np.delete(array,index))

def get_filenames_from(folder, ending=''):
    """
    Get list of all CSV filanmes in directory

    Returns:
        list: list of all CSV filenames
    """
    path = os.path.join(PATH, folder)
    filenames = os.listdir(path)
    return [filename for filename in filenames if filename.endswith(ending)]

def get_number_of_weeknds(long_dates, short_dates):
    """
    Returns list with number of weeknds per time period

    Args:
        long_dates (pandas.core.indexes.datetimes.DatetimeIndex): Long Dates
        short_dates (pandas.core.indexes.datetimes.DatetimeIndex): Short Dates

    Returns:
        list: list with number of weeknds per time period
    """
    num_weeknds = []
    for i in range(0,len(long_dates)):
        num_weeknds.append(len(get_weeknd(long_dates[i], short_days[i])))
    
    return num_weeknds