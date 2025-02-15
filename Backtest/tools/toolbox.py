"""
Module with various function that are used in Backtest

"""
import numpy as np
import pandas as pd
import os
import sqlite3

PATH = os.path.abspath(os.curdir)
DATABASE_INFO = {
    'master_df': ['Timestamp', 'Open' , 'High' , 'Close' , 'Low' , 'Volume' , 'Signal'],
    'equity': ['Timestamp', 'Equity', 'Equity %', 'log Equity', 'log Equity %', 'Benchmark', 'Benchmark %', 'log Benchmark', 'log Benchmark %'],
    'trade_history': ['Start Date', 'End Date', 'Buy Price', 'Sell Price', 'Return', 'Return %', 'Bars Held', 'Size'],
    'drawdown': ['Timestamp', 'Drawdown', 'Drawdown %'],

    'general_info': ['Metric', 'Data'],
    'performance_info': ['Metric', 'Data'],
    'all_trades_info': ['Metric', 'Data'],
    'winners': ['Metric', 'Data'],
    'losers': ['Metric', 'Data'],
    'runs_info': ['Metric', 'Data']
}
  

def get_df_from_database(database_name, table_name, col_names="*"):
    """
    Returns DataFrame from given Database

    Args:
        database_name (str): database name
        table_name (str): table name
        col_names (str, optional): column name. Defaults to "*".

    Returns:
        pd.DataFrame: DataFrame
    """

    # set cursor
    db_dir = os.path.join(os.path.abspath(os.curdir), 'export/database/') + database_name
    conn = sqlite3.connect(db_dir)
    c = conn.cursor()

    # set column names
    if col_names != '*': # all columns
        columns = col_names
        col_names_str = ", ".join(col_names)

    else: # specific column
        columns = DATABASE_INFO[table_name]
        col_names_str = col_names

    c.execute("SELECT " + col_names_str + " FROM " + table_name)

    df = pd.DataFrame(c.fetchall(), columns=columns)

    # fix index
    date_df_list = ['master_df', 'equity', 'drawdown']
    index_df_list = ['general_info', 'performance_info', 'all_trades_info', 'winners', 'losers', 'runs_info']
    if table_name in date_df_list:
        df = df.set_index('Timestamp')
    elif table_name in index_df_list:
        df = df.set_index('Metric')

    return df

def color_win_loss(val):
    """
    Returns color string for pd dataframe

    Args:
        val (str): val

    Returns:
        str: color string
    """
    color = 'limegreen' if val > 0 else '#cd4f39'
    return f'background-color: {color}'


def get_consecutive(trade_history, of_wins=True):
    """
    Returns the value of the longest consecutive of winners/losers

    Args:
        trade_history (pd Series): trade history
        of_wins (bool, optional): wins or loss. Defaults to True.

    Returns:
        int: returns longest run in bars
    """

    consecutive = 0
    longest_run = 0
    for ret in trade_history:
        # winner trades
        if of_wins:
            if ret > 0:
                consecutive += 1
            elif ret < 0:
                if consecutive > longest_run:
                    longest_run = consecutive
                consecutive = 0
        # loser trades
        else:
            if ret < 0:
                consecutive += 1
            else:
                if consecutive > longest_run:
                    longest_run = consecutive
                consecutive = 0

    return longest_run


def get_equal_len_list(list1, list2):
    """
    Shortens lists to the same size and creates list of excess data

    Args:
        list1 (list): list 1
        list2 (list ): list 2

    Returns:
        [type]: [description]
    """
    excess_list = []

    if len(list1) < len(list2):
        excess = len(list2) - len(list1)
        list2_list = delete_list_by_index(list2, excess)
        excess_list = list2[len(list2)-excess:]
        list1_list = list1
    elif len(list2) < len(list1):
        excess = len(list1) - len(list2)
        list1_list = delete_list_by_index(list1, excess)
        excess_list = list1[len(list1)-excess:]
        list2_list = list2
    else:
        list2_list = list2
        list1_list = list1

    return list2_list, list1_list, excess_list


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
    
    return np.delete(array,index)

def get_filenames_from(folder, ending=''):
    """
    Get list of all CSV filanmes in directory

    Args:
        folder: folder to get filenames from
        endings: ending of filenames

    Returns:
        list: list of all CSV filenames
    """
    folder = "Backtest/" + folder
    path = os.path.join(PATH, folder)
    filenames = os.listdir(path)
    return [filename for filename in filenames if filename.endswith(ending)]

def get_number_of_weeknds(list2, list1):
    """
    Returns list with number of weeknds per time period

    Args:
        list2 (pandas.core.indexes.datetimes.DatetimeIndex): Long Dates
        list1 (pandas.core.indexes.datetimes.DatetimeIndex): Short Dates

    Returns:
        list: list with number of weeknds per time period
    """
    num_weeknds = []
    for i in range(0,len(list2)):
        num_weeknds.append(len(get_weeknd(list2[i], short_days[i])))
    
    return num_weeknds



