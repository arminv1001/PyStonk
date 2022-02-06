import numpy as np
import pandas as pd

# CLOSE PRICE = __SYMBOL ÄNDERN

class Equity(object):

    def __init__(self, __symbol, df, start_capital, comission):

        """
        Note:
        df: DataFrame contains Close Price, Position
        """
        self.__symbol = __symbol
        self.__master_df = df
        self.__equity_df = pd.DataFrame(index = self.__master_df.index)
        self.__comission = comission

        self.__master_df['Capital'] = np.nan
        self.__master_df['Capital'][0] = start_capital
        self.__master_df['Size'] = 1 # wie wird das angeben sp äter ?

    @property
    def equity_df(self):
        return self.__equity_df

    def create(self):
        
        self.create_capital_col()    

        self.__equity_df['Return'] = self.__master_df['Capital'].diff() # Profit & Loss between Rows
        self.__equity_df['Return'][0] = 0 # Profit & Loss in % between Rows

        self.__equity_df['Return %'] = self.__master_df['Capital'].pct_change()
        self.__equity_df['Return %'][0] = 0

        # cumulative Return
        self.__equity_df['Equity'] = self.__equity_df['Return'].cumsum()
        self.__equity_df['Equity'][0] = 0

        self.__equity_df['Equity %'] = self.__equity_df['Return %'].cumsum()  # cumulative Return %
        self.__equity_df['Equity %'][0] = 0

    def create_capital_col(self):
        """
        Creates a column in MasterDataFrame which contains the current capital
        """
        capital = self.__master_df['Capital'][0]
        for index in self.__master_df[self.__master_df['Position'] != 0].index: # go through rows where a Position is indicated
            current_row = self.__master_df.loc[index] 
            capital = self._calculate_new_capital(capital, current_row)
            self.__master_df.loc[index, 'Capital'] = capital # set new capital in cell

        self.__master_df['Capital'] = self.__master_df['Capital'].fillna(
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
        new_capital = old_capital - factor * \
            (current_row[self.__symbol] * current_row['Size'] -
             self.__comission)  # 'AAPL' = 'Close Price'
        return new_capital

        
        
    def get_dataframe(self):
        
        return self.__master_df.drop(columns=[self.__symbol, 'Position'])

        """
        def _create_id(self):
            
            Creates unique identifier for trade: "<__Symbol> + <crosssum of date>"
            
            date = self.opendt.split(" ")[0].split("-")
            date = [int(string) for string in date]
            date_crosssum = sum(date)
            self.id = self.__symbol + str(date_crosssum)
        """


