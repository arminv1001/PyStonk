import pandas as pd
class Broker:
    ## Abstrakte Klasse
    def __init__(self,BrokerName:str,ApiUrl:str):
        self.__broker_name = BrokerName
        self.API_URL = ApiUrl
    
    def getBrokerName(self):
        return self.__broker_name
    
    def sendOrder(self,price,stoploss=None,takeprofit=None) -> int:
        #"Need to be implemented"
        pass
    
    def sendTrade(self,stoploss=None,takeprofit=None) -> int:
        #"Need to be implemented"
        pass
    
    def closeTrade(self,id) -> bool:
        #"Need to be implemented"
        pass
    
    def closeOrder(self,id) -> bool:
        #"Need to be implemented
        pass

    def getHistoricalData(self,symbol:str,timeframe:str) -> pd.DataFrame:
        # if start and end date is none than get max data
        return "Need to be implemented"
        
    def getHistoricalData(self,symbol:str,start_date,end_date,timeframe:str) -> pd.DataFrame:
        # if start and end date is none than get max data
        return "Need to be implemented"
    
    def readLoginData(self):
        # Need to be implemented
        pass