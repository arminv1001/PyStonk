import numpy as np
import pandas as pd
from tools.toolbox import *

PERIODS = {
    "Annually": 12,
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}

MAX_DD_D_PERIOD = np.power(60, 2)*24


def get_drawdowns(master_df):
    """
    Return DataFrame with infos about drawdown: Max. Trade Drawdown, Max. Trade % Drawdown

    Returns:
        pd.Dataframe: master_df
    """

    drawdowns_array, max_dd_duration = calculate_drawdowns(master_df['Equity'])
    drawdowns_array_pct, _ = calculate_drawdowns(master_df['Equity %'])
    drawdowns = pd.DataFrame(data=drawdowns_array,
                                index=master_df.index)

    drawdowns['Drawdown %'] = drawdowns_array_pct
    drawdowns = drawdowns.rename(columns={'Equity': 'Drawdown'})
    return drawdowns, max_dd_duration
    
def get_consecutive(trade_history, of_wins=True):
    """
    Returns the value of the longest consecutive of winners/losers

    Args:

        of_wins (bool, optional): winners or losers. Defaults to True.

    Returns:
        float: consecutive
    """

    consecutive = 0
    longest_run = 0
    for ret in trade_history:
        
        if of_wins:
            if ret > 0:
                consecutive = consecutive + 1
            else:
                consecutive = 0
                if consecutive > longest_run:
                    longest_run = consecutive
        else:
            if ret < 0:
                consecutive = consecutive + 1
            else:
                consecutive = 0
                if consecutive > longest_run:
                    longest_run = consecutive

    return longest_run
    

def calculate_drawdowns(equity):
    """
    Calculates drawdowns of the equity curve & drawdown duration.

    Args:
        equity (pd Series): cumulative profit-loss curve

    Returns:
        pd DataFrame, float: drawdown, max. drawdown
    """

    hwm = np.zeros(len(equity.index))  # high water marks (global maximum)
    # Get high water marks
    for t in range(0, len(equity.index)):
        hwm[t] = max(hwm[t-1], equity.iloc[t])
    hwm_tmp = list(set(hwm)) # clear redundancy
    hwm_dates = [equity[equity == mark].index[0] for mark in hwm_tmp]

    hwm_dates.sort()
    dd_durations = []

    for i in range(len(hwm_dates)):
        if i < len(hwm_dates)-1:
            dd_durations.append(hwm_dates[i+1]-hwm_dates[i])

    dd_max_duration = max(dd_durations)

    # Get dates of whm

    # Calculate drawdown, max. drawdown, max. drawdown duration
    # performance = pd.DataFrame(index=equity.index)

    drawdown = (hwm - equity) / hwm

    return drawdown, dd_max_duration

def calculate_sharpe_ratio(returns, timeframe=True, period="Annually"):
    """
    Calculates the Sharpe Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

    Args:
        returns (pd Series): return of strategy
        timeframe (str, optional): desired trading periods. Defaults to "Daily".

    Returns:
        float: Sharpe Ration
    """

    if timeframe:
        periods = PERIODS[period]
    else:
        periods = 1
    
    rfr = 0 # risk-free rate
    return np.sqrt(periods) * ((np.mean(returns)-rfr) / np.std(returns))

def calculate_sortino_ratio(returns, timeframe=True, period="Annually"):
    """
    Calculates the Sortino Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

    Args:
        returns (pd Series): return of strategy
        timeframe (str, optional): desired trading periods. Defaults to "Daily".

    Returns:
        float: Sortino Ration
    """
    if timeframe:
        periods = PERIODS[period]
    else:
        periods = 1

    rfr = 0  # risk-free rate

    return np.sqrt(periods) * ((np.mean(returns)-rfr) / np.std(returns[returns < 0]))

def calculate_mar_ratio(cagr, max_dd):
    """
    Calculates the MAR Ratio of the strategy.

    Args:
        cagr (float): compound annual growth rate %
        max_dd (float): maximum drawdown in % 

    Returns:
        float: MAR Ration
    """
    return cagr/max_dd

def calculate_calmar_ratio(rp, max_dd):
    """
    Calculates the Calmar Ratio of the strategy.

    Args:
        rp (float): portfolio return %
        max_dd (float): maximum drawdown in % 

    Returns:
        float: Calmar Ration
    """
    return rp/max_dd

def calculate_cagr(equity, periods="Daily"):
    """
    Calculates the Compound Annual Growth Rate (CAGR)
    for the portfolio, by determining the number of years
    and then creating a compound annualised rate based
    on the total return.

    Args:
        equity (pd Series): equity curve
        periods (int, optional): desired trading periods. Defaults to "Daily".

    Returns:
        float: CAGR
    """
    periods = PERIODS[periods]
    years = len(equity) / float(periods)
    return (equity[-1] ** (1.0 / years)) - 1.0 

def calculate_beta_alpha(returns_df, benchmark_df):
    """
    Calculates the Beta & Alpha of the strategy

    Args:
        returns (pd.DataFrame): Returns
        benchmark (pd.DataFrame): compared market index or broad benchmark

    Returns:
        float: alpha, beta
    """
    returns = returns_df.to_numpy()
    benchmark = benchmark_df.to_numpy()
    numerator = np.cov(returns.astype(float), benchmark.astype(float))
    denumerator = np.var(benchmark)
    beta = numerator[0][0] / denumerator
    alpha = returns.mean() - beta * benchmark.mean()
    return beta, alpha

def get_return_of_trades(master_df, long_dates, short_dates):
    returns = []
    returns_pct = []

    for i in range(0, len(long_dates)):
        long_index = master_df.index.get_loc(long_dates[i])
        short_index = master_df.index.get_loc(short_dates[i])
        ret = master_df[short_index] - \
            master_df[long_index]
        ret_pct = ret / master_df[long_index]
        returns.append(ret)
        returns_pct.append(ret_pct)

    return returns, returns_pct


def get_bars_held(master_df):
    """
        Returns bars held

        Returns:
            np.array: bars held
        """

    long_dates, short_dates, _ = get_long_short_dates(master_df)
    bars_held = []

    for i in range(0, len(long_dates)):

        short_index = master_df.index.get_loc(short_dates[i])
        long_index = master_df.index.get_loc(long_dates[i])
        bars = short_index - long_index
        bars_held.append(bars)

    return np.array(bars_held)




    


