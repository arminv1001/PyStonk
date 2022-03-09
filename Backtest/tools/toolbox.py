import numpy as np
import pandas as pd
import os

PATH = '/Users/mr.kjn/Projects/PyStonk/Backtest/'


def get_bars_held(master_df):
    """
        Returns bars held

        Returns:
            np.array: bars held
        """

    long_dates, short_dates, _ = get_long_short_dates(master_df)
    bars_held = []

    for i in range(0, len(long_dates)):

        short_index = master_df.index.get_loc(short_dates[i])
        long_index = master_df.index.get_loc(long_dates[i])
        bars = short_index - long_index
        bars_held.append(bars)

    return np.array(bars_held)

def get_return_of_trades(master_df, long_dates, short_dates):
    returns = []
    returns_pct = []

    for i in range(0, len(long_dates)):
        long_index = master_df.index.get_loc(long_dates[i])
        short_index = master_df.index.get_loc(short_dates[i])
        ret = master_df[short_index] - \
            master_df[long_index]
        ret_pct = ret / master_df[long_index]
        returns.append(ret)
        returns_pct.append(ret_pct)

    return returns, returns_pct

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

def create_trade_history_df(master_df):
    """
        Retuns DataFrame with history of position: Start Date, End Date, Return, Return %, Bars Held

        Returns:
            pd.DataFrame: History all positions DataFrame
        """
    long_dates, short_dates, _ = get_long_short_dates(
        master_df['Position'])
    returns, returns_pct = get_return_of_trades(
        master_df['Close'], long_dates, short_dates)
    bars_held = get_bars_held(master_df['Position'])

    data = {
        'Start Date': long_dates,
        'End Date': short_dates,
        'Return': returns,
        'Return %': returns_pct,
        'Bars Held': bars_held
    }

    trade_hist = pd.DataFrame.from_dict(data, orient='index').transpose()
    trade_hist = trade_hist.rename(columns={0: "Data"})
    return trade_hist

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
            
            if of_wins:
                if ret > 0:
                    consecutive = consecutive + 1
                else:
                    consecutive = 0
                    if consecutive > longest_run:
                        longest_run = consecutive
            else:
                if ret < 0:
                    consecutive = consecutive + 1
                else:
                    consecutive = 0
                    if consecutive > longest_run:
                        longest_run = consecutive

        return longest_run