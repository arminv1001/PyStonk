from Broker import Broker
import os

from oandapyV20.contrib.requests import StopOrderRequest, StopLossOrderRequest
from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20 import oandapyV20
import oandapyV20.endpoints.orders as orders
class Oanda(Broker):
        def __init__(self, BrokerName, ApiUrl):
            super().__init__(BrokerName, ApiUrl)
            self.env = "demo"
            self.API_URL,self.ACCESS_TOKEN,self.ACCOUNT_ID = self.readLoginData()

        def readLoginData(self):
            dirname = os.path.dirname(__file__)
            file = os.path.join(dirname, "./Broker/LoginData/OandaData" + self.env + ".txt")
            logginData = []
            with open(file) as f:
                contents = f.readlines()  # API_URL # ACCESS_TOKEN # ACCOUNT_ID
            for line in contents:
                logginData.append(line.rstrip())
            return logginData[0],logginData[1],logginData[2]

        def sendOrder(self,price,stoploss=None,takeprofit=None) -> int:
            '''
            Place Stop Order or execute Market Order
            :return: Order ID
            '''
            #TODO Stoploss
            #TODO Takeprofit
            stopOrder = StopOrderRequest(
                instrument=self.INSTRUMENT,
                units=self.units,
                price=price
            )
            r = orders.OrderCreate(self.ACCOUNT_ID, data=stopOrder.data)
            API = oandapyV20.API(access_token=self.ACCESS_TOKEN, environment=self.ENV)
            try:
                # create the OrderCreate request
                rv = API.request(r)
                return rv["orderCreateTransaction"]["id"]
            except oandapyV20.exceptions.V20Error as err:
                return -1
        
        def sendTrade(self,price=None,stoploss=None,takeprofit=None) -> int:
            mktOrder = MarketOrderRequest(
                instrument=self.INSTRUMENT,
                units=self.units,
            )
            r = orders.OrderCreate(self.ACCOUNT_ID, data=mktOrder.data)
            API = oandapyV20.API(access_token=self.ACCESS_TOKEN, environment=self.ENV)
            try:
                # create the OrderCreate request
                rv = API.request(r)
                return rv["orderCreateTransaction"]["id"]
            except oandapyV20.exceptions.V20Error as err:
                return -1
