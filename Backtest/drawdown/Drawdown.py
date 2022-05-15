import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class Drawdown(object):
    """
    Drawdown contains all relevant information about drawdowns of strategy

    """

    def __init__(self, equity_df):

        self.__equity_df = equity_df
        self.__drawdown_df, self.__hwm_dates = self.__calculate_drawdown('Equity')
        self.__drawdown_df = self.__drawdown_df * -1
        self.__drawdown_df_pct, _ = self.__calculate_drawdown('Equity %')
        self.__drawdown_df_pct = self.__drawdown_df_pct * -100
        self.__complete_df = pd.concat(
            [self.__drawdown_df, self.__drawdown_df_pct], axis=1)
        self.__complete_df = self.__complete_df.rename(
            columns={'Equity': "Drawdown", 'Equity %': "Drawdown %"})
        self.__durations, self.__durations_bars = self.__calculate_durations()
        self.__max_duration = max(self.__durations)
        self.__max_duration_bars = max(self.__durations_bars)


    @property
    def df(self):
        return self.__drawdown_df

    @property
    def df_pct(self):
        return self.__drawdown_df_pct

    @property
    def max_duration(self):
        return self.__max_duration

    @property
    def max_duration_bars(self):
        return self.__max_duration_bars

    @property
    def complete_df(self):
        return self.__complete_df

    def __calculate_drawdown(self, equity_type):
        """
        Calculates drawdown of equity and indentifies high-watermarks

        Args:
            equity_type (str): name of equity column

        Returns:
            list: drawdown
            list: high-watermarks
        """

        equity = self.__equity_df[equity_type]

        hwm = np.zeros(len(equity.index))  # high water marks (global maximum)
        
        # Get high water marks
        for t in range(0, len(equity.index)):
            hwm[t] = max(hwm[t-1], equity.iloc[t])

        hwm_tmp = list(set(hwm))  # clear redundancy
        
        hwm_dates = [equity[equity == mark].index[0] for mark in hwm_tmp]

        hwm_dates.sort()

        drawdown = (hwm - equity) / hwm

        return drawdown, hwm_dates

    def __calculate_durations(self):
        """
        Calculates the drawdown durations between two high_watermarks in time & bars

        Returns:
            list(datetime): drawdown durations
            list(float): drawdown durations
        """

        dd_durations = [0]
        dd_durations_bars = [0]

        for i in range(len(self.__hwm_dates)):
            if i < len(self.__hwm_dates)-1:
                dd_durations.append(self.__hwm_dates[i+1]-self.__hwm_dates[i])

                fellow_index = self.__equity_df.index.get_loc(
                    self.__hwm_dates[i+1])
                previous_index = self.__equity_df.index.get_loc(
                    self.__hwm_dates[i])

                dd_durations_bars.append(fellow_index - previous_index)

        return dd_durations, dd_durations_bars
