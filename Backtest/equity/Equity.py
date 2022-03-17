import numpy as np
import pandas as pd

class Equity(object):

    def __init__(self, symbol, df, start_capital, comission, size=1):

        """
        Note:
        df: DataFrame contains Close Price, Position
        """
        self.__symbol = symbol
        self.__master_df = df
        self.__comission = comission
        self.__start_capital = start_capital
        self.__size = size
        self.__capital_df = self.__create_capital()
        self.__equity_df = self.__create_equity()
        self.__complete_df = pd.concat([self.__capital_df, self.__equity_df], axis=1)

    @property
    def complete_df(self):
        return self.__complete_df
    
    @property
    def df(self):
        return self.__equity_df
    

    def __create_equity(self):

        equity_df = pd.DataFrame(index=self.__master_df.index)
        equity_df['Equity'] = self.__capital_df['Capital'][self.__master_df['Position'] < 0]
        equity_df['Equity'][0] = self.__start_capital
        equity_df = equity_df.ffill()

        equity_df['Equity %'] = equity_df['Equity'] / self.__start_capital * 100
        equity_df['Equity %'][0] = 100  

        return equity_df

    def __create_capital(self):
        """
        Creates a column in MasterDataFrame which contains the current capital
        """
        df = pd.DataFrame(index=self.__master_df.index)
        df['Capital'] = np.nan
        df['Capital %'] = np.nan
        df['Size'] = np.nan
        old_capital = self.__start_capital
        size = 0

        # go through rows where a Position is indicated
        for index in self.__master_df[self.__master_df['Position'] != 0].index:
            current_row = self.__master_df.loc[index]

            if self.__size == 0 and current_row['Position'] == 1:
                size = self.__get_size(current_row, old_capital)
            elif self.__size != 0 and current_row['Position'] == 1:
                size = self.__size

            new_capital = self.__calculate_new_capital(
                old_capital, current_row, size)
            # set new capital in cell
            df.loc[index, 'Capital'] = new_capital

            df.loc[index, 'Capital %'] = new_capital / \
                old_capital * 100  # set new capital in cell

            df.loc[index, 'Size'] = size
            old_capital = new_capital

        df['Capital'][0] = self.__start_capital
        df['Capital %'][0] = 1

        df = df.fillna(method="ffill")  # forward fill NaNs with current capital
        df = df.fillna(0)

        # Profit & Loss between Rows
        df['Profit/Loss'] = df['Capital'].diff()
        df['Profit/Loss'] = 0
        df['Profit/Loss %'] = df['Capital %'].diff()
        df['Profit/Loss %'] = 0

        return df

 

    def __calculate_new_capital(self, old_capital, current_row, size):
        """
        Calculates the current capital after the indicated trade with
        current capital = current capital * factor (close price * order size - comission)

        Args:
            old_capital (float): current capital before the trade
            current_row (pd Dataframe Row): current pd DataFrame Row which represents all the info for a date

        Returns:
            float: new capital after trade
        """

        factor = current_row['Position'] # Long: -1, Short: +1
        new_capital = old_capital - factor * \
            (current_row['Close'] * size -
             self.__comission) 
        return new_capital

    def __get_size(self, current_row, old_capital):
        #To-Do
        return int(old_capital / (current_row['Close'] + self.__comission))
    


