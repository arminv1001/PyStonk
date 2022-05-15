from typing_extensions import Self
from Daten.Datahandler import Datahandler
from Broker import Broker
from TelegramBot import TelegramBot
import pandas as pd
import Database.db_functions as db
#from LiveTradingSystem import LiveTradingSytem

class TradingSystem:
    #Abstrakte Klasse
    def __init__(self,symbolsNames:list,alternativDataNames:list,systemName:str, systemType:str, systemStyle:int, broker:Broker, timeFrame:str,weekendTrading:bool = False, lookback_candels:int = None):
        """
        TradingSystem
        Args:
            symbolsNames (list): symbol name list (live)
            alternativDataNames (list): alternative data list - [0] - data name --- [1] - type [csv, excel] 
            systemName (str): system name
            systemType (str): system type - TradingSystem or Indicator
            systemStyle (int): long only = 1; short only = 2; long and short = 3
            broker (Broker): Broker
            timeFrame (str): Time Frame
            weekendTrading (bool, optional): if weekends trading is allowed set true. Defaults to False.
            lookback_candels (int, optional): number of lookback candels. Defaults to None.
        """
        self.__system_type = systemType
        self.__system_style = systemStyle
        self.__system_name = systemName
        self.__broker = broker
        self.__time_frame = timeFrame
        self.__weekend_trading = weekendTrading
        self.__datenhandler = Datahandler(symbolsNames,alternativDataNames,broker,timeFrame)
        self.__loockback_candels = lookback_candels
        self.__last_signal = 0 # -1 short | 0 nothing | 1 buy
        self.__order_list = []
        self.__signal_df = None #Kursdaten + Signale
        
    def getSystemType(self):
        return self.__system_type

    def getTimeFrame(self):
        return self.__time_frame
    
    def getWeekendTrading(self):
        return self.__weekend_trading
    
    def getDatenHandler(self):
        return self.__datenhandler
    
    def setSignalDf(self,signal_df:pd.DataFrame):
        self.__signal_df = signal_df
    

    def placeOrder(self,price:float, stoploss:float=None, takeprofit:float=None):
        """Place Order

        Args:
            price (float): price
            stoploss (float, optional): Stoploss Price. Defaults to None.
            takeprofit (float, optional): Takeprofit Price. Defaults to None.
        """
        order_id = self.__broker.sendOrder(price=price,stoploss=stoploss,takeprofit=takeprofit)
        db.saveOrderID(order_id,self.__system_name)
        self.__order_list.append(order_id)
        TelegramBot.sendMessage(self.__system_name + " placed Order")
    
    def placeTrade(self, stoploss:float=None, takeprofit:float=None):
        """Place Trade

        Args:
            stoploss (float, optional): Stoploss Price. Defaults to None.
            takeprofit (float, optional): Takeprofit Price. Defaults to None.
        """
        order_id = self.__broker.sendTrade(stoploss=stoploss,takeprofit=takeprofit)
        db.saveOrderID(order_id,self.__system_name)
        self.__order_list.append(order_id)
        TelegramBot.sendMessage(self.__system_name + " placed Trade")
    
    def closeOrder(self,id:int):
        """Close Order by ID

        Args:
            id (int): Order ID
        """
        if self.__broker.closeOrder(id):
            db.deleteOrderID(id)
            TelegramBot.sendMessage(self.__system_name + " closed Order")
        else:
            TelegramBot.sendMessage(self.__system_name + " failed Trade")

    def closeTrade(self,id:int):
        """Close Trade by ID

        Args:
            id (int): Order ID
        """
        if self.__broker.closeTrade(id):
            db.deleteOrderID(id)
            TelegramBot.sendMessage(self.__system_name + " closed Trade")
        else:
            TelegramBot.sendMessage(self.__system_name + " failed Trade")

    def createSignal(self,lookback_period=-1):
        """Generates Trading labels
            1 - long
            0 - nothing
           -1 - short

        Args:
            lookback_period (int, optional): Lookback Periode. Defaults to -1.
        """
        #tmpData = self.__datenhandler.getData()
        #if lookback_period > 0:
         #   tmpData.tail(lookback_period)
        #else:
            #Trading system
        #signal_df = ...
        pass
    
    def getSignalDf(self)->pd.DataFrame:
        return self.__signal_df
    
    def tradingHandler(self):
        """How system has to react to a new state
        """
        # Implement
        pass

    def checkSignal(self):
        """Check for Signal
        """
        if self.__loockback_candels == None:
            print("You need to define loockback_candels")
            return None
        self.createSignal(self.__loockback_candels)
        if self.__signal_df["Position"].iloc[-1] != self.__last_signal:
            if self.__system_style == 1: #long
                if self.__signal_df["Position"].iloc[-1] == -1:
                    return None
                else:
                    self.__last_signal = self.__signal_df["Position"].iloc[-1]
            elif self.__system_style == 2: #short
                if self.__signal_df["Position"].iloc[-1] == 1:
                    return None
                else:
                    self.__last_signal = self.__signal_df["Position"].iloc[-1]
            elif self.__system_style == 3: #long & short
                self.__last_signal = self.__signal_df["Position"].iloc[-1]

            self.tradingHandler()
            #LiveTradingSytem.startScheduler(self)    
       
        

        



