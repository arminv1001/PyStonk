import numpy as np
import pandas as pd
from statistics.performance_measurements import *

PERIODS = {
    "Annually": 12,
    "Daily": 252,
    "Hourly": 252*6.5,
    "Minutely": 252*6.5*60,
    "Secondly": 252*6.5*60*60}
    
MAX_DD_D_PERIOD = np.power(60,2)*24

class SpreadSheet(object):

    def __init__(self, df, complete_capital, pos_size, comission, periodicity):
        self.__master_df = df
        # self.benchmark_df = benchmark
        self.__complete_capital = complete_capital
        self.__pos_size = pos_size # position size
        self.__comission = comission

        self.__periodicity = periodicity

        self.__general_info = self.__create_general_info()
        self.__trade_history = self.__create_trade_history_df()
        self.__all_trades_info = self.__create_all_trades()
        self.__winners = self.__create_winners()
        self.__losers = self.__create_losers()

        self.__drawdowns, self.__max_dd_duration = get_drawdowns(self.__master_df[['Equity', 'Equity %']])
        self.__drawdowns_info = self.__create_drawdown_info()

        self.__performance_info = self.__create_performance_info()
    
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
    def drawdowns_info(self):
        return self.__drawdowns_info

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
        info_df = pd.concat(frames)
        return info_df


    def __create_general_info(self):
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
            #'Exposure': self.__master_df['Equity'][0] / self.__complete_capital,
            'Annual Return %': calculate_cagr(self.__master_df['Equity']),
            'Transaction Costs': len(self.__master_df[self.__master_df['Position'] != 0]) * self.__pos_size * self.__comission
        }
        general_info = pd.DataFrame.from_dict(data, orient='index')
        general_info = general_info.rename(columns={0: "Data"})
        return general_info
    
    def __create_trade_history_df(self):
        """
        Retuns DataFrame with history of position: Start Date, End Date, Return, Return %, Bars Held

        Returns:
            pd.DataFrame: History all positions DataFrame
        """
        long_dates, short_dates, _ = get_long_short_dates(self.__master_df['Position'])
        returns, returns_pct = get_return_of_trades(self.__master_df['Close'], long_dates, short_dates)
        bars_held = get_bars_held(self.__master_df['Position'])

        data = {
            'Start Date': long_dates,
            'End Date': short_dates,
            'Return': returns,
            'Return %': returns_pct,
            'Bars Held': bars_held
        }

        trade_hist = pd.DataFrame.from_dict(data, orient='index').transpose()
        trade_hist = trade_hist.rename(columns={0: "Data"})
        return trade_hist


    def __create_performance_info(self):
        """
        Returns DataFrame with performance measurements: Sharpe Ratio, Sortino Ratio, Alpha, Beta

        Returns:
            pd.DataFrame: Performance measurements DataFrame
        """
        sharpe = calculate_sharpe_ratio(self.__trade_history['Return %'])
        sortino = calculate_sortino_ratio(
            self.__trade_history['Return %'])
        beta, alpha = calculate_beta_alpha(self.__trade_history['Return %'], self.__trade_history['Return %']) # TO-DO: benchmark
        cagr = calculate_cagr(self.__master_df['Equity %'])
        mar = calculate_mar_ratio(cagr, self.__drawdowns_info.loc['Max. Drawdown %'][0])
        calmar = calculate_calmar_ratio(
            self.__trade_history['Return %'].mean(), self.__drawdowns_info.loc['Max. Drawdown %'][0])
        data = {
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino,
            'Alpha': alpha,
            'Beta': beta,
            'CAGR': cagr,
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
        data = {
            'Avg. PnL': self.__trade_history['Return'].mean(),
            'Avg. PnL %': self.__trade_history['Return %'].mean(),
            'Avg. Bars held': round(get_bars_held(self.__master_df['Position']).mean())
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
       
        winner_bars = self.__trade_history['Bars Held'][self.__trade_history['Return'] > 0]
        largest_win = self.__trade_history['Return'][self.__trade_history['Return'] > 0].max(
        )

        data = {
            'Total Profit': self.__trade_history['Return'][self.__trade_history['Return'] > 0].sum(),
            'Avg. Profit': self.__trade_history['Return'][self.__trade_history['Return'] > 0].mean(),
            'Avg. Bars Held': float('NaN') if winner_bars.empty else int(winner_bars.mean()),
            'Max. Consecutive': get_consecutive(self.__trade_history['Return']),
            'Largest Win': largest_win,
            'Bars in Largest Win': self.__trade_history['Bars Held'][self.__trade_history['Return'] == largest_win].iloc[0]

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
        loser_bars = self.__trade_history['Bars Held'][self.__trade_history['Return'] < 0]
        largest_loss = self.__trade_history['Return'][self.__trade_history['Return'] < 0].max(
        )
        data = {
            'Total Profit': self.__trade_history['Return'][self.__trade_history['Return'] < 0].sum(),
            'Avg. Profit': self.__trade_history['Return'][self.__trade_history['Return'] < 0].mean(),
            'Avg. Bars Held': float('NaN') if loser_bars.empty else int(loser_bars.mean()),
            'Max. Consecutive': get_consecutive(self.__trade_history['Return']),
            'Largest Loss': self.__trade_history['Return'][self.__trade_history['Return'] > 0].max(),
            'Bars in Largest Loss': self.__trade_history['Bars Held'][self.__trade_history['Return'] == largest_loss].iloc[0]
        }

        losers = pd.DataFrame.from_dict(data, orient='index')
        losers = losers.rename(columns={0: "Data"})
        return losers

    def __create_drawdown_info(self):
        
        data = {
            'Max. Drawdown': max(self.__drawdowns['Drawdown']),
            'Max. Drawdown %': max(self.__drawdowns['Drawdown %']),
            'Max. Drawdown Duration': self.__max_dd_duration.total_seconds()/MAX_DD_D_PERIOD
        }
        dd = pd.DataFrame.from_dict(data, orient='index')
        dd = dd.rename(columns={0: "Data"})
        return dd

    
            


    

    
    
