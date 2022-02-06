from data_prep.CSVDataPreparer import *
from RSI import *
from equity.Equity import *
from statistics.SpreadSheet import *
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


if __name__ == "__main__":
    csv_dir = '/Users/mr.kjn/Projects/PyStonk/Backtest/backtest_data'
    symbol = 'AAPL'
    symbols = [symbol]
    
    csvDP = CSVDataPreparer(csv_dir=csv_dir, csv_symbols=symbols)
    start_date = '2015-01-01'
    end_date = '2021-12-31'
    start_capital = 10000
    comission = 0

    closes = csvDP.get_assets_historic_data(start_date, end_date, symbols)
    closes['20_SMA'] = closes[symbol].rolling(window=20, min_periods=1).mean()
    closes['50_SMA'] = closes[symbol].rolling(window=50, min_periods=1).mean()
    closes['Signal'] = 0
    closes['Signal'] = np.where(closes['20_SMA'] > closes['50_SMA'], 1, 0)
    closes['Position'] = closes['Signal'].diff().fillna(0)
    columns = ['50_SMA', '20_SMA']
    # Moving Average Crossover Strategy
    plt.figure(figsize=(20,5))
    #plt.plot(closes.index, closes[symbol], color="#425af5")
    #plt.plot(closes.index, closes['50_SMA'], color= "#f5b042")
    #plt.plot(closes.index, closes['20_SMA'], color= "#f5ef42")
    closes['Short_Signal'] = closes[symbol][closes['Position'] == -1]
    closes['Long_Signal'] = closes[symbol][closes['Position'] == 1]

    #print(closes)

    input_df = closes[[symbol, 'Position']]
    equity = Equity(symbol, closes, start_capital, comission)
    equity.create()
    eq = equity.equity_df

    master_df = pd.concat([closes, eq], axis=1)

    complete_capital = 50000
    quantity = 5
    time_period = 'days'
    spreadsheet = SpreadSheet(
        master_df, complete_capital, quantity, comission, time_period)

    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.general_info)
    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.performance_info)
    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.all_trades_info)
    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.position_history)
    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.winners)
    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.losers)
    print('---------------------------------------------------------------------------------------')
    print(spreadsheet.drawdowns)
    print('---------------------------------------------------------------------------------------')


    """
    print(master_df)


    complete_capital = 50000
    quantity = 5
    time_period = 'days'
    spreadsheet = SpreadSheet(master_df, complete_capital, quantity, comission, time_period)

    a = np.array([3])
    b = closes[symbol][closes['Position'] < 0]

    #print(bing)

    #print(do)




    #held = bing - bong
    #print(held)


    #plt.plot(closes.index, closes['Equity %'])

    #plt.scatter(closes.index, closes['Short_Signal'], color= "#CE5757", marker="v")
    #plt.scatter(closes.index, closes['Long_Signal'], color= "#57CE95", marker="^")
    #plt.show()
    
    """
    

