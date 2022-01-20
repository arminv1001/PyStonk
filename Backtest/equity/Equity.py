import numpy as np
import pandas as pd

# CLOSE PRICE = SYMBOL ÄNDERN

class Equity(object):

    def __init__(self, symbol, df, start_capital, comission):

        """
        Note:
        df: DataFrame contains Close Price, Position
        """
        self.symbol = symbol
        self.master_df = df
        self._end_date = self.master_df.index[-1]
        self.current_row = None

        self.prev_capital = start_capital # previous capital

        self.master_df['Capital'] = np.nan
        self.master_df['Capital'][0] = start_capital
        self.master_df['Comission'] = comission
        self.master_df['Size'] = 1 # wie wird das angeben später ?


    def create(self):
        
        self._create_capital_col()    

        self.master_df['Return'] = self.master_df['Capital'].diff() # Profit & Loss between Rows
        self.master_df['Return %'] = self.master_df['Capital'].pct_change() # Profit & Loss in % between Rows
        self.master_df['Equity'] = self.master_df['Return'].cumsum() # cumulative Return
        self.master_df['Equity %'] = self.master_df['Return %'].cumsum() # cumulative Return %

    def _create_capital_col(self):
        """
        Creates a column in MasterDataFrame which contains the current capital
        """
        capital = self.master_df['Capital'][0]
        for index in self.master_df[self.master_df['Position'] != 0].index: # go through rows where a Position is indicated
            current_row = self.master_df.loc[index] 
            capital = self._calculate_new_capital(capital, current_row)
            self.master_df.loc[index, 'Capital'] = capital # set new capital in cell

        self.master_df['Capital'] = self.master_df['Capital'].fillna(
            method="ffill")  # forward fill NaNs with current capital


    def _calculate_new_capital(self, old_capital, current_row):
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
        new_capital = old_capital - factor*(current_row[self.symbol] * current_row['Size'] - current_row['Comission'])  # 'AAPL' = 'Close Price'
        return new_capital

        
        
    def get_dataframe(self):
        
        return self.master_df.drop(columns=[self.symbol, 'Position'])

        """
        def _create_id(self):
            
            Creates unique identifier for trade: "<Symbol> + <crosssum of date>"
            
            date = self.opendt.split(" ")[0].split("-")
            date = [int(string) for string in date]
            date_crosssum = sum(date)
            self.id = self.symbol + str(date_crosssum)
        """


