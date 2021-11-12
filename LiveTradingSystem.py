from _typeshed import Self


class LiveTradingSytem:
    def __init__(self,TradingSystems:list):
        self.__trading_systems = TradingSystems

    def main(self):
        while(1):
            for trading_system in self.__trading_systems:
                trading_system.checkSignal()