from itertools import groupby
import numpy as np
import pandas as pd

PERIODS = {
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}


def get_bars_held_of(self, dates_of):
    """
        Returns numbers of bars held of specific case

        Returns:
            np.array: array of numbers of bars
        """
     _, short_dates = self.get_long_short_dates()

      specific_bars_held = []
       for date in dates_of:
            short_idx = short_dates.index(date)
            specific_bars_held.append(bars_held[short_idx])

        return np.array(specific_bars_held)


def get_weeknd(start_date, end_date, excluded=(6, 7)):
     """
        Returns weeknd days within time period

        Args:
            start_date (Timestamp): start date
            end_date (Timestamp): end date
            excluded (int, optional): numbers for weeknd days. Defaults to (6, 7).

        Returns:
            list: list with dates of weeknd days
        """
      weeknd_days = []
       while d.date() <= end.date():
            if d.isoweekday() in excluded:
                days.append(d)
            d += datetime.timedelta(days=1)
        return weeknd_days

def clear_weeknds(self, long_dates, short_dates):
        num_of_weeknd_list = self.get_number_of_weeknds(long_dates, short_dates)
        bars_held = short_dates - long_dates

        for i in range(0, len(bars_held)):
            bars_held[i] = bars_held[i] - num_of_weeknd_list[i]

        return np.array(bars_held)

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

def calculate_drawdowns(equity, type):
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
        hwm[t] = max(hwm[t-1], equity.iloc[t])
    
    hwm_tmp = list(set(hwm))
    
    hwm_dates = [equity[equity == mark].index[0] for mark in hwm_tmp]
    hwm_dates.sort()
    dd_durations = []

    for i in range(len(hwm_dates)):
        
        if i < len(hwm_dates)-1:
            dd_durations.append(hwm_dates[i+1]-hwm_dates[i])
    
    dd_max_duration = max(dd_durations)
    
    
    # Get dates of whm
    
    # Calculate drawdown, max. drawdown, max. drawdown duration
    performance = pd.DataFrame(index=equity.index)
    performance["Drawdown"] = (hwm - equity) / hwm
    performance["Drawdown"].iloc[0] = 0.0


    return performance["Drawdown"], np.max(performance["Drawdown"]), # duration


        
    

