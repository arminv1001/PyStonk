import numpy as np
import pandas as pd

PERIODS = {
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}

class SpreadSheet(object):

    def __init__(self, df, complete_capital, quantity, comission, time_period):
        self.__master_df = df
        # self.benchmark_df = benchmark
        self.__complete_capital = complete_capital
        self.__quantity = quantity
        self.__comission = comission

        self.__time_period = time_period

        self.__general_info = self.create_general_info()
        self.__performance_info = self.create_performance_info()
        self.__all_trades_info = self.create_all_trades()
        self.__position_history = self.create_position_history_df()
        self.__winners = self.create_winners()
        self.__losers = self.create_losers()
        self.__drawdowns = self.create_drawdowns()
    
    @property
    def general_info(self):
        return self.__general_info

    @property
    def performance_info(self):
        return self.__performance_info
    
    @property
    def all_trades_info(self):
        return self.__all_trades_info

    @property
    def position_history(self):
        return self.__position_history

    @property
    def winners(self):
        return self.__winners

    @property
    def losers(self):
        return self.__losers

    @property
    def drawdowns(self):
        return self.__drawdowns

    def create_general_info(self):
        """
        Return DataFrame with general information: Initial Capital, Ending Capital, Net Profit, Net Profit %, Initial Capital, Exposure, Annual Returns %, Transaction Costs

        Returns:
            pd.DataFrame: General Information DataFrame
        """
        general_info = pd.DataFrame(index = self.__master_df.index)
        general_info['Initial Capital'] = self.__master_df['Capital'][0]
        general_info['Ending Capital'] = self.__master_df['Capital'][-1]
        general_info['Net Profit'] = self.__master_df['Capital'][-1]- \
            self.__master_df['Capital'][0]
        general_info['Net Profit %'] = general_info['Net Profit'] / \
            general_info['Initial Capital']
        general_info['Exposure'] = general_info['Initial Capital'] / \
            self.__complete_capital
        general_info['Annual Returns %'] = self.create_cagr(self.__master_df['Equity'])
        general_info['Transaction Costs'] = len(
            self.__master_df[self.__master_df['Position'] != 0]) * self.__quantity * self.__comission
        
        return general_info


    def create_performance_info(self):
        """
        Returns DataFrame with performance measurements: Sharpe Ratio, Sortino Ratio, Alpha, Beta

        Returns:
            pd.DataFrame: Performance measurements DataFrame
        """
        performance_info = pd.DataFrame(index=self.__master_df.index)
        performance_info['Sharpe Ratio'] = self.calculate_sharpe_ratio(self.__master_df['Return'])
        performance_info['Sortino Ratio'] = self.calculate_sortino_ratio(self.__master_df['Return'])
        beta, alpha = self.calculate_beta_alpha(
            self.__master_df['Return'], self.__master_df['Return'])
        performance_info['Alpha'] = alpha
        performance_info['Beta'] = beta

        return performance_info
    
    def create_all_trades(self):
        """
        Returns DataFrame with info regarding all trades

        Returns:
            pd.DataFrame: Info regarding all trades DataFrame
        """
        all_trades_info = pd.DataFrame(index=self.__master_df.index)
        all_trades_info['Avg. Return'] = self.__master_df['Return'].mean()
        all_trades_info['Avg. Return %'] = self.__master_df['Return %'].mean()
        all_trades_info['Avg. Bars held'] = round(self.get_bars_held().mean())

        return all_trades_info
        
    def create_position_history_df(self):
        """
        Retuns DataFrame with history of position: Start Date, End Date, Return, Return %, Bars Held

        Returns:
            pd.DataFrame: History all positions DataFrame
        """
        long_dates, short_dates, _ = self.get_long_short_dates()
        pnl = self.__master_df.loc[short_dates[0], 'Return'].tolist()
        pnl_pct = self.__master_df.loc[short_dates[0], 'Return %'].tolist()
        bars_held = self.get_bars_held()

        data = {
            'Start Date': pd.Series(long_dates[0]).tolist(),
            'End Date': pd.Series(short_dates[0]).tolist(),
            'Return': pnl,
            'Return %': pnl_pct,
            'Bars Held': bars_held
            }

        return pd.DataFrame.from_dict(data, orient='index').transpose()

    def create_winners(self):
        """
        Retuns DataFrame with infos about winning trades: Total Profit, Avg. Profit, Avg, Bars Held, Max. Consecutive, Largest Win, Bars in Largest Win

        Returns:
            pd.DataFrame: Infos about winning trades DataFrame
        """
        winners = pd.DataFrame(index=self.__master_df.index)
        winners['Total Profit'] = self.__position_history['Return'][self.__position_history['Return'] > 0].sum()
        winners['Avg. Profit'] = self.__position_history['Return'][self.__position_history['Return'] > 0].mean()
        winner_bars = self.__position_history['Bars Held'][self.__position_history['Return'] > 0]
        winners['Avg. Bars Held'] = float('NaN') if winner_bars.empty else int(winner_bars.mean())
        winners['Max. Consecutive'] = self.get_consecutive()
        winners['Largest Win'] = self.__position_history['Return'][self.__position_history['Return'] > 0].max()
        winners['Bars in Largest Win'] = self.__position_history['Bars Held'][self.__position_history['Bars Held']
                                                                              == winners['Largest Win'][0]]

        return winners

    def create_losers(self):
        """
        Retuns DataFrame with infos about losing trades: Total Loss, Avg. Loss, Avg, Bars Held, Max. Consecutive, Largest Loss, Bars in Largest Loss

        Returns:
            pd.DataFrame: History all positions DataFrame
        """
        losers = pd.DataFrame(index=self.__master_df.index)
        print('hierho')
        print(self.__position_history['Return']
              [self.__position_history['Return'] < 0])
        losers['Total Loss'] = self.__position_history['Return'][self.__position_history['Return'] < 0].sum()
        losers['Avg. Loss'] = self.__position_history['Return'][self.__position_history['Return'] < 0].mean()
        loser_bars = self.__position_history['Bars Held'][self.__position_history['Return'] < 0]
        losers['Avg. Bars Held'] = float('NaN') if loser_bars.empty else int(loser_bars.mean())
        losers['Max. Consecutive'] = self.get_consecutive()
        losers['Largest Loss'] = self.__position_history['Return'][self.__position_history['Return'] < 0].max()
        losers['Bars in Largest Loss'] = self.__position_history['Bars Held'][self.__position_history['Bars Held'] == losers['Largest Loss'][0]]

        return losers

    def create_drawdowns(self):
        """
        Return DataFrame with infos about drawdown: Max. Trade Drawdown, Max. Trade % Drawdown

        Returns:
            [type]: [description]
        """
        
        drawdowns = pd.DataFrame(index=self.__master_df.index)
        drawdowns['Max. Trade Drawdown'], max_dd_duration = self.calculate_drawdowns(
            self.__master_df['Equity'])
        drawdowns['Max. Trade % Drawdown'], _ = self.calculate_drawdowns(
            self.__master_df['Equity'])
        drawdowns['Max. Trade Drawdown Duration'] = max_dd_duration
        #self.drawdowns['Max. System Drawdown']
        #self.drawdowns['Max. System % Drawdown']

        return drawdowns


    def get_bars_held(self):
        """
        Returns bars held

        Returns:
            np.array: bars held
        """

        long_dates, short_dates, _ = self.get_long_short_dates()
        bars_held = []

        for i in range(0, len(long_dates[0])):
            
            long_index = self.__master_df.index.get_loc(long_dates[0][i])
            short_index = self.__master_df.index.get_loc(short_dates[0][i])
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
        for ret in self.__position_history['Return']:
            
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
        
    def get_long_short_dates(self):
        """
        Return list of long, short dates and of excess dates

        Returns:
            list: [description]
        """
        long_dates = self.__master_df[self.__master_df['Position'] == 1].index
        short_dates = self.__master_df[self.__master_df['Position'] == -1].index

        long_dates_list = []
        short_dates_list = []
        excess_dates = []

        # clear excess dates
        if len(short_dates) < len(long_dates):
            excess = len(long_dates) - len(short_dates)
            long_dates_list = self.delete_list_by_index(long_dates, excess)
            excess_dates = [long_dates] - long_dates_list
        elif len(long_dates) < len(short_dates):
            excess = len(short_dates) - len(long_dates)
            short_dates_list = self.delete_list_by_index(short_dates, excess)
            excess_dates = [short_dates] - short_dates_list
        else:
            long_dates_list = [long_dates]
            short_dates_list = [short_dates]

        return long_dates_list, short_dates_list, excess_dates

    def delete_list_by_index(self, del_list, excess):
        """
        Deletes last excess entries of list

        Args:
            del_list (np.array): list to be shorten
            excess (float): excess entries

        Returns:
            list: excess cleared list
        """
        end = len(del_list)
        start = end - excess
        array = np.array(data)
        index = [i for i in range(start, end)]
        
        return list(np.delete(array,index))

    def calculate_drawdowns(self, equity):
        """
        Calculates drawdowns of the equity curve & drawdown duration.

        Args:
            equity (pd Series): cumulative profit-loss curve

        Returns:
            pd DataFrame, float: drawdown, max. drawdown
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
        # performance = pd.DataFrame(index=equity.index)
        drawdown = (hwm - equity) / hwm
        drawdown[0] = 0.0

        return drawdown, dd_max_duration

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

    def calculate_beta_alpha(self, returns_df, benchmark_df):
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
        numerator = np.cov(returns, benchmark)
        denumerator = np.var(benchmark)
        beta = numerator[0][0] / denumerator
        alpha = returns.mean() - beta * benchmark.mean()
        return beta, alpha

    def calculate_sortino_ratio(self, returns_df, timeframe="Daily"):
        """
        Calculates the Sortino Ratio of the strategy (based on a benchmark with neglectable risk-free rate).

        Args:
            returns (pd Series): return of strategy
            timeframe (str, optional): desired trading periods. Defaults to "Daily".

        Returns:
            float: Sortino Ration
        """
        returns = returns_df.to_numpy()
        periods = PERIODS[timeframe]

        return np.sqrt(periods) * (np.mean(returns)) / np.std(returns[returns < 0])

    
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
        for i in range(0,len(long_dates)):
            num_weeknds.append(len(self.get_weeknd(long_dates[i], short_days[i])))
        
        return num_weeknds
            


    

    
    
