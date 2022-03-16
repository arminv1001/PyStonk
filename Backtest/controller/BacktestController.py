import numpy as np
import pandas as pd
import yfinance as yf

from data_prep.CSVDataPreparer import *
from equity.Equity import *
from statistics.spreadsheet import *
from tools.toolbox import *
from trade_history.TradeHistory import *
from strategy.strategy1 import *


class BacktestController(object):

    def __init__(self, view_settings_dict):

        self.__strategy = view_settings_dict['strategy']
        self.__data_source_s = view_settings_dict['data_source_s']
        self.__date_source_b = view_settings_dict['data_source_b']
        self.__symbol = view_settings_dict['symbols']
        self.__benchmark_symbol = view_settings_dict['benchmark']
        self.__start_date_time = view_settings_dict['start_date_time']
        self.__end_date_time = view_settings_dict['end_date_time']
        self.__start_capital = view_settings_dict['start_capital']
        self.__periodicity = view_settings_dict['periodicity']
        self.__size = view_settings_dict['size']
        self.__comission = view_settings_dict['comission']
        self.__rfr = view_settings_dict['risk-free rate']

        self.__set_all()

    @property
    def master_df(self):
        return self.__master_df_s

    @property
    def spreadsheet(self):
        return self.__spreadsheet

    @property
    def drawdown_df(self):
        return self.__drawdown.complete_df

    def __set_all(self):
        self.__set_master_dfs()
        self.__set_trade_histories()
        self.__set_drawdown()    
        self.__set_performance_measurement()
        self.__set_spreadsheet()

    
    def __set_master_dfs(self):

        self.__master_df_s = self.__get_data_df(
            self.__symbol,
            self.__start_date_time,
            self.__end_date_time,
            self.__data_source_s)

        self.__master_df_b = self.__get_data_df(
            self.__symbol,
            self.__start_date_time,
            self.__end_date_time,
            self.__data_source_s)

        self.__master_df_s = run_strategy(self.__master_df_s)
        self.__master_df_b = run_strategy(self.__master_df_b)

        self.__equity_s = Equity(
            self.__symbol,
            self.__master_df_s,
            self.__start_capital,
            self.__comission,
            self.__size)

        self.__equity_b = Equity(
            self.__symbol,
            self.__master_df_b,
            self.__start_capital,
            self.__comission,
            self.__size)

        self.__master_df_s = pd.concat(
            [self.__master_df_s, self.__equity_s.df], axis=1)

        self.__master_df_b = pd.concat(
            [self.__master_df_b, self.__equity_b.df], axis=1)

        
        
    def __set_trade_histories(self):
        self.__trade_history_s = TradeHistory(
            self.__master_df_s[['Equity', 'Equity %', 'Position', 'Size']],
            self.__size)

        self.__trade_history_b = TradeHistory(
            self.__master_df_b[['Equity', 'Equity %', 'Position', 'Size']],
            self.__size)

    def __set_drawdown(self):
        self.__drawdown = Drawdown(self.__master_df_s[['Equity', 'Equity %']])
        

    def __set_performance_measurement(self):
        self.__performance_measurement = PerformanceMeasurement(
            self.__master_df_s[['Equity', 'Equity %']],
            self.__master_df_b[['Equity', 'Equity %']],
            self.__trade_history_s.df,
            self.__trade_history_b.df,
            self.__periodicity,
            self.__rfr
        )
        

    def __set_spreadsheet(self):

        self.__spreadsheet = SpreadSheet(
            self.__master_df_s,
            self.__trade_history_s.df,
            self.__performance_measurement,
            self.__drawdown,
            self.__start_capital,
            self.__comission,
            self.__periodicity)

    def __get_data_df(self, symbol, start_date, end_date, source):

        if source == 'Yahoo Finance':
            master = yf.Ticker(symbol[0])
            master_df = master.history(start_date, end_date)

        elif source == 'Source Folder':
            csvDP = CSVDataPreparer(csv_symbols=symbol)
            master_df = csvDP.get_assets_historic_data(
                start_date, end_date, symbol)

        return master_df
