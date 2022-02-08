import numpy as np
import pandas as pd

PERIODS = {
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}

class SpreadSheet(object):

    def __init__(self, df, complete_capital, pos_size, comission, periodicity):
        self.__master_df = df
        # self.benchmark_df = benchmark
        self.__complete_capital = complete_capital
        self.__pos_size = pos_size # position size
        self.__comission = comission

        self.__periodicity = periodicity

        self.__general_info = self.create_general_info()
        self.__trade_history = self.create_trade_history_df()
        self.__performance_info = self.create_performance_info()
        self.__all_trades_info = self.create_all_trades()
        self.__winners = self.create_winners()
        self.__losers = self.create_losers()

        self.__drawdowns, self.__max_dd_duration = self.create_drawdowns()
        self.__drawdowns_info = self.create_drawdown_info()
    
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
    def trade_history(self):
        return self.__trade_history

    @property
    def winners(self):
        return self.__winners

    @property
    def losers(self):
        return self.__losers

    @property
    def drawdowns(self):
        return self.__drawdowns

    @property
    def max_dd_duration(self):
        return self.__max_dd_duration

    def get_info_df(self):
        """
        Returns DataFrame with all SpreadSheet Infos

        Returns:
            pd.DataFrame: SpreadSheet Infos
        """
        frames = [
            self.__general_info,
            self.__performance_info,
            self.__all_trades_info,
            self.__winners,
            self.__losers,
            self.__drawdowns_info
        ]
        print(self.__drawdowns_info)
        print(self.__drawdowns_info['Max. Drawdown Duration'])
        info_df = pd.concat(frames)
        return info_df


    def create_general_info(self):
        """
        Return DataFrame with general information: Initial Capital, Ending Capital, Net Profit, Net Profit %, Initial Capital, Exposure, Annual Returns %, Transaction Costs

        Returns:
            pd.DataFrame: General Information DataFrame
        """
        data = {
            'Initial Capital': self.__master_df['Equity'][0],
            'Ending Capital': self.__master_df['Equity'][-1],
            'Net Profit': self.__master_df['Equity'][-1] - self.__master_df['Equity'][0],
            'Net Profit %': (self.__master_df['Equity'][-1] - self.__master_df['Equity'][0]) / self.__master_df['Equity'][0],
            'Exposure': self.__master_df['Equity'][0] / self.__complete_capital,
            'Annual Returns %': self.create_cagr(self.__master_df['Equity']),
            'Transaction Costs': len(self.__master_df[self.__master_df['Position'] != 0]) * self.__pos_size * self.__comission
        }
        return pd.DataFrame.from_dict(data, orient='index')
    
    def create_trade_history_df(self):
        """
        Retuns DataFrame with history of position: Start Date, End Date, Return, Return %, Bars Held

        Returns:
            pd.DataFrame: History all positions DataFrame
        """
        long_dates, short_dates, _ = self.get_long_short_dates()
        returns, returns_pct = self.get_return_of_trades(
            long_dates, short_dates)
        bars_held = self.get_bars_held()

        data = {
            'Start Date': pd.Series(long_dates[0]).tolist(),
            'End Date': pd.Series(short_dates[0]).tolist(),
            'Return': returns,
            'Return %': returns_pct,
            'Bars Held': bars_held
        }

        return pd.DataFrame.from_dict(data, orient='index').transpose()

    def get_return_of_trades(self, long_dates, short_dates):
        returns = []
        returns_pct = []

        for i in range(0, len(long_dates[0])):
            long_index = self.__master_df.index.get_loc(long_dates[0][i])
            short_index = self.__master_df.index.get_loc(short_dates[0][i])
            ret = self.__master_df['Close'][short_index] - \
                self.__master_df['Close'][long_index]
            ret_pct = ret / self.__master_df['Close'][long_index]
            returns.append(ret)
            returns_pct.append(ret_pct)

        return returns, returns_pct


    def create_performance_info(self):
        """
        Returns DataFrame with performance measurements: Sharpe Ratio, Sortino Ratio, Alpha, Beta

        Returns:
            pd.DataFrame: Performance measurements DataFrame
        """
        sharpe = self.calculate_sharpe_ratio(self.__master_df['Profit/Loss'])
        sortino = self.calculate_sortino_ratio(self.__master_df['Profit/Loss %'])
        beta, alpha = self.calculate_beta_alpha(self.__master_df['Profit/Loss'], self.__master_df['Profit/Loss'])
        data = {
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino,
            'Alpha': alpha,
            'Beta': beta
        }

        return pd.DataFrame.from_dict(data, orient='index')
    
    def create_all_trades(self):
        """
        Returns DataFrame with info regarding all trades

        Returns:
            pd.DataFrame: Info regarding all trades DataFrame
        """
        data = {
            'Avg. Return': self.__trade_history['Return'].mean(),
            'Avg. Return %': self.__trade_history['Return %'].mean(),
            'Avg. Bars held': round(self.get_bars_held().mean())
        }

        return pd.DataFrame.from_dict(data, orient='index')

    def create_winners(self):
        """
        Retuns DataFrame with infos about winning trades: Total Profit, Avg. Profit, Avg, Bars Held, Max. Consecutive, Largest Win, Bars in Largest Win

        Returns:
            pd.DataFrame: Infos about winning trades DataFrame
        """
       
        winner_bars = self.__trade_history['Bars Held'][self.__trade_history['Return'] > 0]
        largest_win = self.__trade_history['Return'][self.__trade_history['Return'] > 0].max(
        )

        data = {
            'Total Profit': self.__trade_history['Return'][self.__trade_history['Return'] > 0].sum(),
            'Avg. Profit': self.__trade_history['Return'][self.__trade_history['Return'] > 0].mean(),
            'Avg. Bars Held': float('NaN') if winner_bars.empty else int(winner_bars.mean()),
            'Max. Consecutive': self.get_consecutive(),
            'Largest Win': largest_win,
            'Bars in Largest Win': self.__trade_history['Bars Held'][self.__trade_history['Return'] == largest_win].iloc[0]

        }

        return pd.DataFrame.from_dict(data, orient='index')

    def create_losers(self):
        """
        Retuns DataFrame with infos about losing trades: Total Loss, Avg. Loss, Avg, Bars Held, Max. Consecutive, Largest Loss, Bars in Largest Loss

        Returns:
            pd.DataFrame: History all positions DataFrame
        """
        loser_bars = self.__trade_history['Bars Held'][self.__trade_history['Return'] < 0]
        largest_loss = self.__trade_history['Return'][self.__trade_history['Return'] < 0].max(
        )
        data = {
            'Total Profit': self.__trade_history['Return'][self.__trade_history['Return'] < 0].sum(),
            'Avg. Profit': self.__trade_history['Return'][self.__trade_history['Return'] < 0].mean(),
            'Avg. Bars Held': float('NaN') if loser_bars.empty else int(loser_bars.mean()),
            'Max. Consecutive': self.get_consecutive(),
            'Largest Loss': self.__trade_history['Return'][self.__trade_history['Return'] > 0].max(),
            'Bars in Largest Loss': self.__trade_history['Bars Held'][self.__trade_history['Return'] == largest_loss].iloc[0]
        }

        return pd.DataFrame.from_dict(data, orient='index')

    def create_drawdowns(self):
        """
        Return DataFrame with infos about drawdown: Max. Trade Drawdown, Max. Trade % Drawdown

        Returns:
            [type]: [description]
        """
        
        drawdowns_array, max_dd_duration = self.calculate_drawdowns(
            self.__master_df['Equity'])
        drawdowns_array_pct, _ = self.calculate_drawdowns(
            self.__master_df['Equity %'])
        drawdowns = pd.DataFrame(data=drawdowns_array,
                                 index=self.__master_df.index)
        
        drawdowns['Drawdown %'] = drawdowns_array_pct
        drawdowns = drawdowns.rename(columns={'Equity':'Drawdown'})
        return drawdowns, max_dd_duration

    def create_drawdown_info(self):
        
        data = {
            'Max. Drawdown': max(self.__drawdowns['Drawdown']),
            'Max. Drawdown %': max(self.__drawdowns['Drawdown %']),
            'Max. Drawdown Duration': str(self.__max_dd_duration)
        }
        return pd.DataFrame.from_dict(data, orient='index')

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
        for ret in self.__trade_history['Return']:
            
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
            


    

    
    
