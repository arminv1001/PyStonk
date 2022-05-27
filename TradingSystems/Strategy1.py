from TradingSystems.TradingSystem import TradingSystem
from Broker import Broker

import numpy as np
import pandas as pd

class Strategy1(TradingSystem):
    def __init__(self, symbolsNames: list, alternativDataNames: list, systemName: str, systemType: str, systemStyle: int, broker: Broker, timeFrame: str, weekendTrading: bool = False, lookback_candels: int = None):
        super().__init__(symbolsNames, alternativDataNames, systemName, systemType, systemStyle, broker, timeFrame, weekendTrading, lookback_candels)
        
        
    def createSignal(self, parameter, lookback_period=-1):
        
        tmpData = super().getDatenHandler().getData()
        
        if lookback_period > 0:
            tmpData.tail(lookback_period)
        else:
           
            tmpData['20_SMA'] = tmpData['Close'].rolling(window=int(parameter), min_periods=1).mean()
            tmpData['50_SMA'] = tmpData['Close'].rolling(window=50, min_periods=1).mean()
            tmpData['Signal'] = 0
            tmpData['Signal'] = np.where(tmpData['20_SMA'] > tmpData['50_SMA'], -1, 0)
            tmpData['Signal'] = np.where(tmpData['20_SMA'] < tmpData['50_SMA'], 1, 0)
            tmpData['Signal'] = tmpData['Signal'].diff().fillna(0)
            columns = ['50_SMA', '20_SMA']
            # Moving Average Crossover Strategy
            #plt.plot(master_df.index, master_df[symbol], color="#425af5")
            #plt.plot(master_df.index, master_df['50_SMA'], color= "#f5b042")
            #plt.plot(master_df.index, master_df['20_SMA'], color= "#f5ef42")
            tmpData['Short_Signal'] = tmpData['Close'][tmpData['Signal'] == -1]
            tmpData['Long_Signal'] = tmpData['Close'][tmpData['Signal'] == 1]
            #master_df = master_df.rename(columns={symbol[0]:"Close"})
            tmpData = tmpData[["Date", "Close","Open","High","Low","Volume","Signal"]]

            tmpData = tmpData.rename(columns={'Date': 'Timestamp'})
            tmpData = tmpData.set_index('Timestamp')
            tmpData.index = pd.to_datetime(tmpData.index)

            
            
        super().setSignalDf(tmpData)
        #print(tmpData)