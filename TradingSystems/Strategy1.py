from TradingSystems.TradingSystem import TradingSystem


from Broker import Broker
import numpy as np
class Strategy1(TradingSystem):
    def __init__(self, symbolsNames: list, alternativDataNames: list, systemName: str, systemType: str, systemStyle: int, broker: Broker, timeFrame: str, weekendTrading: bool = False, lookback_candels: int = None):
        super().__init__(symbolsNames, alternativDataNames, systemName, systemType, systemStyle, broker, timeFrame, weekendTrading, lookback_candels)
        
    def createSignal(self, lookback_period=-1):
        tmpData = super().getDatenHandler().getData()
        if lookback_period > 0:
            tmpData.tail(lookback_period)
        else:
            tmpData['20_SMA'] = tmpData['Close'].rolling(window=20, min_periods=1).mean()
            tmpData['50_SMA'] = tmpData['Close'].rolling(window=50, min_periods=1).mean()
            tmpData['Signal'] = 0
            tmpData['Signal'] = np.where(tmpData['20_SMA'] > tmpData['50_SMA'], 1, 0)
            tmpData['Position'] = tmpData['Signal'].diff().fillna(0)
            columns = ['50_SMA', '20_SMA']
            # Moving Average Crossover Strategy
            #plt.plot(master_df.index, master_df[symbol], color="#425af5")
            #plt.plot(master_df.index, master_df['50_SMA'], color= "#f5b042")
            #plt.plot(master_df.index, master_df['20_SMA'], color= "#f5ef42")
            tmpData['Short_Signal'] = tmpData['Close'][tmpData['Position'] == -1]
            tmpData['Long_Signal'] = tmpData['Close'][tmpData['Position'] == 1]
            #master_df = master_df.rename(columns={symbol[0]:"Close"})
        super().setSignalDf(tmpData)
        #print(tmpData)