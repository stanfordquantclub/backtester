import pandas_market_calendars as mcal
from datetime import date, datetime, time, timedelta
import pytz
import glob
import pandas as pd
from itertools import islice
from collections import OrderedDict
import os
from src.options import *
import time as execution_time

class BacktestTime:
    def __init__(self, new_time:datetime, open_time:datetime, close_time:datetime) -> None:
        self.time = new_time
        self.seconds_elapsed = 0
        self.open_time = open_time
        self.close_time = close_time

    def set_time(self, new_time:datetime):
        self.time = new_time

    def set_open_time(self, open_time:datetime):
        self.open_time = open_time

    def set_close_time(self, close_time:datetime):
        self.close_time = close_time

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
        self.time = BacktestTime(None, None, None)
        self.schedule = []
        self.start_cash = start_cash
        self.security_name = security_name

        self.start_date = start_date
        self.end_date = end_date
        self.path_dates = path_dates

        self.filter_paths = filter_paths
        self.root_path = root_path
        self.timezone = timezone

    def initialize(self):
        """
        Method is to be overriden by subclass
        """
        print("Initialize Engine")
        pass

    def get_time(self):
        return self.time.time

    def get_open_time(self):
        return self.time.open_time

    def get_close_time(self):
        return self.time.close_time

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

    def buy(self, contract:OptionContract, quantity:int)->None:
        current_ask_price = contract.get_ask_min_price() * 0.75 + contract.get_ask_max_price() * 0.25

        if self.get_time() == self.get_close_time():
            next_ask_price = current_ask_price
        else:
            seconds_elapsed = self.get_seconds_elapsed()
            next_ask_price = contract.get_ask_min_price(seconds_elapsed + 1) * 0.75 + contract.get_ask_max_price(seconds_elapsed + 1) * 0.25

        price = round(max(current_ask_price, next_ask_price), 2)

        return price

    def sell(self, contract:OptionContract, quantity:int)->None:
        current_bid_price = contract.get_bid_max_price() * 0.75 + contract.get_bid_min_price() * 0.25

        if self.get_time() == self.get_close_time():
            next_bid_price = current_bid_price
        else:
            seconds_elapsed = self.get_seconds_elapsed()
            next_bid_price = contract.get_bid_max_price(seconds_elapsed + 1) * 0.75 + contract.get_bid_min_price(seconds_elapsed + 1) * 0.25

        price = round(min(current_bid_price, next_bid_price), 2)

        return price

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

        t1 = execution_time.time()

        for open_date, close_date in self.schedule:
            open_date_convert = datetime(open_date.year, open_date.month, open_date.day, 9, 30, 1)

            self.time.set_time(pytz.timezone('America/New_York').localize(open_date_convert)) # converts to eastern time
            self.time.set_open_time(open_date)
            self.time.set_close_time(close_date)
            self.time.reset_seconds_elapsed()

            chains = options_chains[open_date] # chains get redefined every day (old chains are deleted through garbage collection)
            data = Slice()

            # Iterate through each asset options chain at the current date
            for chain in chains:
                data.add_chain(chain.asset, chain)

            while self.get_time() <= close_date:
                self.on_data(data)

                self.time.increment()

        print("Execution Time: ", execution_time.time() - t1)
