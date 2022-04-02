import sched
import time
import datetime
from TradingSystems.TradingSystem import TradingSystem
from typing import List
class LiveTradingSytem:
    def __init__(self,TradingSystems:List[TradingSystem]):
        self.__trading_systems = TradingSystems

    scheduler = sched.scheduler(time.time, time.sleep)

    @staticmethod
    def startScheduler(tradingSystem:TradingSystem):
        if (not tradingSystem.getWeekendTrading()) and datetime.datetime.today().weekday() >=  5:
            now = datetime.datetime.now()
            if now.hours == 23:
                if now.minute <= 50:
                    time.sleep((now.minute - 1) * 60)
                else:
                    print("System startet gleich")
                    ## System wird gleich starten
            else: 
                time.sleep((24-now.hours-1) * 60*60)
        elif (datetime.datetime.today().weekday() < 5) or tradingSystem.getWeekendTrading():
            now = datetime.datetime.now()
            LiveTradingSytem.scheduler.enter(((((tradingSystem.getTimeFrame()-(now.minute % tradingSystem.getTimeFrame()))-1) * 60) + (60-now.second)), 1, tradingSystem.checkSignal, ())
        
    def main(self):
        for trading_system in self.__trading_systems:
            LiveTradingSytem.startScheduler(trading_system,trading_system.getWeekendTrading())
        LiveTradingSytem.scheduler.run()