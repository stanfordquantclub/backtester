from src.options import *
from src.logs import Logs
from src.order import Order
from src.backtesttime import BacktestTime
from src.portfolio import Portfolio
import pandas_market_calendars as mcal
import pytz
import glob
import pandas as pd
from itertools import islice
from collections import OrderedDict
import os
import statistics
import time as execution_time
import statistics
from datetime import date, datetime, time, timedelta

class Engine:
    def initialize_defaults(self, security_name: str=None, cash: float=None, portfolio: Portfolio=None, start_date:date=None, end_date:date=None, path_dates=None, timezone="US/Eastern", root_path="/srv/sqc/data/"):
        """
        Initialize the defaults for the engine

        Args:
            security_name (str): name of the security to backtest
            cash (float): amount of cash to start with
            portfolio (Portfolio): portfolio to use for the backtest
            start_date (date): start date of the backtest
            end_date (date): end date of the backtest
            path_dates (list[str]): list of paths to use for the backtest - if this is used, start_date and end_date are ignored
            timezone (str): timezone to use for the backtest
            root_path (str): root path to use for the backtest - must be absolute path
        """
        print("Initialize Defaults")

        self.cash = cash

        self.time = BacktestTime(None, None, None)
        self.schedule = []
        self.portfolio = portfolio
        self.security_name = security_name

        self.start_date = start_date
        self.end_date = end_date
        self.path_dates = path_dates

        self.root_path = root_path
        self.timezone = timezone
        self.logs = Logs()
        self.order_id = 1

        #[[trading_day_1 {file_name: [trade_1 [buy [price, number_of_contracts], sell [price, number_of_contracts] ] ] , file_name}], [trading_day_2 {}], ]

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
    
    def initialize_after(self):
        """
        Further initialization after the engine is initialized from user method, using variables that the
        user set in the initialize method.
        """
        
        # Create the portfolio
        self.portfolio = Portfolio(self.cash, self.time)
        
        # Create the schedule
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(self.start_date, self.end_date)
        schedule["market_open"] = schedule["market_open"].dt.tz_convert(pytz.timezone(self.timezone))
        schedule["market_close"] = schedule["market_close"].dt.tz_convert(pytz.timezone(self.timezone))

        for day, (open_date, close_date) in schedule.iterrows():
            self.schedule.append([open_date, close_date])

    def get_time(self):
        return self.time.time
    
    def get_date(self):
        return self.time.time.date()

    def get_open_time(self):
        return self.time.open_time

    def get_close_time(self):
        return self.time.close_time

    def get_seconds_elapsed(self):
        return self.time.seconds_elapsed

    def get_underlying(self):
        if self.start_date and self.end_date:
            underlying_assets = OrderedDict()
            
            for open_date, close_date in self.schedule:
                underlying_path = f"{self.root_path}client-2378-luke-eq-taq/{open_date.year}/{open_date.strftime('%Y%m%d')}/{self.security_name[0]}/Candles.{self.security_name}.csv"
                
                underlying_assets[open_date] = UnderlyingAsset(self.security_name, underlying_path, open_date, self.time)

            return underlying_assets    
        
    def get_chains(self, underlying_assets):
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

            for open_date, close_date in self.schedule:
                # All the expirations within the day
                data_path = f"{self.root_path}us-options-tanq/us-options-tanq-{open_date.year}/{open_date.strftime('%Y%m%d')}/{self.security_name[0]}/{self.security_name}/*"
                expirations = glob.glob(data_path)
                underlying_asset = underlying_assets[open_date]

                # Put it in array format to expand to multiple assets later
                option_chains[open_date] = [DailyOptionChain(self.security_name, expirations, underlying_asset, open_date, self.time)]

            return option_chains
    
    def buy(self, contract:OptionContract, quantity:int):
        price = contract.get_adjusted_ask(quantity)

         #insufficient funds to execute given trade
        if (price > self.portfolio.cash_amount()):
            return None

        #adding trade to log
        new_trade = Order(contract, 1, quantity, price, self.order_id)
        self.logs.add_ordered(new_trade)

        self.order_id += 1

        #add trade to portfolio
        self.portfolio.add_asset(contract, price, quantity)


    def sell(self, contract:OptionContract, quantity:int):
        price = contract.get_adjusted_bid(quantity)

        if (self.portfolio.valid_sell(contract, quantity) == False):
            return None

        new_trade = Order(contract, 2, quantity, price, self.order_id)
        self.logs.add_ordered(new_trade)

        self.order_id += 1

        self.portfolio.remove_asset(contract, price, quantity)

    def total_return(self):
        """
        Gets the total return on the portfolio
        """
        self.total_return = ((self.portfolio.cash_mount() - self.cash)/ self.cash) * 100

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

    def back_test(self):
        self.initialize_defaults() # initializes fields
        self.initialize() # user defined
        self.initialize_after() # uses user defined variables

        underlying_assets = self.get_underlying()
        options_chains = self.get_chains(underlying_assets)

        t1 = execution_time.time()

        for open_date, close_date in self.schedule:
            # Iterates through each day in the schedule
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

            # Iterate through each second in the day
            while self.get_time() <= close_date:
                self.on_data(data)

                self.time.increment()

        print("Execution Time: ", execution_time.time() - t1)
        
    def on_data(self, data: Slice):
        """
        Method is to be overriden by subclass

        Args:
            data (Slice): data slice of the csv data
        """
        pass
