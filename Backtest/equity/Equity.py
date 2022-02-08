import numpy as np
import pandas as pd

# CLOSE PRICE = __SYMBOL ÄNDERN

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
        self.__equity_df = self.create_equity()

    @property
    def equity_df(self):
        return self.__equity_df

    def create_equity(self):
        """
        Creates a column in MasterDataFrame which contains the current capital
        """
        equity_df = pd.DataFrame(index=self.__master_df.index)
        equity_df['Equity'] = np.nan
        equity_df['Equity %'] = np.nan
        old_capital = self.__start_capital


        for index in self.__master_df[self.__master_df['Position'] != 0].index: # go through rows where a Position is indicated
            current_row = self.__master_df.loc[index] 
            new_capital = self.calculate_new_capital(old_capital, current_row)
            # set new capital in cell
            equity_df.loc[index, 'Equity'] = new_capital
            equity_df.loc[index, 'Equity %'] = new_capital / \
                old_capital  # set new capital in cell
            old_capital = new_capital
        
        

        equity_df['Equity'][0] = self.__start_capital
        equity_df['Equity %'][0] = 1

        equity_df = equity_df.fillna(
            method="ffill")  # forward fill NaNs with current capital
        
        #equity_df = equity_df['Equity'].fillna(self.__start_capital)
        

        #equity_df = equity_df['Equity %'].fillna(1)

        # Profit & Loss between Rows
        equity_df['Profit/Loss'] = equity_df['Equity'].diff()
        equity_df['Profit/Loss'][0] = 0
        equity_df['Profit/Loss %'] = equity_df['Equity %'].diff()
        equity_df['Profit/Loss'][0] = 0

        return equity_df


    def calculate_new_capital(self, old_capital, current_row):
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
            (current_row['Close'] * self.__size -
             self.__comission)  # 'AAPL' = 'Close Price'
        return new_capital

        
    


