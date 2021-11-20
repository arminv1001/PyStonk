import pandas as pd
class Broker:
    ## Abstrakte Klasse
    def __init__(self,BrokerName,ApiUrl):
        self.__broker_name = BrokerName
        self.__api_url = ApiUrl
    
    def getBrokerName(self):
        return self.__broker_name
    
    def sendOrder(self,price,stoploss=None,takeprofit=None) -> int:
        #"Need to be implemented"
        pass
    
    def sendTrade(self,price=None,stoploss=None,takeprofit=None) -> int:
        #"Need to be implemented"
        pass
    
    def closeTrade(self,id) -> bool:
        #"Need to be implemented"
        pass
    
    def closeOrder(self,id) -> bool:
        #"Need to be implemented
        pass

    def getHistoricalData(self,symbol) -> pd.DataFrame:
        # if start and end date is none than get max data
        return "Need to be implemented"
        
    def getHistoricalData(self,symbol,start_date,end_date) -> pd.DataFrame:
        # if start and end date is none than get max data
        return "Need to be implemented"
    
    def readLoginData(self):
        # Need to be implemented
        pass