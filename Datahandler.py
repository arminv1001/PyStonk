import pandas as pd
from Broker import Broker
class Datahandler:
    def __init__(self,SymbolsNames,AlternativDataNames,_Broker:Broker,TimeFrame):
        self.__symbols_names = SymbolsNames
        self.__alternativ_data_names = AlternativDataNames
        self.__broker = _Broker
        self.__data = None
        self.__time_scale = TimeFrame

    def getHistoricalData(self,start_date,end_date):
        for symbol in self.__symbols_names:
            hist_data = self.__broker.getHistoricalData(symbol,start_date,end_date)
            if self.__data != None:
                self.__data.merge(hist_data, left_on='DateTime', right_on='DateTime')

    def getAlternativData(self):
        for alternativ_data in self.__alternativ_data_names:
            #0 - name/path
            #1 - type
            if alternativ_data[1] == "csv":
                alt_data = pd.read_csv(alternativ_data[0])
            elif alternativ_data[1] == "excel":
                alt_data =  pd.read_excel(alternativ_data[0])
            else:
                print("Unknown type " + alternativ_data[1])
            if self.__data != None:
                self.__data.merge(alt_data, left_on='DateTime', right_on='DateTime')

    def getData(self):
        return self.__data
    
    def scaleData(data):
        #TODO Scale DateTime
        scaled_data = None
        return scaled_data
