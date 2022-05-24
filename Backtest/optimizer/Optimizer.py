from model.BacktestModel import *

import numpy as np
import pandas as pd

class Optimizer(object):
    """
    Optimizer runs multiple backtest with altering input parameters

    """

    def __init__(self, view_settings_dict):

        self.__settings_dict = view_settings_dict

        self.__parameters = []
        self.__general_infos = []
        self.__performance_infos = []
        self.__all_trades_infos = []
        self.__winners = []
        self.__losers = []
        self.__runs = []

        self.__models = {}

        self.__opt_start = view_settings_dict['opt_start']
        self.__opt_end = view_settings_dict['opt_end']
        self.__opt_steps = view_settings_dict['opt_steps']

        self.__run()

    @property
    def parameters(self):
        return self.__parameters

    @property
    def general_infos(self):
        # Initial Capital, Ending Capital, Net Profit, Net Profit %, Ratio Longs, Transaction Costs
        return self.__general_infos

    @property
    def all_trades_info(self):
        return self.__all_trades_info

    @property
    def winners(self):
        return self.__winners

    @property
    def losers(self):
        return self.__losers

    @property
    def runs(self):
        return self.__runs

    @property
    def models(self):
        return self.__models

    def get_info(self, info_type, info_key):

        if info_type == 'General':
            info_list = self.__general_infos

        elif info_type == 'Performance':
            info_list = self.__performance_infos

        elif info_type == 'All Trades':
            info_list = self.__all_trades_infos

        elif info_type == 'Winners':
            info_list = self.__winners

        elif info_type == 'Losers':
            info_list = self.__losers

        elif info_type == 'Runs':
            info_list = self.__runs

        infos = []
        
        for info in info_list:
            infos.append(info['Data'][info_key])

        return infos


    def __run(self):   

        parameter = self.__opt_start

        while parameter <= self.__opt_end:

            self.__settings_dict['parameter'] = parameter

            model = BacktestModel(self.__settings_dict)
            spreadsheet = model.spreadsheet

            self.__parameters.append(parameter)

            self.__general_infos.append(spreadsheet.general_info)
            self.__performance_infos.append(spreadsheet.performance_info)
            self.__all_trades_infos.append(spreadsheet.all_trades_info)
            self.__winners.append(spreadsheet.winners)
            self.__losers.append(spreadsheet.losers)
            self.__runs.append(spreadsheet.runs_info)

            self.__models[parameter] = model

            parameter += self.__opt_steps
        

