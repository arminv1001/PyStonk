from data_prep.CSVDataPreparer import *
from equity.Equity import *
from statistics.SpreadSheet import *
from strategy.strategy1 import *
from tools.toolbox import *

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
import os



def run_backtest_viewer():

    st.title("Backtest Dashboard")

    bt_settings_dict = view_sidebar_settings()

    run = st.button('Run')

    master_df, spreadsheet, trade_history_df, drawdowns_df = create_backtest(
        bt_settings_dict)

    view_dashboard(bt_settings_dict, master_df)
    view_trade_history(trade_history_df)
    view_equity(master_df[['Equity', 'Equity %']])
    view_drawdown(drawdowns_df)
    view_spreadsheet(spreadsheet)


def view_trade_history(trade_history_df):
        st.header('Trade History')
        st.dataframe(trade_history_df, 1100, 200)

def view_equity(equity_df):
    st.header('Equity')
    equity_rad = st.radio('', ['absolute', 'percentage %'], key="<equity_rad>")

    if equity_rad == 'absolute':
        equity_data = equity_df['Equity']

    elif equity_rad == 'percentage %':
        equity_data = equity_df['Equity %']


    fig = go.Figure()
    fig.add_trace(go.Scatter(x=equity_df.index, y=equity_data))
    fig.layout.update(title_text='Equity',
                        xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

def view_drawdown(drawdown_df):
    st.header('Drawdown')
    dd_rad = st.radio('', ['absolute', 'percentage %'], key="<dd_rad>")
    if dd_rad == 'absolute':
        drawdown_data = drawdown_df['Drawdown']
    elif dd_rad == 'percentage %':
        drawdown_data = drawdown_df['Drawdown %']

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown_df.index, y=drawdown_data))
    fig.layout.update(
        title_text='Drawdown', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


def view_spreadsheet(spreadsheet):
    st.header('SpreadSheet')
    
    gen_info_col, perf_col = st.columns(2)
    gen_info_col.subheader('General Information')
    perf_col.subheader('Performance')
    gen_info_col.dataframe(spreadsheet.general_info)
    perf_col.dataframe(spreadsheet.performance_info)

    all_trades_col, dd_col = st.columns(2)
    all_trades_col.subheader('All Trades')
    all_trades_col.dataframe(spreadsheet.all_trades_info)
    dd_col.subheader('Drawdowns')
    dd_col.dataframe(spreadsheet.drawdowns_info)

    winner_col, loser_col = st.columns(2)
    winner_col.subheader('Winners')
    winner_col.dataframe(spreadsheet.winners)
    loser_col.subheader('Losers')
    loser_col.dataframe(spreadsheet.losers)

    
    
   

def view_dashboard(bt_settings_dict, master_df):
    st.header("General Info")
    chart_type= st.selectbox('Select Chart Type', ['OHLC', 'Close'])

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(chart_type, 'Volume'),
                        row_width=[0.2, 0.7])

    if (chart_type == 'OHLC'):
        # Plot OHLC on 1st row
        fig.add_trace(go.Candlestick(x=master_df.index, open=master_df['Open'], high=master_df["High"],
                                     low=master_df["Low"], close=master_df["Close"], name="OHLC"), row=1, col=1)
    elif (chart_type == 'Close'):
        # Plot Close on 1st row
        fig.add_trace(go.Scatter(
            x=master_df.index, y=master_df['Close'], name="Close Price"), row=1, col=1)

    # Bar trace for volumes on 2nd row without legend
    fig.add_trace(go.Bar(x=master_df.index, y=master_df['Volume'],
                         showlegend=True, name="Volume"), row=2, col=1)

    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=master_df['Close'][master_df['Position'] == -1].index,
            y=master_df['Close'][master_df['Position'] == -1],
            marker=dict(
                color=px.colors.qualitative.D3[3],
                size=10
            ),
            name = 'Sell'
        )
    )


    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=master_df['Close'][master_df['Position'] == 1].index,
            y=master_df['Close'][master_df['Position'] == 1],
            marker=dict(
                color=px.colors.qualitative.D3[0],
                size=10
            ),
            name = 'Buy'
        )
    )


    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor = 'dimgrey'
            ),
            rangeslider=dict(
                visible=False
            ),
            type="date"
        )
    )
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.layout.yaxis2.showgrid = False

    st.plotly_chart(fig)


def view_sidebar_settings():

    strategy_list = get_filenames_from('strategy')
    benchmark_list = get_filenames_from('benchmark')
    symbols_list = get_filenames_from('backtest_data')

    # General
    st.sidebar.header('General')
    strategy = st.sidebar.selectbox(
        'Choose your strategy', strategy_list)
    symbols_csv = st.sidebar.multiselect('Symbol', symbols_list)
    symbols = [symbol.replace('.csv', '') for symbol in symbols_csv]
    benchmark = st.sidebar.selectbox('Benchmark', benchmark_list)

    # Trading Seetings
    # TO-DO: for different time periods
    st.sidebar.header('Trading Settings')
    et = ['Current Day Close Price', 'Next Day Close Price']
    buy_ex_type = st.sidebar.selectbox('Buy Execution Type', et, key = "<buy_ex_type>")
    sell_ex_type = st.sidebar.selectbox('Sell Execution Type', et, key = "<sell_ex_type>")

    # Date & Time
    st.sidebar.header('Date & Time')
    start_date = st.sidebar.date_input('Start Date')
    start_time = st.sidebar.time_input('Start Time')
    end_date = st.sidebar.date_input('End Date')
    end_time = st.sidebar.time_input('End Time')
    periodicity = st.sidebar.select_slider('Periodicity', ['Secondly', 'Minutely', 'Hourly', 'Daily'])

    # Cash & Co
    st.sidebar.header('Cash & Co.')
    start_capital = st.sidebar.number_input('Start Capital')
    size = st.sidebar.number_input('Size')
    comission = st.sidebar.number_input('Comission')

    bt_settings_dict = {
        'strategy': strategy,
        'symbols': symbols,
        'benchmark': benchmark,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'periodicity': periodicity,
        'start_capital': start_capital,
        'size': size,
        'comission': comission
    }

    return bt_settings_dict

def create_backtest(view_settings_dict):
    master_df = run_strategy(
        view_settings_dict['symbols'], view_settings_dict['start_date'], view_settings_dict['end_date'])

    equity = Equity(
        view_settings_dict['symbols'], master_df, view_settings_dict['start_capital'], view_settings_dict['comission'], view_settings_dict['size'])
    eq = equity.equity_df

    master_df = pd.concat([master_df, eq], axis=1)

    spreadsheet = SpreadSheet(
        master_df, view_settings_dict['start_capital'], view_settings_dict['size'], view_settings_dict['comission'], view_settings_dict['periodicity'])

    #spreadsheet_df = spreadsheet.get_info_df()
    #spreadsheet_df = spreadsheet_df

    trade_history_df = spreadsheet.trade_history
    trade_history_df = trade_history_df

    drawdowns_df = spreadsheet.drawdowns
    drawdowns_df = drawdowns_df

    return master_df, spreadsheet, trade_history_df, drawdowns_df




    