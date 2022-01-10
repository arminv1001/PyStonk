
class Trade(object):

    def __init__(self, symbol, date, size, current_capital, price, isOpen):

        self.symbol = symbol
        self.id = self._create_id()
        self._date = date
        self._size = size
        self._current_capital = current_capital
        self._price = price
        self._comission = comission
        self._isOpen = isOpen # is trade open (True) or closed (False)

        # profit & loss
        self.pnl_val = _calculate_pnl() # absolute profit & loss value
        self.pnl_pct = 0 # percentage of profit & loss

        def _create_id(self):
            """
            Creates unique identifier for trade: "<Symbol> + <crosssum of date>"
            """
            date = self.opendt.split(" ")[0].split("-")
            date = [int(string) for string in date]
            date_crosssum = sum(date)
            self.id = self.symbol + str(date_crosssum)

        def _calculate_pnl(self):
            """
            Calculates the profit & loss of a open or close trade 
            """
            factor = -1 if self.isOpen else 1 # entry=-1, exit=1
            self.pnl_val = self.current_capital - factor*(self.price * self.size - self.comission)
            self.pnl_pct = self.pnl_val/self.current_capital

        def update(self):
