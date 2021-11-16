from _typeshed import Self
import sched
import time
import datetime
from TradingSystem import TradingSystem
class LiveTradingSytem:
    def __init__(self,TradingSystems:list):
        self.__trading_systems = TradingSystems
    @staticmethod
    def startScheduler(timeFrame:int, scheduler:sched, tradingSystem:TradingSystem, weekend_trading=False):
        if (not weekend_trading) and datetime.datetime.today().weekday() >=  5:
            now = datetime.datetime.now()
            if now.hours == 23:
                if now.minute <= 50:
                    time.sleep((now.minute - 1) * 60)
                else:
                    print("System startet gleich")
                    ## System wird gleich starten
            else: 
                time.sleep((24-now.hours-1) * 60*60)
        elif (datetime.datetime.today().weekday() < 5) or weekend_trading:
            now = datetime.datetime.now()
            scheduler.enter(((((timeFrame-(now.minute % timeFrame))-1) * 60) + (60-now.second)), 1, tradingSystem.checkSignal, ())
        

    def main(self):
        scheduler = sched.scheduler(time.time, time.sleep)
        while(1):
            for trading_system in self.__trading_systems:
                trading_system.checkSignal()