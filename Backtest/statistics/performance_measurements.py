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


class PerformanceMeasurement(object):
    """
    PerformanceMeasurement contains all relevant performance ratios of strategy

    """

    def __init__(self, equity_df, trade_history_s, trade_history_b, periodicity, rfr):

        self.__equity_df = equity_df
        self.__trade_history_s = trade_history_s
        self.__trade_history_b = trade_history_b
        self.__return_s = self.__trade_history_s['Return %'].to_numpy()
        self.__return_b = self.__trade_history_b['Return %'].to_numpy()
        self.__periodicity = periodicity
        self.__rfr = rfr # risk-free rate

    def calculate_sharpe_ratio(self, period="Annually"):
        """
        Calculates the Sharpe Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

        Args:
            returns (pd Series): return of strategy
            timeframe (str, optional): desired trading periods. Defaults to "Annually".

        Returns:
            float: Sharpe Ratio
        """
        periods = PERIODS[period]

        return_s, return_b, excess_list = get_equal_len_list(
            self.__return_s, self.__return_b)
        
        d = return_s - return_b

        return np.sqrt(periods) * ((np.mean(d)) / np.std(return_s))

    def calculate_sortino_ratio(self, period="Annually"):
        """
        Calculates the Sortino Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

        Args:
            returns (pd Series): return of strategy
            timeframe (str, optional): desired trading periods. Defaults to "Annually".

        Returns:
            float: Sortino Ratio
        """

        periods = PERIODS[period]
        
        return_s, return_b, excess_list = get_equal_len_list(
            self.__return_s, self.__return_b)

        d = return_s - return_b

        rfr = 0  # risk-free rate

        return np.sqrt(periods) * ((np.mean(d)) / np.std(return_s[return_s < 0]))

    def calculate_mm_ratio(self, period="Annually"):
        """
        Calculates the Modigliani and Modigliani Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

        Args:
            returns (pd Series): return of strategy
            timeframe (str, optional): desired trading periods. Defaults to "Annually".

        Returns:
            float: Modigliani and Modigliani Ratio
        """

        periods = PERIODS[period]

        return_s, return_b, excess_list = get_equal_len_list(
            self.__return_s, self.__return_b)

        d_s = np.mean(return_s) - self.__rfr
        d_b = np.mean(return_b) - self.__rfr
        fraq = np.std(return_s) / np.std(return_b)

        rap = np.sqrt(periods) * fraq * d_s + self.__rfr
        rm = np.sqrt(periods) * fraq * d_b + self.__rfr

        return rap, rm

    def calculate_sterling_ratio(self, sorted_dd, N=10, period="Annually"):
        """
        Calculates the Sterling Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

        Args:
            returns (pd Series): return of strategy
            timeframe (str, optional): desired trading periods. Defaults to "Annually".

        Returns:
            float: Sterling Ratio
        """

        periods = PERIODS[period]

        denominator = np.mean(np.negative(sorted_dd[:N]))

        return np.sqrt(periods) * ((np.mean(self.__return_s) -
                                    self.__rfr) / denominator)

    def calculate_burke_ratio(self, sorted_dd, N=10, period="Annually"):
        """
        Calculates the Burke Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

        Args:
            sorted_dd (pd Series): sorted drawdowns
            n (int): number of max. drawdowns
            timeframe (str, optional): desired trading periods. Defaults to "Annually".

        Returns:
            float: Burke Ratio
        """

        periods = PERIODS[period]

        denominator = np.mean(np.square(np.negative(sorted_dd[:N])))

        return np.sqrt(periods) * ((np.mean(self.__return_s) -
                                    self.__rfr) / denominator)

    def calculate_mar_ratio(self, cagr, max_dd):
        """
        Calculates the MAR Ratio of the strategy.

        Args:
            cagr (float): compound annual growth rate %
            max_dd (float): maximum drawdown in % 

        Returns:
            float: MAR Ratio
        """
        return cagr/max_dd

    def calculate_calmar_ratio(self, max_dd, period="Annually"):
        """
        Calculates the Calmar Ratio of the strategy.

        Args:
            max_dd (float): maximum drawdown in % 

        Returns:
            float: Calmar Ratio
        """
        periods = PERIODS[period]
        return np.sqrt(periods) * ((np.mean(self.__return_s) -
                                    self.__rfr) / max_dd)

    def calculate_cagr(self, period="Daily"):
        """
        Calculates the Compound Annual Growth Rate (CAGR)
        for the portfolio, by determining the number of years
        and then creating a compound annualised rate based
        on the total return.

        Returns:
            float: CAGR
        """
        periods = PERIODS[period]
        equity = self.__equity_df['Equity %']
        years = len(equity) / float(periods)
        return ((equity[-1]/equity[1]) ** (1.0 / years)) - 1.0 

    def calculate_beta_alpha(self):
        """
        Calculates the Beta & Alpha of the strategy

        Returns:
            float: alpha, beta
        """

        return_s, return_b, excess_list = get_equal_len_list(
            self.__return_s, self.__return_b)

        numerator = np.cov(return_s.astype(
            float), return_b.astype(float))
        denumerator = np.var(return_b)
        beta = numerator[0][0] / denumerator
        alpha = return_s.mean() - beta * return_b.mean()
        return beta, alpha

    def calculate_hhi(self, returns):
        """
        Calculates the Herfindahl-Hirschman Index of the strategy

        Args:
            returns (pd Series): returns of trades

        Returns:
            float: Herfindahl-Hirschman Index
        """
        
        weight = returns/returns.sum()
        w_sum_p2 = (weight**2).sum()
        return (w_sum_p2 - len(returns)**-1)/(1-len(returns)**-1)








    


