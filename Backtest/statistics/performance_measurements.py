import numpy as np
import pandas as pd

PERIODS = {
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}


def aggregate_returns(returns, convert_to):
    """
    Aggregates returns Daily, Weekly, Monthly or Yearly.

    Args:
        returns (pd Series): return of strategy
        convert_to (string): desired timeframe to be converted to
    """
    def cumulate_returns(x):
        return np.exp(np.log(1 + x).cumsum())[-1] - 1

    if convert_to == 'weekly':
        return returns.groupby(
            [lambda x: x.year,
             lambda x: x.month,
             lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == 'monthly':
        return returns.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == 'yearly':
        return returns.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError('convert_to must be weekly, monthly or yearly')


def create_cagr(equity, periods="Daily"):
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
    years = len(equity) / float(periods)
    return (equity[-1] ** (1.0 / years)) - 1.0

def calculate_sharpe_ratio(returns, timeframe="Daily"):
    """
    Calculates the Sharpe Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

    Args:
        returns (pd Series): return of strategy
        timeframe (str, optional): desired trading periods. Defaults to "Daily".

    Returns:
        float: Sharpe Ration
    """
    periods = PERIODS[timeframe]
    return np.sqrt(periods) * (np.mean(returns)/np.std(returns))

def calculate_sortino_ratio(returns, timeframe="Daily"):
    """
    Calculates the Sortino Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

    Args:
        returns (pd Series): return of strategy
        timeframe (str, optional): desired trading periods. Defaults to "Daily".

    Returns:
        float: Sortino Ration
    """
    periods = PERIODS[timeframe]
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns[returns < 0])

def calculate_equity(returns):
    """
    Calculates the equity (cumulative profit-loss curve)

    Args:
        returns (pd Series): return of strategy

    Returns:
        pd Series: equity
    """

    return returns.cumsum()

def calculate_drawdowns(equity):
    """
    Calculates drawdowns of the equity curve & drawdown duration.

    Args:
        equity (pd Series): cumulative profit-loss curve

    Returns:
        pd DataFrame: drawdown, 
    """
    hwm = np.zeros(len(equity.index)) # high water marks (global maximum)
    # Get high water marks
    for t in range(1, len(equity.index)):
        hwm[t] = max(hwm[t-1], returns.iloc[t])
    
    # Calculate drawdown, max. drawdown, max. drawdown duration
    performance = pd.DataFrame(index=returns.idx)
    performance["Drawdown"] = (hwm - returns) / hwm
    performance["Drawdown"].iloc[0] = 0.0
    performance["DrawdownDuration"] = np.where(
        performance["Drawdown"] == 0, 0, 1)
    duration = max(
        sum(1 for i in g if i == 1)
        for k, g in groupby(performance["DurationCheck"])
    )
    return performance["Drawdown"], np.max(performance["Drawdown"]), duration


    

