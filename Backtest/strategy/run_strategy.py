import sys
from equity.Equity import *
from statistics.spreadsheet import *
from viewer.BacktestViewer import *

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
import pandas as pd
import os

sys.path.append('.')
from TradingSystems.Strategy1 import Strategy1
from TradingSystems.ml_stra import ml_strat_reg
from TradingSystems.ml_strat_reg_kla import ml_strat_reg_kla

CSV_DIR = os.path.join(os.path.abspath(os.curdir), "Backtest/backtest_data")

def run_strategy(strategy, symbols, data_source, parameter) -> pd.DataFrame:
    """
    Runs demanded strategy with given information

    Args:
        strategy (str): strategy
        symbols (str): symbol
        data_source (str): data source
        parameter (float): parameter of strategy

    Returns:
        pd.DataFrame: _description_
    """

    # general strategy settings
    if data_source.startswith('.'): # data source is a file e.g. ".csv"
        filename = symbols + data_source
        path = os.path.join(CSV_DIR, filename)

    symbolsNames = []
    alternativDataName = [[path, data_source]]
    systemName = strategy
    systemType = 'TradingSystem'
    systemStyle = 1
    broker = None
    timeFrame = ''

    # create Trading System object
    if strategy == 'Moving_Average':
        ma_strategy = Strategy1(
            symbolsNames, alternativDataName, systemName, systemType, systemStyle, broker, timeFrame)
        ma_strategy.createSignal(parameter)
        signal_df = ma_strategy.getSignalDf()

    elif strategy == 'ML_reg_Bitcoin':
        ml_strat_reg_model = ml_strat_reg(
            symbolsNames, alternativDataName, systemName, systemType, systemStyle, broker, timeFrame)
        ml_strat_reg_model.createSignal()
        signal_df = ml_strat_reg_model.getSignalDf()
    
    elif strategy == 'ML_class_reg_Bitcoin':
        ml_strat_reg_model = ml_strat_reg_kla(
            symbolsNames, alternativDataName, systemName, systemType, systemStyle, broker, timeFrame)
        ml_strat_reg_model.createSignal()
        signal_df = ml_strat_reg_model.getSignalDf()

    return signal_df

