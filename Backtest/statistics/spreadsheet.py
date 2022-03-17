import numpy as np
import pandas as pd
from statistics.performance_measurements import *
from drawdown.Drawdown import *
from tools.toolbox import *

PERIODS = {
    "Annually": 12,
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}
    
MAX_DD_D_PERIOD = np.power(60,2)*24

class SpreadSheet(object):

    def __init__(self, df, equity_df, trade_history, performance, drawdown, start_capital, comission, periodicity):

        self.__master_df = df
        self.__equity_df = equity_df
        self.__trade_history = trade_history
        self.__performance_measurement = performance
        self.__drawdown = drawdown
        self.__start_capital = start_capital
        self.__comission = comission
        self.__periodicity = periodicity

        self.__general_info = self.__create_general_info()

        self.__all_trades_info = self.__create_all_trades()
        self.__winners = self.__create_winners()
        self.__losers = self.__create_losers()

        
        
        
        # extract out of class
        

        self.__performance_info = self.__create_performance_info()

        self.__runs_info = self.__create_runs_info()

    
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
    def runs_info(self):
        return self.__runs_info


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
            self.__runs_info
        ]
        info_df = pd.concat(frames)

        return info_df


    def __create_general_info(self):
        """
        Return DataFrame with general information: Initial Capital, Ending Capital, Net Profit, Net Profit %, Initial Capital, Exposure, Annual Returns %, Transaction Costs

        Returns:
            pd.DataFrame: General Information DataFrame
        """

        initial_capital = self.__equity_df['Equity'][0]
        ending_capital = self.__equity_df['Equity'][-1]
        net_profit = self.__equity_df['Equity'][-1] - \
            self.__equity_df['Equity'][0]
        net_profit_pct = (
            self.__equity_df['Equity'][-1] - self.__equity_df['Equity'][0]) / self.__equity_df['Equity'][0]
        trans_cost = len(self.__trade_history) * self.__comission

        data = {
            'Initial Capital': initial_capital,
            'Ending Capital': ending_capital,
            'Net Profit': net_profit,
            'Net Profit %': net_profit_pct,
            'Transaction Costs': trans_cost 
        }

        general_info = pd.DataFrame.from_dict(data, orient='index')
        general_info = general_info.rename(columns={0: "Data"})
        return general_info


    def __create_performance_info(self):
        """
        Returns DataFrame with performance measurements: Sharpe Ratio, Sortino Ratio, Alpha, Beta

        Returns:
            pd.DataFrame: Performance measurements DataFrame
        """

        trade_history = self.__trade_history
        exposure = sum(trade_history['Bars Held']) / \
            len(self.__master_df.index)  # Time Exposure
        sharpe = self.__performance_measurement.calculate_sharpe_ratio()
        sortino = self.__performance_measurement.calculate_sortino_ratio()
        rap, rm = self.__performance_measurement.calculate_mm_ratio()
        sterling = self.__performance_measurement.calculate_sterling_ratio(self.__drawdown.df_pct)
        burke = self.__performance_measurement.calculate_burke_ratio(
            self.__drawdown.df_pct)
        beta, alpha = self.__performance_measurement.calculate_beta_alpha()
        cagr = self.__performance_measurement.calculate_cagr()
        mar = self.__performance_measurement.calculate_mar_ratio(cagr, self.__drawdown.max_duration_bars)
        calmar = self.__performance_measurement.calculate_calmar_ratio(
            self.__drawdown.max_duration_bars)
        data = {
            'Exposure %': exposure,
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino,
            'M&M Ratio: RAP': rap,
            'M&M Ratio: rm': rm,
            'Alpha': alpha,
            'Beta': beta,
            'CAGR %': cagr,
            'MAR': mar,
            'Calmar': calmar
        }

        performance = pd.DataFrame.from_dict(data, orient='index')
        performance = performance.rename(columns={0: "Data"})
        return performance
    
    def __create_all_trades(self):
        """
        Returns DataFrame with info regarding all trades

        Returns:
            pd.DataFrame: Info regarding all trades DataFrame
        """

        trade_history = self.__trade_history

        data = {
            'Avg. PnL': trade_history['Return'].mean(),
            'Avg. PnL %': trade_history['Return %'].mean(),
            'Avg. Bars held': int(self.__trade_history['Bars Held'].mean())
        }

        all_trades = pd.DataFrame.from_dict(data, orient='index')
        all_trades = all_trades.rename(columns={0: "Data"})
        return all_trades

    def __create_winners(self):
        """
        Retuns DataFrame with infos about winning trades: Total Profit, Avg. Profit, Avg, Bars Held, Max. Consecutive, Largest Win, Bars in Largest Win

        Returns:
            pd.DataFrame: Infos about winning trades DataFrame
        """

        trade_history = self.__trade_history

        if trade_history.empty:
            total_profit = np.nan
            avg_profit = np.nan
            avg_bars_held = np.nan
            max_consecutive = np.nan
            largest_win = np.nan
            bars_in_largest_win = np.nan
        else:
            winner_bars = trade_history['Bars Held'][trade_history['Return'] > 0]
            total_profit = trade_history['Return %'][trade_history['Return %'] > 0].sum(
            )
            avg_profit = trade_history['Return %'][trade_history['Return %'] > 0].mean(
            )
            avg_bars_held = float(
                'NaN') if winner_bars.empty else int(winner_bars.mean())
            max_consecutive = get_consecutive(trade_history['Return'])
            largest_win = trade_history['Return'][trade_history['Return'] > 0].max(
            )
            bars_in_largest_win = trade_history['Bars Held'][trade_history['Return']
                                                              == largest_win].iloc[0]
       
        data = {
            'Total Profit': total_profit,
            'Avg. Profit %': avg_profit,
            'Avg. Bars Held': avg_bars_held,
            'Max. Consecutive': max_consecutive,
            'Largest Win': largest_win,
            'Bars in Largest Win': bars_in_largest_win
        }

        winners = pd.DataFrame.from_dict(data, orient='index')
        winners = winners.rename(columns={0: "Data"})
        return winners

    def __create_losers(self):
        """
        Retuns DataFrame with infos about losing trades: Total Loss, Avg. Loss, Avg, Bars Held, Max. Consecutive, Largest Loss, Bars in Largest Loss

        Returns:
            pd.DataFrame: History all positions DataFrame
        """

        trade_history = self.__trade_history

        if trade_history.empty:
            total_profit = np.nan
            avg_profit = np.nan
            avg_bars_held = np.nan
            max_consecutive = np.nan
            largest_loss = np.nan
            bars_in_largest_loss = np.nan
        else:
            loser_bars = trade_history['Bars Held'][trade_history['Return'] < 0]
            total_profit = trade_history['Return %'][trade_history['Return %'] < 0].sum(
            )
            avg_profit = trade_history['Return %'][trade_history['Return %'] < 0].mean(
            )
            avg_bars_held = float(
                'NaN') if loser_bars.empty else int(loser_bars.mean())
            max_consecutive = get_consecutive(trade_history['Return'])
            largest_loss = trade_history['Return'][trade_history['Return'] < 0].max()
            bars_in_largest_loss = trade_history['Bars Held'][trade_history['Return'] == largest_loss].iloc[0]

        data = {
            'Total Profit': total_profit,
            'Avg. Profit': avg_profit,
            'Avg. Bars Held': avg_bars_held,
            'Max. Consecutive': max_consecutive,
            'Largest Loss': largest_loss,
            'Bars in Largest Loss': bars_in_largest_loss
        }

        losers = pd.DataFrame.from_dict(data, orient='index')
        losers = losers.rename(columns={0: "Data"})
        return losers

    def __create_runs_info(self):

        trade_history = self.__trade_history

        hhi_positive = self.__performance_measurement.calculate_hhi(
            trade_history['Return %'][trade_history['Return'] > 0])
        hhi_negative = self.__performance_measurement.calculate_hhi(
            trade_history['Return %'][trade_history['Return'] < 0])
        
        data = {
            'HHI on + Returns': hhi_positive,
            'HHI on - Returns': hhi_negative,
            'Max. Drawdown': max(self.__drawdown.df),
            'Max. Drawdown %': max(self.__drawdown.df_pct),
            'Max. Drawdown Duration (bars)': self.__drawdown.max_duration_bars,
        }
        dd = pd.DataFrame.from_dict(data, orient='index')
        dd = dd.rename(columns={0: "Data"})
        return dd

    
            


    

    
    
