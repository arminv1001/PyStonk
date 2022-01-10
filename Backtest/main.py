from data_prep.CSVDataPreparer import *
from RSI import *
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


if __name__ == "__main__":
    csv_dir = '/Users/mr.kjn/Projects/PyStonk/Backtest/backtest_data'

    symbols = ["AAPL"]
    csvDP = CSVDataPreparer(csv_dir=csv_dir, csv_symbols=symbols)

    closes = csvDP.get_assets_historic_data('2015-01-01', '2021-12-31', symbols)
    closes['20_SMA'] = closes['AAPL'].rolling(window=20, min_periods=1).mean()
    closes['50_SMA'] = closes['AAPL'].rolling(window=50, min_periods=1).mean()
    closes['Signal'] = 0
    closes['Signal'] = np.where(closes['20_SMA'] > closes['50_SMA'], 1, 0)
    closes['Position'] = closes['Signal'].diff()
    #print(closes)
    columns = ['50_SMA', '20_SMA']

    # Moving Average Crossover Strategy
    plt.figure(figsize=(20,5))
    plt.plot(closes.index, closes['AAPL'], color="#425af5")
    plt.plot(closes.index, closes['50_SMA'], color= "#f5b042")
    plt.plot(closes.index, closes['20_SMA'], color= "#f5ef42")
    closes['Short_Signal'] = closes['AAPL'][closes['Position'] == -1]
    closes['Long_Signal'] = closes['AAPL'][closes['Position'] == 1]
    plt.scatter(closes.index, closes['Short_Signal'], color= "#CE5757", marker="v")
    plt.scatter(closes.index, closes['Long_Signal'], color= "#57CE95", marker="^")
    plt.show()
    
    # to-do equity testen dann drawdown implementieren
    
    
    

