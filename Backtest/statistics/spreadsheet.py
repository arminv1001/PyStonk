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
        self.complete_capital g
        self.quantity
        self.comission = comission

        self.time_period = time_period

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
        self.all_trades_info['Avg. Return'] = self.master_df['Return'].mean()
        self.all_trades_info['Avg. Return %'] = self.master_df['Return %'].mean()
        self.all_trades_info['Avg. Bars held'] = self.get_bars_held().mean()
        
    def create_trade_history_df(self):
        long_dates, short_dates, _ = self.get_long_short_dates()
        pnl = self.master_df.loc[short_dates, 'Return']
        pnl_pct = self.master_df.loc[short_dates, 'Return %']
        bars_held = self.get_bars_held()
        data = {
            'Start Date': long_dates, 
            'End Date': short_dates, 
            'Return': pnl,
            'Return %': pnl_pct,
            'Bars Held': bars_held
            }
        self.trade_history = pd.DataFrame(data=data)

    def create_winners(self):
        self.winners['Total Profit'] = self.trade_history['Return'][self.master.df['Return'] > 0].sum()
        self.winners['Avg. Profit'] = self.trade_history['Return'][self.master.df['Return'] > 0].mean()
        winner_bars = self.trade_history['Bars'][self.master.df['Return'] > 0].mean()
        self.winners['Avg. Bars Held'] = self.trade_history['Bars'][self.master.df['Return'] > 0].mean()
        self.winners['Max. Consecutive'] = self.get_consecutive()
        self.winners['Largest Win'] = self.trade_history['Return'][self.master.df['Return'] > 0].max()
        self.winners['Bars in Largest Win'] = self.trade_history['Bars'][self.winners['Largest Win']]

    def create_losers(self):
        self.losers['Total Loss'] = self.trade_history['Return'][self.master.df['Return'] < 0].sum()
        self.losers['Avg. Loss'] = self.trade_history['Return'][self.master.df['Return'] < 0].mean()
        loser_bars = self.trade_history['Bars'][self.master.df['Return'] < 0].mean()
        self.losers['Avg. Bars Held'] = self.trade_history['Bars'][self.master.df['Return'] < 0].mean()
        self.losers['Max. Consecutive'] = self.get_consecutive()
        self.losers['Largest Loss'] = self.trade_history['Return'][self.master.df['Return'] < 0].max()
        self.losers['Bars in Largest Win'] = self.trade_history['Bars'][self.losers['Largest Win']]

    def create_drawdowns(self):
        self.drawdowns['Max. Trade Drawdown']
        self.drawdowns['Max. Trade % Drawdown']
        self.drawdowns['Max. System Drawdown']
        self.drawdowns['Max. System % Drawdown']


    def get_bars_held(self, long_dates, short_dates periods='Daily'):
        """
        Returns the bars held

        Returns:
            np.array : bars held

        TO-DO:
            Bars nicht nur in days time period -> welche
        """

        long_dates, short_dates, _ = self.get_long_short_dates()
        bars_held = []

        i in range(0, len(long_dates)):
            long_index = self.master_df.get_loc(long_dates[i])
            short_index = self.master_df.get_loc(long_dates[i])
            bars = short_index - long_index
            bars_held.append(bars)


        return np.array(bars_held)
    
    def get_consecutive(self, of_wins=True):
        """
        Returns the value of the longest consecutive of winners/losers

        Args:
            of_wins (bool, optional): winners or losers. Defaults to True.

        Returns:
            float: consecutive
        """

        consecutive = 0
        longest_run = 0
        for return in self.trade_history['Return']:
            
            if of_wins:
                if return > 0:
                    consecutive = consecutive + 1
                else:
                    consecutive = 0
                    if consecutive > longest_run:
                        longest_run = consecutive
            else:
                if return < 0:
                    consecutive = consecutive + 1
                else:
                    consecutive = 0
                    if consecutive > longest_run:
                        longest_run = consecutive

        return longest_run



    def get_bars_held_of(self, dates_of)
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



    def clear_weeknds(self, long_dates, short_dates):
        num_of_weeknd_list = self.get_number_of_weeknds(long_dates, short_dates)
        bars_held = short_dates - long_dates

        for i in range(0, len(bars_held)):
            bars_held[i] = bars_held[i] - num_of_weeknd_list[i]

        return np.array(bars_held)
        
    def get_long_short_dates(self):
        """
        Return list of long, short dates and of excess dates

        Returns:
            list: [description]
        """
        short_dates = self.master_df[self.master_df['Position'] == -1].index
        long_dates = self.master_df[self.master_df['Position'] == 1].index

        # clear excess dates
        if len(short_dates) < len(long_dates):
            excess = len(long_dates) - len(short_dates)
            long_dates_list = self.delete_list_by_index(long_dates, excess)
            excess_dates = [long_dates] - long_dates_list
        elif len(long_dates) < len(short_dates):
            excess = len(short_dates) - len(long_dates)
            short_dates_list = self.delete_list_by_index(short_dates, excess)
            excess_dates = [short_dates] - short_dates_list

        return long_dates_list, short_dates_list, excess_dates

      

    def delete_list_by_index(self, del_list, excess):
        end = len(del_list)
        start = end - excess
        array = np.array(data)
        index = [i for i in range(start, end)]
        
        return list(np.delete(array,index))
    
    def get_number_of_weeknds(self, long_dates, short_dates):
        """
        Returns list with number of weeknds per time period

        Args:
            long_dates (pandas.core.indexes.datetimes.DatetimeIndex): Long Dates
            short_dates (pandas.core.indexes.datetimes.DatetimeIndex): Short Dates

        Returns:
            list: list with number of weeknds per time period
        """
        num_weeknds = []
        for i in range(0,len(long_dates):
            num_weeknds.append(len(self.get_weeknd(long_dates[i], short_days[i])))
        
        return num_weeknds
            


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
