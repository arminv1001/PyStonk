from data_prep.CSVDataPreparer import *
from RSI import *
from equity.Equity import *
from statistics.SpreadSheet import *
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
# streamlit run dashboard.py

st.title("Dashboard")


def create_dashboard(symbol, master_df, trade_history_df, drawdown_df, spreadsheet_df):

    st.sidebar.header('Menu')
    
    dashboard_button = st.sidebar.button('Dashboard')
    trade_history_button = st.sidebar.button('Trade History')
    equity_button = st.sidebar.button('Equity')
    drawdown_button = st.sidebar.button('Drawdown')
    spreadsheet_button = st.sidebar.button('SpreadSheet')
    settings_button = st.sidebar.button('Settings')

    if settings_button:

        st.header('General')
        st.selectbox('Choose your strategy', ['Strategy 1', 'Strategy 2'])
        st.multiselect('Choose your Benchmark', [
                            'Benchmark 1', 'Benchmark 2'])
        st.multiselect('Choose your Data', ['Data 1', 'Data 2'])
        st.header('Date & Time')
        st.date_input('Start Date')
        st.time_input('Start Time')
        st.date_input('End Date')
        st.time_input('End Time')
        st.select_slider('Periodicity', ['1min', '5min', '15min', '1h', '6h', '1d', '5d', '1m', '3m', '6m', '1y', '5y', 'all'])
        st.header('Cash & Co.')
        st.number_input('Complete Capital')
        st.number_input('Comission')

    if trade_history_button:
        st.dataframe(trade_history_df)

    if equity_button:
        st.header('Equity')

        equity_rad = st.radio('in', ['absolute', 'percentage %'])
        if equity_rad == 'absolute':
            equity_data = master_df['Equity']
            
        elif equity_rad == 'percentage %':
            equity_data = master_df['Equity %']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=master_df.index, y=equity_data))
        fig.layout.update(title_text='Equity', xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

        st.dataframe(equity_data)
    
    if dashboard_button:
        st.header(symbol)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=master_df.index, y=master_df['Close'], name="Close Price"))
        fig.layout.update(
            title_text=symbol, xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

    if drawdown_button:
        st.header('Drawdown')

        equity_rad = st.radio('in', ['absolute', 'percentage %'])
        if equity_rad == 'absolute':
            equity_data = drawdown_df['Drawdown']
        elif equity_rad == 'percentage %':
            equity_data = drawdown_df['Drawdown %']

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=master_df.index, y=equity_data))
        fig.layout.update(
            title_text='Drawdown', xaxis_rangeslider_visible=True)
        st.plotly_chart(fig)

    if spreadsheet_button:
        st.header('SpreadSheet')

        st.dataframe(spreadsheet_df)



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


    closes = closes.rename(columns={symbol:'Close'})

    #print(closes)

    equity = Equity(symbol, closes, start_capital, comission)
    eq = equity.equity_df

    master_df = pd.concat([closes, eq], axis=1)

    complete_capital = 50000
    quantity = 5
    time_period = 'days'
    spreadsheet = SpreadSheet(
        master_df, complete_capital, quantity, comission, time_period)

    spreadsheet_df = spreadsheet.get_info_df()

    trade_history_df = spreadsheet.trade_history
    drawdowns_df = spreadsheet.drawdowns
    print(spreadsheet_df)

    create_dashboard(symbol, master_df, trade_history_df,
                     drawdowns_df, spreadsheet_df)

    """
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
    

