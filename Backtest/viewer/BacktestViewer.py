from controller.BacktestController import *

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from tools.toolbox import *
from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
import os
import datetime

def run_backtest_viewer():
    """
    Main function to create the streamlit gui
    """

    st.title("Backtest Dashboard")

    bt_settings_dict = view_sidebar_settings()

    run = st.button('Run')

    controller = BacktestController(bt_settings_dict)
    master_df = controller.master_df
    equity_df = controller.equity_df
    spreadsheet = controller.spreadsheet
    drawdown_df = controller.drawdown_df

    view_dashboard(bt_settings_dict, master_df)
    view_trade_history(spreadsheet.trade_history)
    view_charts(equity_df, drawdown_df, master_df['Position'])
    view_spreadsheet(spreadsheet)


def view_trade_history(trade_history_df):
    """
    Displays trade history dataframe

    Args:
        trade_history_df (pd DataFrame): trade history df
    """
    st.header('Trade History')
    trade_history_df = trade_history_df.style.applymap(
        color_win_loss, subset=['Return', 'Return %']).highlight_max(
        color='lightgreen', axis=0).highlight_min(color='#cd4f39', axis=0)
    st.dataframe(trade_history_df, 1100, 200)


def view_charts(equity_df, drawdown_df, position_df):
    """
    Displays equity and drawdown charts

    Args:
        equity_df (pd DataFrame): equity df
        drawdown_df (pd DataFrame): drawdown df
        position_df (pd DataFrame: position df
    """

    st.header('Charts')

    view_equity(equity_df, position_df)
    view_drawdown(drawdown_df, position_df)
    
def view_equity(equity_df, position_df):
    """
    Displays equity information

    Args:
        equity_df (pd DataFrame): equity df
        position_df (pd DataFrame): position df
    """
    equity_rad = st.radio(
        '', ['percentage %', 'absolute', 'log10 percentage %', 'log10absolute'], key="<equity_rad>")

    if equity_rad == 'absolute':
        print(1)
        equity_data = equity_df['Equity'][position_df < 0]
        benchmark_data = equity_df['Benchmark'][position_df < 0]
    elif equity_rad == 'percentage %':
        print(2)
        equity_data = equity_df['Equity %'][position_df < 0]
        benchmark_data = equity_df['Benchmark %'][position_df < 0]
    elif equity_rad == 'log10 percentage %':
        print(3)
        equity_data = equity_df['log Equity %'][position_df < 0]
        benchmark_data = equity_df['log Benchmark %'][position_df < 0]
    elif equity_rad == 'log10 absolute':
        print(4)
        equity_data = equity_df['log Equity'][position_df < 0]
        benchmark_data = equity_df['log Benchmark'][position_df < 0]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=equity_data.index, 
        y=equity_data,
        name='Equity'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=equity_data.index,
            y=benchmark_data,
            name='Benchmark Performance'
        )
    )

    fig.layout.update(title_text='Equity',
                        xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)



def view_drawdown(drawdown_df, position_df):
    """
    Displays drawdown information

    Args:
        drawdown_df (pd DataFrame): drawdown df
        position_df (pd DataFrame): position df
    """
    

    """ dd_rad = st.radio('', ['absolute', 'percentage %'], key="<dd_rad>")
    if dd_rad == 'absolute':
        drawdown_data = drawdown_df['Drawdown'][position_df < 0]
    elif dd_rad == 'percentage %':
        drawdown_data = drawdown_df['Drawdown %'][position_df < 0] """

    drawdown_data = drawdown_df['Drawdown %'][position_df < 0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown_data.index, y=drawdown_data, name='Drawdown'))
    fig.layout.update(
        title_text='Drawdown', 
        xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


def view_spreadsheet(spreadsheet):
    """
    Displays spreadsheet information

    Args:
        spreadsheet_df (pd DataFrame): spreadsheet df
        position_df (pd DataFrame): position df
    """

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
    """
    Display dashboard with generel information about strategy and stock

    Args:
        bt_settings_dict (dict):  backtest settings
        master_df (pd DataFrame): master df
    """
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
    """
    Display sidebar menu for backtest settings

    Returns:
        dict: backtest settings
    """

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

