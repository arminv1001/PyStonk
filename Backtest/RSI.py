import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import ta
from tqdm import tqdm
from scipy.optimize import minimize
from hurst import compute_Hc
import warnings
warnings.filterwarnings("ignore")

def RSI(close, neutral=5, window=14):
    """ 
            ------------------------------------------------------------------------------
            | Output: The function gives the returns of RSI strategy                     |
            ------------------------------------------------------------------------------
            | Inputs: -signal_df (type dataframe pandas): Entry signal_dfues of the stock            |
            |         -neutral (float): signal_dfue of neutrality, i.e. no action zone         |
            |         -window (float): rolling period for RSI                            |
            ------------------------------------------------------------------------------
    """
    signal_df = pd.DataFrame(close)
    signal_df['rsi'] = ta.momentum.RSIIndicator(close, window=window).rsi()

    overbuy = 70
    neutral_buy = 50 + neutral

    signal_df['rsi_yesterday'] = signal_df['rsi'].shift(1)
    signal_df['signal_long'] = np.nan



    # We need define the Open Long signal (RSI yersteday<55 and RSI today>55)
    signal_df.loc[(signal_df["rsi"] > neutral_buy) & (
        signal_df["rsi_yesterday"] < neutral_buy), "signal_long"] = 1

    # We need define the Close Long signal (RSI yersteday>55 and RSI today<55) False signal
    signal_df.loc[(signal_df["rsi"] < neutral_buy) & (
        signal_df["rsi_yesterday"] > neutral_buy), "signal_long"] = 0

    # We need define the Close Long signal (RSI yersteday>70 and RSI today<70) Over buy signal
    signal_df.loc[(signal_df["rsi"] < overbuy) & (
        signal_df["rsi_yesterday"] > overbuy), "signal_long"] = 0


   
