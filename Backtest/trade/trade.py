
class Trade(object):

    def __init__(self):

        self.symbol = symbol
        self.opendt = opendt
        self.closedt = closedt
        self.id = self.create_id()
        self.size = size
        self.price = price
        self.value = value
        self.comission = comission

        # profit & loss
        self.pnl = 0
        self.pnlcom = 0

        def create_id(self):
            date = self.opendt.split(" ")[0].split("-")
            date = [int(string) for string in date]
            date_crosssum = sum(date)
            self.id = self.symbol + str(date_crosssum)
