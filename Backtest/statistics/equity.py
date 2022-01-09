
class Equity(object):

    def __init__(self, capital, trades, index):
        self.capital = capital
        self.trades = trades
        self.equity_curve = None
    
    def calculate_single_equity(self, trade, eoe=True):
        factor = -1 if eoe else 1 # entry=-1, exit=1
        trade_price = trade.open_price if eoe else trade.close_price # set open or close price of trade

        return equity = self.capital - factor*(trade_price * trade.size - trade.comission)


    def get_equity_curve(self):

        for trade in self.trades:
            eq_open = calculate_single_equity(trade)
            if trade.isClosed:
                eq_close = calculate_single_equity(trade)
                trade.pnlcom = eq_close - eq_open

