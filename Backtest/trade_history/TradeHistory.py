import numpy as np
import pandas as pd

from tools.toolbox import *

LONG_ONLY = True


class TradeHistory(object):
    """
    TradeHistory contains all information about all trades of strategy

    """

    def __init__(self, df, equity_df, size):
        self.__master_df = df
        self.__equity_df = equity_df
        self.__long_dates, self.__short_dates, self.__excess_dates = self.__get_long_short_dates()
        self.__buy_price = self.__get_close(self.__long_dates)
        self.__sell_price = self.__get_close(self.__short_dates)
        self.__returns, self.__returns_pct = self.__get_return_of_trades()
        self.__bars_held = self.__get_bars_held()
        self.__sizes = self.__get_sizes(size)
        
        self.__df = self.__create_trade_history_df()


    @property
    def df(self):
        print(self.__df)
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
            'Buy Price': self.__buy_price,
            'Sell Price': self.__sell_price,
            'Return': self.__returns,
            'Return %': self.__returns_pct,
            'Bars Held': self.__bars_held,
            'Size': self.__sizes
        }

        trade_hist = pd.DataFrame.from_dict(data, orient='index').transpose()
        trade_hist = trade_hist.rename(columns={0: "Data"})
        

        return trade_hist

    

    def __get_close(self, dates):
        """
        Return close price for given date

        Args:
            dates (datetime): date

        Returns:
            float: close price
        """

        closes = []
        for date in dates:
            close = self.__master_df.at[date, 'Close']
            closes.append(close)
        
        return closes

    def __get_long_short_dates(self):
        """
        Return list of long, short dates and of excess dates

        Returns:
            np.array: array of long, short & excess dates 
        """
        signals = self.__master_df['Signal']
        long_dates = np.array(signals[signals == 1].index)
        short_dates = np.array(signals[signals == -1].index)


        if LONG_ONLY:
            # first position must be long and before first short date
            i = 0

            if long_dates[0] > short_dates[0]:
                for date in short_dates:
                    if date > long_dates[0]:
                        i += 1
                    else:
                        break

                short_dates = np.delete(short_dates, np.s_[:i+1])


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
        """
        Return list of returns of all finished trades

        Returns:
            list: returns in abs. & pct
        """
        
        equity = self.__equity_df['Equity']
        equity_pct = self.__equity_df['Equity %']

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
            bars_held.append(float(bars))

        return np.array(bars_held)

    def __get_sizes(self, size_val):
        """
        Returns list of sizes of the trades

        Args:
            size_val (pd Series): size values

        Returns:
            list: sizes
        """
        sizes_df = self.__equity_df['Size']

        sizes = []

        if size_val > 0:
            sizes = [size_val for date in self.__long_dates]
        else:
            for i in range(0, len(self.__long_dates)):
                long_index = sizes_df.index.get_loc(self.__long_dates[i])
                size = sizes_df[long_index]
                sizes.append(size)

        return sizes



