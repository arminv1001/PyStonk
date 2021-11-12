from Broker import Broker
from TelegramBot import TelegramBot
class TadingSystem:
    #Abstrakte Klasse
    def __init__(self) -> None:
        self.__system_type = None
        self.__system_name = None
        self.__broker = Broker(None,None)
        self.__datenhanlder = None

    def getSystemType(self):
        return self.__system_type

    def placeOrder(self,price, stoploss=None, takeprofit=None):
        self.__broker.sendOrder(price=price)
        TelegramBot.sendMessage(self.__system_name + " placed Order")
    
    def placeTrade(self,price, stoploss=None, takeprofit=None):
        self.__broker.sendTrade(price=price)
        TelegramBot.sendMessage(self.__system_name + " placed Order")

        
