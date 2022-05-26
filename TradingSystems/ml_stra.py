from TradingSystems.TradingSystem import TradingSystem
from TradingSystems.featureCreatenClass import featuresGen
from keras.models import load_model
from Broker import Broker
import pandas as pd
import numpy as np
class ml_strat_reg(TradingSystem):
    def __init__(self, symbolsNames: list, alternativDataNames: list, systemName: str, systemType: str, systemStyle: int, broker: Broker, timeFrame: str, weekendTrading: bool = False, lookback_candels: int = None):
        super().__init__(symbolsNames, alternativDataNames, systemName, systemType, systemStyle, broker, timeFrame, weekendTrading, lookback_candels)
        self.model = load_model('TradingSystems/ml_system/1_lstm_V2_reg.h5')
        
    def createSignal(self, lookback_period=-1):
        tmpData = super().getDatenHandler().getData()
        if lookback_period > 0:
            tmpData.tail(lookback_period)
        else:
            tmpData.index = pd.to_datetime(tmpData["Timestamp"])
            tmpData_features = featuresGen(tmpData)
            tmpData_features = tmpData_features.drop(["Timestamp","zscores","Target","Label","Asset_ID","index","Open","High","Low","Close","Volume"], axis=1).reset_index(drop=True)
            tmpData_features.index = tmpData_features.index.astype("int")
            #TODO drop features - Low,Close,Open,High
            #TODO sequenzierung
            n_future = 1 #Naechste 15min prädizieren
            n_past = 16
            train_x = []
            for i in range(n_past,len(tmpData_features)-n_future+1):
                train_x.append(tmpData_features.iloc[i-n_past:i, 0:tmpData_features.shape[1]])
            train_x = np.array(train_x)
            trainPredict = self.model.predict(train_x)
            diff_len = len(tmpData) - len(trainPredict)
            tmpData = tmpData.iloc[diff_len:,]
            tmpData["Target"] = trainPredict
            # Tradingsystem
            
            openTrades =  False
            counter = 0
            #np.zero
            position_list = np.zeros([len(tmpData),])
            target_stopLoss = [0,0]
            tmpData = tmpData.reset_index(drop=True)
            tmpData.index = tmpData.index.astype("int")  
            for index,row in tmpData.iterrows():
                if (row["Minute"] % 15) == 0:
                    if row["Target"] > 0:
                       counter = 14
                       openTrades = True
                       target_stopLoss[0] = row["Target"] * row["Close"] + row["Close"]
                       target_stopLoss[1] = row["Close"] * 0.05 + row["Close"]
                       position_list[index] = 1
                    elif counter > 0:
                        print("Error - Überschreitung")
                        
                elif counter > 0 and openTrades == True:
                    if target_stopLoss[1] >= row["Low"] or target_stopLoss[0] <= row["High"]:
                        position_list[index] = -1
                        counter = 0
                        openTrades = False
                    else:
                        counter -= 1
            tmpData["Position"] = position_list
            tmpData = tmpData.iloc[:int(len(tmpData))]
            tmpData = tmpData.set_index("Timestamp")
            tmpData = tmpData[["Close","Open","High","Low","Volume","Position"]]
            
            super().setSignalDf(tmpData)
        #print(tmpData)