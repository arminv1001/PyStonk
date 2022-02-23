import sys
sys.path.insert(0, '/Users/mr.kjn/Projects/PyStonk/Backtest/data_prep')
from CSVDataPreparer import *
from RSI import *
from equity.Equity import *
from statistics.SpreadSheet import *
from viewer.BacktestViewer import *
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
    
def run_strategy(symbol, start_date, end_date):
    csv_dir = '/Users/mr.kjn/Projects/PyStonk/Backtest/backtest_data'
    csvDP = CSVDataPreparer(csv_dir=csv_dir, csv_symbols=symbol)
    closes = csvDP.get_assets_historic_data(start_date, end_date, symbol)
    closes['20_SMA'] = closes['Close'].rolling(window=20, min_periods=1).mean()
    closes['50_SMA'] = closes['Close'].rolling(window=50, min_periods=1).mean()
    closes['Signal'] = 0
    closes['Signal'] = np.where(closes['20_SMA'] > closes['50_SMA'], 1, 0)
    closes['Position'] = closes['Signal'].diff().fillna(0)
    columns = ['50_SMA', '20_SMA']
    # Moving Average Crossover Strategy
    plt.figure(figsize=(20,5))
    #plt.plot(closes.index, closes[symbol], color="#425af5")
    #plt.plot(closes.index, closes['50_SMA'], color= "#f5b042")
    #plt.plot(closes.index, closes['20_SMA'], color= "#f5ef42")
    closes['Short_Signal'] = closes['Close'][closes['Position'] == -1]
    closes['Long_Signal'] = closes['Close'][closes['Position'] == 1]
    closes = closes.rename(columns={symbol[0]:"Close"})


    return closes