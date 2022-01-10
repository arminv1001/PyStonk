
class Equity(object):

    def __init__(self, trades, index):
        self._trades = trades
        self.equity_series = pd.Series(index=pd.date_range(self.trades.start_date, self.trades_end_date))
    
    def _calculate_single_pnl(self, trade, eoe=True):
        factor = -1 if trade.isOpen else 1 # entry=-1, exit=1
        return pnl = trade.current_capital - factor*(trade.price * trade.size - trade.comission)


    def get_equity_series(self):
        for trade in self._trades:
            # get pnl for open trade
            self.equity_series[trade.open_date] = trade.pnl_value
        self.equity_series.fillna(method="ffill") # fill NaN with prev value
        self.equity_series.pct_change(1).cumsum() # cumulative percentage change of profit & loss 




