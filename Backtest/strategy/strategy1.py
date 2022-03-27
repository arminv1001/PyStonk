import sys
from data_prep.CSVDataPreparer import *
from equity.Equity import *
from statistics.SpreadSheet import *
from viewer.BacktestViewer import *
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
    
def run_strategy(master_df):
    """
    Simple function running Moving Average Strategy

    Args:
        master_df (pd Dataframe): master_df

    Returns:
        pd Dataframe: master_df with Signals and Position
    """
    
    master_df['20_SMA'] = master_df['Close'].rolling(window=20, min_periods=1).mean()
    master_df['50_SMA'] = master_df['Close'].rolling(window=50, min_periods=1).mean()
    master_df['Signal'] = 0
    master_df['Signal'] = np.where(master_df['20_SMA'] > master_df['50_SMA'], 1, 0)
    master_df['Position'] = master_df['Signal'].diff().fillna(0)
    columns = ['50_SMA', '20_SMA']
    # Moving Average Crossover Strategy
    plt.figure(figsize=(20,5))
    #plt.plot(master_df.index, master_df[symbol], color="#425af5")
    #plt.plot(master_df.index, master_df['50_SMA'], color= "#f5b042")
    #plt.plot(master_df.index, master_df['20_SMA'], color= "#f5ef42")
    master_df['Short_Signal'] = master_df['Close'][master_df['Position'] == -1]
    master_df['Long_Signal'] = master_df['Close'][master_df['Position'] == 1]
    #master_df = master_df.rename(columns={symbol[0]:"Close"})


    return master_df