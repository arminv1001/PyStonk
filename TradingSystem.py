from Broker import Broker
from TelegramBot import TelegramBot
import pandas as pd
class TadingSystem:
    #Abstrakte Klasse
    def __init__(self) -> None:
        self.__system_type = None #TradingSystem or Indicator
        self.__system_style = None #long only = 1;short only = 2; long and short = 3
        self.__system_name = None
        self.__broker = None
        self.__datenhanlder = None
        self.__loockback_candels = None
        self.__last_signal = None

    def getSystemType(self):
        return self.__system_type

    def placeOrder(self,price, stoploss=None, takeprofit=None):
        self.__broker.sendOrder(price=price)
        TelegramBot.sendMessage(self.__system_name + " placed Order")
    
    def placeTrade(self,price=None, stoploss=None, takeprofit=None):
        self.__broker.sendTrade(price=price)
        TelegramBot.sendMessage(self.__system_name + " placed Trade")
    
    def closeOrder(self,id):
        self.__broker.closeOrder(id)
        TelegramBot.sendMessage(self.__system_name + " closed Order")
    
    def closeTrade(self,id):
        self.__broker.closeTrade(id)
        TelegramBot.sendMessage(self.__system_name + " closed Trade")

    def createSignal(self,lookback_period) -> pd.DataFrame:
        #Trading system
        pass

    def checkSignal(self):
        self.__datenhanlder.updateData()
        if self.__loockback_candels == None:
            print("You need to define loockback_candels")
            return None
        signal_df = self.createSignal(self.__loockback_candels)
        if self.__system_style == 1:
            signal_df = signal_df[signal_df["Long"] == 1]
            last_signal = signal_df["Long"].iloc[-1]
        elif self.__system_style == 2:
            signal_df = signal_df[signal_df["Short"] == 1]
            last_signal = signal_df["Long"].iloc[-1]
        elif self.__system_style == 3:
            signal_df = signal_df[signal_df["Short"] == 1 | signal_df["Long"] == 1]
            last_signal = signal_df.iloc[-1]

        if last_signal["Long"] == 1:
            last_signal = signal_df["Long"].iloc[-1]
        elif last_signal["Short"] == 1:
            last_signal = signal_df["Short"].iloc[-1]
        
        if last_signal > self.__last_signal:
            self.placeTrade()
            #TODO send to DB
        



