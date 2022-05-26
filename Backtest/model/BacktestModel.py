import numpy as np
import pandas as pd
import yfinance as yf
import sqlite3

from data_prep.CSVDataPreparer import *
from equity.Equity import *
from statistics.spreadsheet import *
from tools.toolbox import *
from trade_history.TradeHistory import *
from strategy.strategy1 import *


sys.path.append('.')
from Daten.Datahandler import Datahandler

CSV_DIR = os.path.join(os.path.abspath(os.curdir), "Backtest/backtest_data")


class BacktestModel(object):
    """
    BacktestModel is responsible for providing all Backtest-relevant data

    """

    def __init__(self, view_settings_dict):

        self.__database_name = view_settings_dict['database_name']
        self.__strategy = view_settings_dict['strategy']
        self.__data_source_s = view_settings_dict['data_source_s']
        self.__date_source_b = view_settings_dict['data_source_b']
        self.__symbol = view_settings_dict['symbols']
        self.__benchmark_symbol = view_settings_dict['benchmark']

        self.__start_date_time = view_settings_dict['start_date_time']
        self.__end_date_time = view_settings_dict['end_date_time']
        self.__periodicity = view_settings_dict['periodicity']

        self.__start_capital = view_settings_dict['start_capital']
        self.__size = view_settings_dict['size']
        self.__comission = view_settings_dict['comission']
        self.__rfr = view_settings_dict['risk-free rate']

        self.__parameter = view_settings_dict['parameter']

        self.__set_all()
        self.__create_database()

    @property
    def master_df(self):
        return self.__master_df_s

    def trade_history(self):
        return self.__trade_history_s

    @property
    def spreadsheet(self):
        return self.__spreadsheet

    @property
    def drawdown_df(self):
        return self.__drawdown.complete_df

    @property
    def equity_df(self):
        return self.__equity_df


    def __create_database(self):

        conn = sqlite3.connect(self.__database_name) 

        c = conn.cursor()

        c.execute('CREATE TABLE IF NOT EXISTS master_df (Date date, Open number, High number, Close number, Low number, Volume number, Turnover number, Unadjusted_Close number, Dividend number, Signal number)')
        c.execute('CREATE TABLE IF NOT EXISTS equity (Date date, Equity number, Equity_pct number, log_Equity number, log_Equity_pct number)')
        c.execute('CREATE TABLE IF NOT EXISTS trade_history (Start_Date date, End_Date date, Buy_Price number, Sell_Price number, Return number, Return_pct number, Bars_Held number, Size number)')
        c.execute('CREATE TABLE IF NOT EXISTS drawdown (Date date, Drawdown number, Drawdown_pct number)')

        c.execute('CREATE TABLE IF NOT EXISTS general_info (Metric text, Data number)')
        c.execute('CREATE TABLE IF NOT EXISTS performance_info (Metric text, Data number)')
        c.execute('CREATE TABLE IF NOT EXISTS all_trades_info (Metric text, Data number)')
        c.execute('CREATE TABLE IF NOT EXISTS winners (Metric text, Data number)')
        c.execute('CREATE TABLE IF NOT EXISTS losers (Metric text, Data number)')
        c.execute('CREATE TABLE IF NOT EXISTS runs_info (Metric text, Data number)')

        conn.commit()
        equity_df = self.__equity_df.set_index(self.__master_df_s.index)
        equity_df = self.equity_df.reset_index()
        equity_df = equity_df.rename(columns={'index': "Date"})
        drawdown_df = self.__drawdown.complete_df.set_index(self.__master_df_s.index)
        drawdown_df = self.drawdown_df.reset_index()
        drawdown_df = drawdown_df.rename(columns={'index': "Date"})
        master_df_s = self.__master_df_s.reset_index()
        master_df_s = master_df_s.rename(columns={'index': "Date"})

        general_info = self.__spreadsheet.general_info.reset_index()
        performance_info = self.__spreadsheet.performance_info.reset_index()
        all_trades_info = self.__spreadsheet.all_trades_info.reset_index()
        winners = self.__spreadsheet.winners.reset_index()
        losers = self.__spreadsheet.losers.reset_index()
        runs_info = self.__spreadsheet.runs_info.reset_index()

        master_df_s.to_sql('master_df', conn, if_exists='replace', index = False)
        equity_df.to_sql('equity', conn, if_exists='replace', index = False)
        self.__trade_history_s.df.to_sql('trade_history', conn, if_exists='replace', index = False)
        drawdown_df.to_sql('drawdown', conn, if_exists='replace', index = False)

        general_info.to_sql('general_info', conn, if_exists='replace', index = False)
        performance_info.to_sql('performance_info', conn, if_exists='replace', index = False)
        all_trades_info.to_sql('all_trades_info', conn, if_exists='replace', index = False)
        winners.to_sql('winners', conn, if_exists='replace', index = False)
        losers.to_sql('losers', conn, if_exists='replace', index = False)
        runs_info.to_sql('runs_info', conn, if_exists='replace', index = False)


    def __set_all(self):
        """
        Creates all relevant objects
        """

        self.__set_master_dfs()
        self.__set_equity()
        self.__set_trade_histories()
        self.__set_drawdown()    
        self.__set_performance_measurement()
        self.__set_spreadsheet()

    
    def __set_master_dfs(self):
        """
        Creates Master DF containing stock data and buy/sell signals
        """

        

        # self.__master_df_s = self.__get_data_df(
        #     self.__symbol,
        #     self.__start_date_time,
        #     self.__end_date_time,
        #     self.__data_source_s)

        # self.__master_df_b = self.__get_data_df(
        #     self.__benchmark_symbol,
        #     self.__start_date_time,
        #     self.__end_date_time,
        #     self.__date_source_b)

        self.__master_df_s = run_strategy(self.__strategy, self.__symbol, self.__data_source_s, self.__parameter)
        self.__master_df_s = self.__master_df_s.set_index('Date')
        self.__master_df_s.index = pd.to_datetime(self.__master_df_s.index)

        self.__master_df_b = run_strategy(self.__strategy, self.__benchmark_symbol, self.__data_source_s, self.__parameter)
        self.__master_df_b =  self.__master_df_b.set_index('Date')
        self.__master_df_b.index = pd.to_datetime(self.__master_df_b.index)

    def __set_equity(self):
        """
        Creates Equity for strategy and benchmark and Equity DataFrame
        """
       
        self.__equity_s = Equity(
            self.__symbol,
            self.__master_df_s[['Close', 'Signal']],
            self.__start_capital,
            self.__comission,
            self.__size)

        self.__equity_b = Equity(
            self.__benchmark_symbol,
            self.__master_df_b[['Close', 'Signal']],
            self.__start_capital,
            self.__comission,
            self.__size)

        self.__equity_df = self.__equity_s.df
        self.__equity_df['Benchmark'] = self.__equity_s.df['Equity'] - \
            self.__equity_b.df['Equity']
        self.__equity_df['Benchmark %'] = self.__equity_s.df['Equity %'] - self.__equity_b.df['Equity %']
        self.__equity_df['log Benchmark'] = self.__equity_s.df['log Equity'] - \
            self.__equity_b.df['log Equity']
        self.__equity_df['log Benchmark %'] = self.__equity_s.df['log Equity %'] - \
            self.__equity_b.df['log Equity %']


        
    def __set_trade_histories(self):
        """
        Creates TradeHistory object for strategy and benchmark 
        """

        self.__trade_history_s = TradeHistory(
            self.__master_df_s[['Close', 'Signal']],
            self.__equity_s.complete_df,
            self.__size)

        self.__trade_history_b = TradeHistory(
            self.__master_df_b[['Close','Signal']],
            self.__equity_b.complete_df,
            self.__size)

    def __set_drawdown(self):
        """
        Creates Drawdown object for strategy
        """

        self.__drawdown = Drawdown(self.__equity_s.df)
        

    def __set_performance_measurement(self):
        """
        Creates PerformanceMeasurement object for strategy
        """

        self.__performance_measurement = PerformanceMeasurement(
            self.__equity_s.df,
            self.__trade_history_s.df,
            self.__trade_history_b.df,
            self.__periodicity,
            self.__rfr
        )
        

    def __set_spreadsheet(self):
        """
        Creates Spreadsheet object 
        """

        self.__spreadsheet = SpreadSheet(
            self.__master_df_s,
            self.__equity_s.df,
            self.__trade_history_s.df,
            self.__performance_measurement,
            self.__drawdown,
            self.__start_capital,
            self.__comission,
            self.__periodicity)

    def __get_data_df(self, symbol, start_date, end_date, source):
        """
        Gets stock data of symbol for given timeframe

        Args:
            symbol (str): Symbol
            start_date (datetime): Start Time
            end_date (datetime): End Time
            source (str): Source from which the stock data is retrivied from

        Returns:
            DataFrame: DataFrame containing stock data
        """
        
        

        # # Retrieves from Yahoo Finance Data
        # if source == 'Yahoo Finance':

        #     master = yf.Ticker(symbol[0])
        #     master_df = master.history(start_date, end_date)

        # # Retrieves Data from backtest_data folder
        # elif source == '.csv':
        #     master_df = data_handler.getAlternativData()

        #     csvDP = CSVDataPreparer(csv_symbols=symbol)
        #     master_df = csvDP.get_assets_historic_data(
        #         start_date, end_date, symbol)

        return master_df
