import numpy as np
import pandas as pd
import os

PATH = '/Users/mr.kjn/Projects/PyStonk/Backtest/'


def color_win_loss(val):
    color = 'limegreen' if val > 0 else '#cd4f39'
    return f'background-color: {color}'


def get_consecutive(trade_history, of_wins=True):
    """
    Returns the value of the longest consecutive of winners/losers

    Args:

        of_wins (bool, optional): winners or losers. Defaults to True.

    Returns:
        float: consecutive
    """

    consecutive = 0
    longest_run = 0
    for ret in trade_history:

        # winner trades
        if of_wins:
            if ret > 0:
                consecutive = consecutive + 1
            else:
                consecutive = 0
                if consecutive > longest_run:
                    longest_run = consecutive
        # loser trades
        else:
            if ret < 0:
                consecutive = consecutive + 1
            else:
                consecutive = 0
                if consecutive > longest_run:
                    longest_run = consecutive

    return longest_run


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



