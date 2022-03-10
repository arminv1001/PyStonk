from controller.BacktestController import *

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
import os
import datetime





def run_backtest_viewer():

    st.title("Backtest Dashboard")

    bt_settings_dict = view_sidebar_settings()

    run = st.button('Run')

    controller = BacktestController(bt_settings_dict)
    master_df = controller.master_df
    spreadsheet = controller.spreadsheet
    drawdown_df = controller.drawdown_df

    print(42)
    print(drawdown_df)

    view_dashboard(bt_settings_dict, master_df)
    view_trade_history(spreadsheet.trade_history_s)
    view_equity(master_df[['Equity', 'Equity %']])
    view_drawdown(drawdown_df)
    view_spreadsheet(spreadsheet)


def view_trade_history(trade_history_df):
        st.header('Trade History')
        st.dataframe(trade_history_df, 1100, 200)


def view_equity(equity_df):
    # TO-DO: Equity Drawdown direkt untereinander
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
    dd_col.subheader('Runs')
    dd_col.dataframe(spreadsheet.runs_info)

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
    data_list = get_filenames_from('backtest_data')

    # General
    st.sidebar.header('General')
    strategy = st.sidebar.selectbox(
        'Choose your strategy', strategy_list)
    source_list = ['Source Folder', 'Yahoo Finance']
    data_source_s = st.sidebar.selectbox(
        'Select your data source', source_list, key="<symbol>")
    

    if data_source_s == 'Yahoo Finance':
        symbols = st.sidebar.text_input('Symbol')
    elif data_source_s == 'Source Folder':
        symbols_csv = st.sidebar.multiselect('Symbol', data_list)
        symbols = [symbol.replace('.csv', '') for symbol in symbols_csv]

    data_source_b = st.sidebar.selectbox(
        'Select your data source', source_list, key="<benchmark>")

    if data_source_b == 'Yahoo Finance':
        benchmark = st.sidebar.text_input('Symbol')
    elif data_source_b == 'Source Folder':
        benchmark_csv = st.sidebar.multiselect('Benchmark', data_list)
        benchmark = [symbol.replace('.csv', '') for symbol in benchmark_csv]

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
    rfr = st.sidebar.number_input('Risk-Free Rate') / 100 # in %

    bt_settings_dict = {
        'strategy': strategy,
        'data_source_s': data_source_s,
        'data_source_b': data_source_b,
        'symbols': symbols,
        'benchmark': benchmark,
        'start_date_time': start_date if periodicity == 'Daily' else datetime.datetime.combine(start_date, start_time),
        'end_date_time': end_date if periodicity == 'Daily' else datetime.datetime.combine(end_date, end_time),
        'periodicity': periodicity,
        'start_capital': start_capital,
        'size': size,
        'comission': comission,
        'risk-free rate': rfr
    }

    return bt_settings_dict

