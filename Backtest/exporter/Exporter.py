from os import listdir
from os.path import isfile, join
from tools.toolbox import *

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import dataframe_image as dfi

from plotly.subplots import make_subplots
import numpy as np

class Exporter(object):
    """
    TradeHistory contains all information about all trades of strategy

    """

    def __init__(self, database_name, benchmark_active):
        self.__database_name = database_name
        self.__benchmark_active = benchmark_active
        self.__dir = os.path.abspath(os.curdir) + '/export' +  '/' + self.__database_name
        os.makedirs(self.__dir)


    def create_exports(self):
        self.__create_dashboard()
        self.__create_trade_history()
        self.__create_charts()
        self.__create_spreadsheet()

    def __create_spreadsheet(self):

        dir_temp = self.__dir + '/spreadsheet'
        os.makedirs(dir_temp)
        
        general_info = get_df_from_database(self.__database_name, 'general_info')
        general_info.to_csv(dir_temp + '/general_info.csv')  
        dir_temp1 = dir_temp + '/general_info.png'
        dfi.export(general_info, dir_temp1)

        performance = get_df_from_database(self.__database_name, 'performance_info')
        performance.to_csv(dir_temp + '/performance_info.csv')  
        dir_temp1 = dir_temp + '/performance_info.png'
        dfi.export(performance, dir_temp1)

        all_trades = get_df_from_database(self.__database_name, 'all_trades_info')
        all_trades.to_csv(dir_temp + '/all_trades_info.csv')  
        dir_temp1 = dir_temp + '/all_trades_info.png'
        dfi.export(all_trades, dir_temp1)

        winners = get_df_from_database(self.__database_name, 'winners')
        winners.to_csv(dir_temp + '/winners.csv')  
        dir_temp1 = dir_temp + '/winners.png'
        dfi.export(winners, dir_temp1)

        losers = get_df_from_database(self.__database_name, 'losers')
        losers.to_csv(dir_temp + '/losers.csv')  
        dir_temp1 = dir_temp + '/losers.png'
        dfi.export(losers, dir_temp1)

        runs_info = get_df_from_database(self.__database_name, 'runs_info')
        runs_info.to_csv(dir_temp + '/runs_info.csv')  
        dir_temp1 = dir_temp + '/runs_info.png'
        dfi.export(runs_info, dir_temp1)

    def __create_charts(self):

        self.__create_equity()
        self.__create_drawdown()

    def __create_equity(self):

        dir_temp = self.__dir + '/equity'

        os.makedirs(dir_temp)

        equity_df = get_df_from_database(self.__database_name, 'equity')

        signal_df = get_df_from_database(self.__database_name, 'master_df', ['Timestamp', 'Signal'])

        equity_data = equity_df['Equity'][signal_df['Signal'] < 0]
        equity_pct_data = equity_df['Equity %'][signal_df['Signal'] < 0]
        equity_log_data = equity_df['log Equity'][signal_df['Signal'] < 0]
        equity_log_pct_data = equity_df['log Equity %'][signal_df['Signal'] < 0]
        

        if self.__benchmark_active:
            benchmark_data = equity_df['Benchmark'][signal_df['Signal'] < 0]
            benchmark_pct_data = equity_df['Benchmark %'][signal_df['Signal'] < 0]
            benchmark_log_data = equity_df['log Benchmark'][signal_df['Signal'] < 0]
            benchmark_log_pct_data = equity_df['log Benchmark %'][signal_df['Signal'] < 0]


        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_data.index,
            y=equity_data,
            name='Equity'
            )
        )

        if self.__benchmark_active:
            fig.add_trace(
                go.Scatter(
                    x=equity_df.index,
                    y=benchmark_data,
                    name='Benchmark Performance'
                )
            )

        fig.layout.update(title_text='Equity',
                            xaxis_rangeslider_visible=True)

        fig.write_html(dir_temp + "/equity.html")
        fig.write_image(dir_temp + "/equity.png")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_pct_data.index,
            y=equity_pct_data,
            name='Equity'
            )
        )

        if self.__benchmark_active:
            fig.add_trace(
                go.Scatter(
                    x=equity_df.index,
                    y=benchmark_pct_data,
                    name='Benchmark Performance'
                )
            )

        fig.layout.update(title_text='Equity %',
                            xaxis_rangeslider_visible=True)

        fig.write_html(dir_temp + "/equity_pct.html")
        fig.write_image(dir_temp + "/equity_pct.png")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_log_data.index,
            y=equity_log_data,
            name='Equity'
            )
        )

        if self.__benchmark_active:
            fig.add_trace(
                go.Scatter(
                    x=equity_df.index,
                    y=benchmark_log_data,
                    name='Benchmark Performance'
                )
            )

        fig.layout.update(title_text='log Equity',
                            xaxis_rangeslider_visible=True)

        fig.write_html(dir_temp + "/equity_log.html")
        fig.write_image(dir_temp + "/equity_log.png")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=equity_log_pct_data.index,
            y=equity_log_pct_data,
            name='Equity'
            )
        )

        if self.__benchmark_active:
            fig.add_trace(
                go.Scatter(
                    x=equity_df.index,
                    y=benchmark_log_pct_data,
                    name='Benchmark Performance'
                )
            )

        fig.layout.update(title_text='log Equity %',
                            xaxis_rangeslider_visible=True)

        fig.write_html(dir_temp + "/equity_log_pct.html")
        fig.write_image(dir_temp + "/equity_log_pct.png")


    def __create_drawdown(self):
        drawdown_df = get_df_from_database(self.__database_name, 'drawdown')
        signal_df = get_df_from_database(self.__database_name, 'master_df', ['Timestamp', 'Signal'])

        drawdown_data = drawdown_df['Drawdown %'][signal_df['Signal'] < 0]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=drawdown_data.index, y=drawdown_data, name='Drawdown'))
        fig.layout.update(
            title_text='Drawdown',
            xaxis_rangeslider_visible=True)

        fig.write_html(self.__dir + "/drawdown.html")
        fig.write_image(self.__dir + "/drawdown.png")

    def __create_trade_history(self):
        df = get_df_from_database(self.__database_name, 'trade_history')
        df.to_csv(self.__dir + '/trade_history.csv') 

        df = df.style.applymap(
            color_win_loss, subset=['Return', 'Return %']).highlight_max(
            color='lightgreen', axis=0).highlight_min(color='#cd4f39', axis=0)

        
        #dir_temp = self.__dir + '/trade_history.png'

        #dfi.export(df, dir_temp)

    def __create_dashboard(self, chart_type='OHLC'):
        

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, subplot_titles=(chart_type, 'Volume'),
                        row_width=[0.2, 0.7])

        df = get_df_from_database(self.__database_name, 'master_df')

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

        fig.write_html(self.__dir + "/dashboard.html")
        fig.write_image(self.__dir + "/dashboard.png")