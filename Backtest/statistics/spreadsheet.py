import numpy as np
import pandas as pd

PERIODS = {
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}

class SpreadSheet(object):

    def __init__(self, df):
        self.master_df = df
        self.benchmark_df = benchmark
        self.complete_capital
        self.quantity
        self.comission = comission

        self.general_info = {}
        self.create_general_info()
        self.performance_info = {}
        self.create_performance_info()
        self.all_trades_info = {}
        self.create_all_trades()

    def create_general_info(self):
        self.general_info['Inital Capital'] = self.master_df['Capital'][0]
        self.general_info['Ending Capital'] = self.master_df['Capital'][-1]
        self.general_info['Net Profit'] = self.master_df['Capital'][0] - \
            self.master_df['Capital'][-1]
        self.general_info['Net Profit %'] = self.general_info['Net Profit'] / \
            general_info['Inital Capital']
        self.general_info['Exposure'] = self.general_info['Initial Capital'] / \
            self.complete_capital
        self.general_info['Annual Returns %'] = self.create_cagr(self.master_df['Equity'])
        self.general_info['Transaction Costs'] = len(
            self.master_df[self.master_df['Position'] != 0]) * self.quantity * self.comission

    def create_performance_info(self):
        self.performance_info['Sharpe Ratio'] = self.calculate_sharpe_ratio(self.master_df['Return'])
        self.performance_info['Sortino Ratio'] = self.calculate_sortino_ratio(self.master_df['Return'])
        beta, alpha = self.calculate_beta_alpha(self.master_df['Return'])
        self.performance_info['Alpha'] = alpha
        self.performance_info['Beta'] = beta
    
    def create_all_trades(self):
        self.all_trades_info['Avg Return'] = self.master_df['Return'].mean()
        self.all_trades_info['Avg Return %'] = self.master_df['Return %'].mean()


    def create_cagr(self, equity, periods="Daily"):
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

    def calculate_sharpe_ratio(self, returns, timeframe="Daily"):
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

    def calculate_beta_alpha(self, returns, benchmark):
        beta = np.cov(returns, benchmark) / np.var(returns, benchmark)
        alpha = returns.mean() - beta * benchmark.mean()
        return beta, alpha



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
        hwm = np.zeros(len(equity.index))  # high water marks (global maximum)

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

        # duration
        return performance["Drawdown"], np.max(performance["Drawdown"]), dd_max_duration
