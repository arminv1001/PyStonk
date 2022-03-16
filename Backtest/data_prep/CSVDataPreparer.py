import os
import numpy as np
import pandas as pd
import pytz

CSV_DIR = os.path.join(os.path.abspath(os.curdir),"Backtest/backtest_data")

class CSVDataPreparer(object):

    def __init__(self, csv_symbols=None):
        self.__csv_dir = CSV_DIR
        self.__csv_symbols = csv_symbols if isinstance(csv_symbols, list) else [csv_symbols]
        self.__asset_dfs = self._load_csvs_into_dfs()

    @property
    def asset_dfs(self):
        return self.__asset_dfs

    def _get_all_asset_csv_filenames(self):
        """
        Get list of all CSV filanmes in directory

        Returns:
            list: list of all CSV filenames
        """
        filenames = os.listdir(self.__csv_dir)
        return [filename for filename in filenames if filename.endswith(".csv")]

    def _get_asset_symbol_from_filename(self, csv_filename):
        """
        Gets the symbol of the asset from the filename.

        Args:
            csv_filename (string): CSV filename

        Returns:
            string: symbol
        """
        return csv_filename.replace(".csv", "")

    def _format_csv_into_df(self, csv_filename):
        """
        Loads a CSV file from directory and converts it into a pd DataFrame.

        Args:
            csv_filename (string): CSV filename

        Returns:
            pd DataFrame: CSV file as pd DataFrame
        """

        csv_df = pd.read_csv(
            os.path.join(self.__csv_dir, csv_filename),
            index_col='Date',
            parse_dates=True
        ).sort_index()

        # Ensure all timestamps are set to UTC for consistency
        csv_df = csv_df.set_index(csv_df.index.tz_localize(pytz.UTC))
        return csv_df

    def _load_csvs_into_dfs(self):
        """
        Loads multiple CSV files and converts them into pd DataFrame by the available CSV symbols.

        Returns:
            dict{symbol : pd DataFrame}: Dictionary with key:symbol-value:pdDataFrame
        """
        
        csv_filenames = []

        if self.__csv_symbols is not None:
            for symbol in self.__csv_symbols:
                if '.csv' not in symbol:
                    csv_filenames.append(symbol+".csv")
                else:
                    csv_filenames.append(symbol)
        else:
            csv_filenames = self._get_all_asset_csv_filenames()

        asset_symbols = {}
        for csv_filename in csv_filenames:
            asset_symbol = self._get_asset_symbol_from_filename(csv_filename)
            csv_df = self._format_csv_into_df(csv_filename)
            asset_symbols[asset_symbol] = csv_df

        return asset_symbols

    def get_assets_historic_data(self, start_dt, end_dt, assets): 
        """
        Gets all historic data of given assests.

        Args:
            start_dt (string): start date
            end_dt (string): end date
            assets (list(string)): list of desired assets
            type (str, optional): Date, Open, High, Low, Close, Volume, Turnover, Unadjusted Close, Dividend. Defaults to "Close".

        Returns:
            pd DataFrame: pd DataFrame containing all historic data
        """
        col_list = []
        for asset in assets:
            if asset in self.__csv_symbols: 
                entry_df = self.__asset_dfs[asset]
                col_list.append(entry_df)
        df = pd.concat(col_list, axis=1).dropna(
            how='all')  # convert into DataFrame & drop NA
        df = df.loc[start_dt:end_dt] # only close prices from start to end dates
        #df.columns = assets # set symbol as column names
        return df
    