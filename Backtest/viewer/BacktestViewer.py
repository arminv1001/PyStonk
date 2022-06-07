from model.BacktestModel import *
from exporter.Exporter import *
from optimizer.Optimizer import *
from tools.toolbox import *
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

from plotly.subplots import make_subplots
import numpy as np
import streamlit as st
import os
from datetime import datetime

STRATEGY_LIST = ['Moving_Average', 'ML_reg_Bitcoin','ML_class_reg_Bitcoin']
SPREADSHEET_INFOS = {
    'General': ['Initial Capital', 'Ending Capital', 'Net Profit', 'Net Profit %', 'Ratio Longs', 'Transaction Costs'],
    'Performance': ['Exposure %', 'Sharpe Ratio', 'Sortino Ratio', 'M&M Ratio: RAP', 'M&M Ratio: rm', 'Alpha', 'Beta', 'CAGR %', 'MAR', 'Calmar'],
    'All Trades': ['Avg. PnL', 'Avg. PnL %', 'Avg. Bars Held'],
    'Winners': ['Total Profit', 'Avg. Profit %', 'Avg, Bars Held', 'Max. Consecutive', 'Largest Win', 'Bars in Largest Win'],
    'Losers': ['Total Loss', 'Avg. Loss %', 'Avg, Bars Held', 'Max. Consecutive', 'Largest Loss', 'Bars in Largest Loss'],
    'Runs Info': ['HHI on positives', 'HHI on negatives', 'Max DD %', 'Max DD in Bars']
}
DATABASE_INFO = {
    'master_df': ['Timestamp', 'Open' , 'High' , 'Close' , 'Low' , 'Volume' , 'Turnover', 'Dividend', 'Unadjusted Close', 'Signal'],
    'equity': ['Timestamp', 'Equity', 'Equity %', 'log Equity', 'log Equity %', 'Benchmark', 'Benchmark %', 'log Benchmark', 'log Benchmark %'],
    'trade_history': ['Start Date', 'End Date', 'Buy Price', 'Sell Price', 'Return', 'Return %', 'Bars Held', 'Size'],
    'drawdown': ['Timestamp', 'Drawdown', 'Drawdown %'],

    'general_info': ['Metric', 'Data'],
    'performance_info': ['Metric', 'Data'],
    'all_trades_info': ['Metric', 'Data'],
    'winners': ['Metric', 'Data'],
    'losers': ['Metric', 'Data'],
    'runs_info': ['Metric', 'Data']
}
SOURCE_LIST = ['.csv', 'Yahoo Finance']

def run_backtest_viewer():
    """
    Main function to create the streamlit gui
    """

    st.title("Backtest Dashboard")

    return_list = view_sidebar_settings()

    if return_list[0]:
        database_name = return_list[1]

        view_dashboard(database_name)
        view_trade_history(database_name)
        view_charts(database_name)
        view_spreadsheet(database_name)
        # view_optimizer(optimizer)



def view_optimizer(optimizer):
    # TO-DO: Finish Optimizer
    """
    Displays Optimizer Chart

    Args:
        optimizer (_type_): _description_
    """

    st.header('Charts')

    info_type_field, info_key_field = st.columns(2)

    info_type_list = SPREADSHEET_INFOS.keys()
    info_type = info_type_field.selectbox('Performance Type', info_type_list, key="<perf_type>")

    info_key_list = SPREADSHEET_INFOS[info_type]
    info_key = info_key_field.selectbox('Performance Metric', info_key_list, key="<perf_met>")

    x_data = optimizer.parameters
    y_data = optimizer.get_info(info_type, info_key)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        name='Optimizer'))
    fig.layout.update(
        title_text='Optimizer',
        xaxis_title="Parameter",
        yaxis_title=info_key,
        xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)



def view_trade_history(database_name):
    """
    Displays trade history dataframe
    Args:
        trade_history_df (pd DataFrame): trade history df
    """

    st.header('Trade History')

    df = get_df_from_database(database_name, 'trade_history')

    df = df.style.applymap(
        color_win_loss, subset=['Return', 'Return %']).highlight_max(
        color='lightgreen', axis=0).highlight_min(color='#cd4f39', axis=0)
    st.dataframe(df, 1100, 200)


def view_charts(database_name):
    """
    Displays equity and drawdown charts
    Args:
        equity_df (pd DataFrame): equity df
        drawdown_df (pd DataFrame): drawdown df
        signal_df (pd DataFrame: position df
    """

    st.header('Charts')

    view_equity(database_name)
    view_drawdown(database_name)

def view_equity(database_name):
    """
    Displays equity information
    Args:
        equity_df (pd DataFrame): equity df
        signal_df (pd DataFrame): position df
    """
    st.subheader('Equity')

    equity_df = get_df_from_database(database_name, 'equity')

    signal_df = get_df_from_database(database_name, 'master_df', ['Timestamp', 'Signal'])

    equity_rad = st.radio(
        '', ['percentage %', 'absolute', 'log10 percentage %', 'log10 absolute'], key="<equity_rad>")

    if equity_rad == 'absolute':
        name = 'Equity'
        equity_data = equity_df['Equity'][signal_df['Signal'] < 0]
        benchmark_data = equity_df['Benchmark'][signal_df['Signal'] < 0]
    elif equity_rad == 'percentage %':
        name = 'Equity %'
        equity_data = equity_df['Equity %'][signal_df['Signal'] < 0]
        benchmark_data = equity_df['Benchmark %'][signal_df['Signal'] < 0]
    elif equity_rad == 'log10 percentage %':
        name = 'log Equity %'
        equity_data = equity_df['log Equity %'][signal_df['Signal'] < 0]
        benchmark_data = equity_df['log Benchmark %'][signal_df['Signal'] < 0]
    elif equity_rad == 'log10 absolute':
        name ='log Equity'
        equity_data = equity_df['log Equity'][signal_df['Signal'] < 0]
        benchmark_data = equity_df['log Benchmark'][signal_df['Signal'] < 0]

    print(equity_data)


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

    fig.layout.update(title_text=name,
                        xaxis_rangeslider_visible=True,
                        showlegend=False
                        )

    st.plotly_chart(fig)



def view_drawdown(database_name):
    """
    Displays drawdown information
    Args:
        drawdown_df (pd DataFrame): drawdown df
        signal_df (pd DataFrame): position df
    """


    """ dd_rad = st.radio('', ['absolute', 'percentage %'], key="<dd_rad>")
    if dd_rad == 'absolute':
        drawdown_data = drawdown_df['Drawdown'][signal_df < 0]
    elif dd_rad == 'percentage %':
        drawdown_data = drawdown_df['Drawdown %'][signal_df < 0] """

    st.subheader('Drawdown')

    drawdown_df = get_df_from_database(database_name, 'drawdown')
    signal_df = get_df_from_database(database_name, 'master_df', ['Timestamp', 'Signal'])

    drawdown_data = drawdown_df['Drawdown %'][signal_df['Signal'] < 0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown_data.index, y=drawdown_data, name='Drawdown'))
    fig.layout.update(
        title_text='Drawdown',
        xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)


def view_spreadsheet(database_name):
    """
    Displays spreadsheet information
    Args:
        spreadsheet_df (pd DataFrame): spreadsheet df
        signal_df (pd DataFrame): position df
    """

    st.header('SpreadSheet')

    general_info = get_df_from_database(database_name, 'general_info')
    performance = get_df_from_database(database_name, 'performance_info')
    all_trades = get_df_from_database(database_name, 'all_trades_info')
    winners = get_df_from_database(database_name, 'winners')
    losers = get_df_from_database(database_name, 'losers')
    runs_info = get_df_from_database(database_name, 'runs_info')

    gen_info_col, perf_col = st.columns(2)
    gen_info_col.subheader('General Information')
    perf_col.subheader('Performance')
    gen_info_col.dataframe(general_info)

    perf_col.dataframe(performance)

    all_trades_col, dd_col = st.columns(2)
    all_trades_col.subheader('All Trades')
    all_trades_col.dataframe(all_trades)
    dd_col.subheader('Runs')
    dd_col.dataframe(runs_info)

    winner_col, loser_col = st.columns(2)
    winner_col.subheader('Winners')
    winner_col.dataframe(winners)
    loser_col.subheader('Losers')
    loser_col.dataframe(losers)


def view_dashboard(database_name):
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

    df = get_df_from_database(database_name, 'master_df')

    if (chart_type == 'OHLC'):
        # Plot OHLC on 1st row
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                     low=df['Low'], close=df['Close'], name="OHLC"), row=1, col=1)
    elif (chart_type == 'Close'):
        # Plot Close on 1st row

        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'], name="Close Price"), row=1, col=1)

    # Bar trace for volumes on 2nd row without legend
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'],
                         showlegend=True, name="Volume"), row=2, col=1)

    fig.add_trace(
        go.Scatter(
            mode='markers',
            x=df['Close'][df['Signal'] == -1].index,
            y=df['Close'][df['Signal'] == -1],
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
            x=df['Close'][df['Signal'] == 1].index,
            y=df['Close'][df['Signal'] == 1],
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

    # General
    st.sidebar.header('Trading System')
    strategy = st.sidebar.selectbox(
        'Choose your strategy', STRATEGY_LIST)
    SOURCE_LIST = ['.csv', 'Yahoo Finance']
    data_source_s = st.sidebar.selectbox(
        'Select your System Data Source', SOURCE_LIST, key="<symbol>")
    data_source_b = None
    benchmark = None


    if data_source_s == 'Yahoo Finance':
        symbols = st.sidebar.text_input('System Symbol', key="<ds_s>")
    elif data_source_s == '.csv':
        #symbols_csv = st.sidebar.multiselect('Symbol', data_list)
        #symbols = [symbol.replace('.csv', '') for symbol in symbols_csv]
        symbols = st.sidebar.text_input('System Symbol', key="<ds_s>")

    st.sidebar.header('Benchmark')
    benchmark_active = st.sidebar.checkbox('Active')

    if benchmark_active:

        data_source_b = st.sidebar.selectbox(
            'Select your Benchmark Data Source', SOURCE_LIST, key="<benchmark>")

        if data_source_b == 'Yahoo Finance':
            benchmark = st.sidebar.text_input('Benchmark Symbol', key="<ds_b>")
        elif data_source_b == '.csv':
            #benchmark_csv = st.sidebar.multiselect('Benchmark', data_list)
            #benchmark = [symbol.replace('.csv', '') for symbol in benchmark_csv]
            benchmark = st.sidebar.text_input('Benchmark Symbol', key="<ds_b>")

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

    # Optimizer
    st.sidebar.header('Optimizer')
    opt_checkbox = st.sidebar.checkbox('Activate')
    opt_start = st.sidebar.number_input('(Start) Parameter')
    if opt_checkbox:
        opt_end = st.sidebar.number_input('End Parameter')
        opt_steps = st.sidebar.number_input('Steps')
    else:
        opt_end = None
        opt_steps = None

    data_list = get_filenames_from('backtest_data')

    # Database name
    # datetime object containing current date and time
    now = datetime.now()
    # dd/mm/YY H:M:S
    creation_date = now.strftime("%d_%m_%Y_%H_%M_%S")

    database_name = 'btdb_' + strategy + '_' + creation_date

    bt_settings_dict = {
        # General
        'database_name': database_name,
        'strategy': strategy,
        'data_source_s': data_source_s,
        'data_source_b': data_source_b,
        'symbols': symbols,
        'benchmark_active': benchmark_active,
        'benchmark': benchmark,
        # Date & Time
        'start_date_time': start_date if periodicity == 'Daily' else datetime.combine(start_date, start_time),
        'end_date_time': end_date if periodicity == 'Daily' else datetime.combine(end_date, end_time),
        'periodicity': periodicity,
        # Cash & Co.
        'start_capital': start_capital,
        'size': size,
        'comission': comission,
        'risk-free rate': rfr,
        # Optimizer
        'opt_checkbox': opt_checkbox,
        'opt_start': opt_start,
        'opt_end': opt_end,
        'opt_steps': opt_steps

    }

    # Run Backtest
    st.sidebar.header('Confirm Configuration')

    database_name = None

    run_bt = st.sidebar.button('Run Backtest')
    run_bt_opt = st.sidebar.button('Run Backtest with Optimizer')

    if run_bt:

        bt_settings_dict['parameter'] = bt_settings_dict['opt_start']

        BacktestModel(bt_settings_dict)

        st.header('Backtest finished')
        st.balloons()

    elif run_bt_opt:
        # TO-DO: Finish Optimizer
        optimizer = Optimizer(bt_settings_dict)

        parameter = st.select_slider('Runs', optimizer.parameters)

        models = optimizer.models
        model = models[parameter]

        st.header('Backtest with Optimizer finished')
        st.balloons()

        return [True, database_name]

    
    # Visualize Results
    st.sidebar.header('Visualize Results')

    dir = os.path.join(os.path.abspath(os.curdir), 'export/database')

    database_name = None

    backtest_list = [f for f in listdir(dir) if isfile(join(dir, f)) and f.startswith("btdb")]
    database_name = st.sidebar.selectbox('Available Backtests', backtest_list, key="<hjgjhg>")
    
    show_bool = st.sidebar.button('Show')
    export_bool = st.sidebar.button('Export')

    if show_bool:

        return [True, database_name]
    
    elif export_bool:

        exporter = Exporter(database_name, benchmark_active)
        exporter.create_exports()
        st.header('Backtest Export finished')
        st.balloons()

    return [False, database_name]
