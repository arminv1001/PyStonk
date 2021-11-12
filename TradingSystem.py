from Broker import Broker
from TelegramBot import TelegramBot
import pandas as pd
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
        TelegramBot.sendMessage(self.__system_name + " placed Trade")
    
    def closeOrder(self,id):
        self.__broker.closeOrder(id)
        TelegramBot.sendMessage(self.__system_name + " closed Order")
    
    def closeTrade(self,id):
        self.__broker.closeTrade(id)
        TelegramBot.sendMessage(self.__system_name + " closed Trade")

    def createSignal(self,lookback_period) -> pd.DataFrame:
        pass

    def checkSignal(self):
        pass


