import numpy as np
import pandas as pd

class MasterDataFrame(object):

    def __init__(self, symbol, df, start_capital, comission):

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

        self.master_df['Capital'] = self.master_df['Capital'].fillna(method="ffill") # forward fill NaN
        self.master_df['PnL'] = self.master_df['Capital'].diff() # Profit & Loss between Rows
        self.master_df['PnL in Pct'] = self.master_df['Capital'].pct_change() # Profit & Loss in % between Rows
        self.master_df['Equity'] = self.master_df['PnL'].cumsum() # cumulative PnL
        self.master_df['Equity in Pct'] = self.master_df['PnL in Pct'].cumsum() # cumulative PnL in pct

    def _create_capital_col(self):
        capital = self.master_df['Capital'][0]
        for index in self.master_df[self.master_df['Position'] != 0].index:
            current_row = self.master_df.loc[index]
            capital = self._calculate_new_capital(capital, current_row)
            self.master_df.loc[index, 'Capital'] = capital
            #self.master_df.insert(loc=index, column='Capital', value=capital)


    def _calculate_new_capital(self, old_capital, current_row):
        factor = current_row['Position'] # Long: -1, Short: +1
        new_capital = old_capital - factor*(current_row[self.symbol] * current_row['Size'] - current_row['Comission'])  # 'AAPL' = 'Close Price'
        return new_capital

        
        
    def get_dataframe(self):
        return self.master_df

        """
        def _create_id(self):
            
            Creates unique identifier for trade: "<Symbol> + <crosssum of date>"
            
            date = self.opendt.split(" ")[0].split("-")
            date = [int(string) for string in date]
            date_crosssum = sum(date)
            self.id = self.symbol + str(date_crosssum)
        """

        def _calculate_pnl(self):
            """
            Calculates the profit & loss of a open or close trade 
            """
            factor = -1 if self.isOpen else 1 # entry=-1, exit=1
            self.pnl_val = self.current_capital - factor*(self.price * self.size - self.comission)
            self.pnl_pct = self.pnl_val/self.current_capital

