import numpy as np
import pandas as pd

from tools.toolbox import *


class TradeHistory(object):

    def __init__(self, df, size):
        self.__master_df = df
        self.__long_dates, self.__short_dates, self.__excess_dates = self.__get_long_short_dates()
        self.__sizes = self.__get_sizes(size)
        self.__returns, self.__returns_pct = self.__get_return_of_trades()
        self.__bars_held = self.__get_bars_held()
        
        self.__df = self.__create_trade_history_df()

    @property
    def df(self):
        return self.__df

    def __create_trade_history_df(self):
        """
            Retuns DataFrame with history of position: Start Date, End Date, Return, Return %, Bars Held

            Returns:
                pd.DataFrame: History all positions DataFrame
            """

        data = {
            'Start Date': self.__long_dates,
            'End Date': self.__short_dates,
            'Return': self.__returns,
            'Return %': self.__returns_pct,
            'Bars Held': self.__bars_held,
            'Size': self.__sizes
        }

        trade_hist = pd.DataFrame.from_dict(data, orient='index').transpose()
        trade_hist = trade_hist.rename(columns={0: "Data"})

        return trade_hist

    def __get_long_short_dates(self):
        """
        Return list of long, short dates and of excess dates

        Returns:
            np.array: array of long, short & excess dates 
        """
        positions = self.__master_df['Position']
        long_dates = np.array(positions[positions == 1].index)
        short_dates = np.array(positions[positions == -1].index)

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


    def __get_return_of_trades(self):

        equity = self.__master_df['Equity']
        equity_pct = self.__master_df['Equity %']

        returns = []
        returns_pct = []

        for i in range(0, len(self.__long_dates)):
            long_index = equity.index.get_loc(self.__long_dates[i]) - 1
            short_index = equity.index.get_loc(self.__short_dates[i])
            
            ret = equity[short_index] - equity[long_index]
            ret_pct = ret / equity[long_index] * 100
            returns.append(ret)
            returns_pct.append(ret_pct)

        return returns, returns_pct


    def __get_bars_held(self):
        """
            Returns bars held

            Returns:
                np.array: bars held
            """

        bars_held = []

        for i in range(0, len(self.__long_dates)):

            short_index = self.__master_df.index.get_loc(self.__short_dates[i])
            long_index = self.__master_df.index.get_loc(self.__long_dates[i])
            bars = short_index - long_index
            bars_held.append(bars)

        return np.array(bars_held)

    def __get_sizes(self, size_val):
        sizes_df = self.__master_df['Size']

        sizes = []

        if size_val > 0:
            sizes = [size_val for date in self.__long_dates]
        else:
            for i in range(0, len(self.__long_dates)):
                long_index = sizes_df.index.get_loc(self.__long_dates[i])
                size = sizes_df[long_index]
                sizes.append(size)

        return sizes



