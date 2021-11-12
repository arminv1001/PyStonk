class Broker:
    ## Abstrakte Klasse
    def __init__(self,BrokerName,ApiUrl):
        self.__broker_name = BrokerName
        self.__api_url = ApiUrl
    
    def getBrokerName(self):
        return self.__broker_name
    
    def sendOrder(self,price,stoploss=None,takeprofit=None):
        return "Need to be implemented"
    
    def sendTrade(self,price=None,stoploss=None,takeprofit=None):
        return "Need to be implemented"
    
    def closeTrade(self,id):
        return "Need to be implemented"
    
    def closeOrder(self,id):
        return "Need to be implemented"

    def getHistoricalData(self,start_date,end_date):
        return "Need to be implemented"