
import pandas as pd
from Broker import Broker
from datetime import datetime
class Datahandler:
    def __init__(self,SymbolsNames:list,AlternativDataNames:list,_Broker:Broker,TimeFrame):
        """_summary_

        Args:
            SymbolsNames (list): _description_
            AlternativDataNames (list): _description_
            _Broker (Broker): _description_
            TimeFrame (_type_): _description_
        """
        self.__symbols_names = SymbolsNames
        self.__alternativ_data_names = AlternativDataNames
        self.__broker = _Broker
        self.__data = None
        self.__last_hist_data_update = None
        self.__time_scale = TimeFrame
        self.getHistoricalData()
        self.getAlternativData()

    def getHistoricalData(self,start_date=None,end_date=None):
        self.__last_hist_data_update = datetime.now()
        for symbol in self.__symbols_names:
            if start_date == None and end_date == None:
                hist_data = self.__broker.getHistoricalData(symbol,self.__time_scale)
            elif start_date != None and end_date != None:
                hist_data = self.__broker.getHistoricalData(symbol,start_date,end_date,self.__time_scale)
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

    def getData(self)->pd.DataFrame:
        self.updateData()
        return self.__data
    
    def updateData(self):
        self.getHistoricalData(start_date=self.__last_hist_data_update,end_date=datetime.now())
        self.getAlternativData()

    def scaleData(data):
        #TODO Scale DateTime
        scaled_data = None
        return scaled_data
