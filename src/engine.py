import pandas_market_calendars as mcal
from datetime import date, datetime, time, timedelta
import pytz
import glob
import pandas as pd
from itertools import islice
from collections import OrderedDict
import os
import logs
import statistics
from src.options import *

class BacktestTime:
    def __init__(self, new_time:datetime) -> None:
        self.time = new_time
        self.seconds_elapsed = 0

    def set_time(self, new_time:datetime):
        self.time = new_time

    def increment(self):
        self.time += timedelta(seconds=1)
        self.seconds_elapsed += 1

    def get_time(self):
        return self.time

    def get_seconds_elapsed(self):
        return self.seconds_elapsed

    def reset_seconds_elapsed(self):
        self.seconds_elapsed = 0

class Engine:
    def initialize_defaults(self, security_name: str=None, start_cash: float=None, start_date:date=None, end_date:date=None, path_dates=None, filter_paths=None, timezone="US/Eastern", root_path="/srv/sqc/data/us-options-tanq"):
        """
        Initialize the defaults for the engine

        Args:
            security_name (str): name of the security to backtest
            start_date (date): start date of the backtest
            end_date (date): end date of the backtest
            path_dates (list[str]): list of paths to use for the backtest - if this is used, start_date and end_date are ignored
            filter (str): filter to use when generating paths within the start_date and end_date or path_dates

        """
        print("Initialize Defaults")

        self.portfolio = {}
        self.time = BacktestTime(None)
        self.schedule = []
        self.start_cash = start_cash
        self.security_name = security_name

        self.start_date = start_date
        self.end_date = end_date
        self.path_dates = path_dates

        self.filter_paths = filter_paths
        self.root_path = root_path
        self.timezone = timezone

        #[[trading_day_1 {file_name: [trade_1 [buy [price, number_of_contracts], sell [price, number_of_contracts] ] ] , file_name}], [trading_day_2 {}], ]

        self.logs = logs()
        self.trades = []
        self.sharpe_ratio = 1
        self.sortino_ratio = 1
        self.total_return = 0

    def initialize(self):
        """
        Method is to be overriden by subclass
        """
        print("Initialize Engine")
        pass

    def get_time(self):
        return self.time.time

    def get_seconds_elapsed(self):
        return self.time.seconds_elapsed

    def get_chains(self):
        """
        Get's the data paths for the backtest

        Args:
            start (date): start date of the backtest
            end (date): end date of the backtest
            paths (list[str]): list of paths to use for the backtest - if this is used, start and end are ignored

        Returns:
            list[str]: list of paths to the data
        """

        if self.path_dates:
            return self.path_dates

        if self.start_date and self.end_date:
            option_chains = OrderedDict()

            nyse = mcal.get_calendar('NYSE')

            schedule = nyse.schedule(self.start_date, self.end_date)

            schedule["market_open"] = schedule["market_open"].dt.tz_convert(pytz.timezone(self.timezone))
            schedule["market_close"] = schedule["market_close"].dt.tz_convert(pytz.timezone(self.timezone))

            for day, (open_date, close_date) in schedule.iterrows():
                self.schedule.append([open_date, close_date])
                # All the expirations within the day
                data_path = f"{self.root_path}/us-options-tanq-{open_date.year}/{open_date.strftime('%Y%m%d')}/{self.security_name[0]}/{self.security_name}/*"
                expirations = glob.glob(data_path)

                # Put it in array format to expand to multiple assets
                option_chains[open_date] = [DailyOptionChain(self.security_name, expirations, open_date, self.time)]

            return option_chains

    def on_data(self, data: Slice):
        """
        Method is to be overriden by subclass

        Args:
            data (Slice): data slice of the csv data
        """
        pass

    def back_test(self):
        self.initialize_defaults()
        self.initialize()

        options_chains = self.get_chains()

        for open_date, close_date in self.schedule:
            open_date_convert = datetime(open_date.year, open_date.month, open_date.day, 9, 30, 1)
            self.time.set_time(pytz.timezone('America/New_York').localize(open_date_convert)) # converts to eastern time
            self.time.reset_seconds_elapsed()

            chains = options_chains[open_date] # chains get redefined every day (old chains are deleted through garbage collection)
            data = Slice()

            # Iterate through each asset options chain at the current date
            for chain in chains:
                data.add_chain(chain.asset, chain)

            while self.get_time() <= close_date:
                self.on_data(data)

                self.time.increment()

     """
     gets the total return on the portfolio
     """
     def total_return(self):
         self.total_return =  ((self.current_cash - self.start_cash)/ self.start_cash) * 100

     def calculate_trades(self):
         ordered_trades = self.logs.get_trades()
         traded_contracts = list(ordered_trades.keys())



         for contract in traded_contracts:
             #the trades_made within one contract
             trades_made = ordered_trades[contract]

             ind = 0
             while (len(trades_made != 0)):
                 if (trades_made[ind].get_order_type != trades_made[ind + 1].get_order_type):
                     self.trades.append((trades_made[ind + 1].get_price_paid() - trades_made[ind].get_price_paid()) / trades_made[ind])
                     del trades_made[ind]
                     del trades_made[ind]


     def sharpe_ratio(self):
         standard_dev = statistics.stdev(self.trades)
         return self.total_return / standard_dev
