from src.options import *
from src.resolution import *
from src.logs import Logs
from src.order import Order
from src.backtest_time import BacktestTime
from src.portfolio import Portfolio
from src.data_slice import Slice
import pandas_market_calendars as mcal
import pytz
import glob
import pandas as pd
from collections import OrderedDict
import os
import sys
import statistics
import time as execution_time
import statistics
import multiprocessing
from datetime import date, datetime, time, timedelta
from contextlib import redirect_stdout
from io import StringIO

def run_process(engine, open_date, close_date):
    """
    Function to run the day in a process. Needs to be outside of the class so that it can be pickled and run in a process.
    
    """
    
    engine.output = None
    engine.run_day(open_date, close_date)
    return engine.output
        
class Engine:
    def initialize_defaults(self, cash: float=None, portfolio: Portfolio=None, start_date:date=None, end_date:date=None, resolution=Resolution.Second, path_dates=None, timezone="US/Eastern", root_path="/srv/sqc/data/", parallel=False):
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
            parallel (bool): whether to use parallel processing for the backtest (running multiple days at once) - this may be usefull for collecting statistics
                Running in parallel uses multiprocessing, which copies the engine and runs it in a separate process. This means that there is no memory shared between the processes.
                days. You may save outputs on on_data() by setting self.output. When all the days stop running, back_test() will return a dictionary of the outputs for each day.
        """

        self.cash = cash

        self.schedule = []
        self.portfolio = portfolio
        self.security_names = []
        self.resolution = resolution

        self.start_date = start_date
        self.end_date = end_date
        self.path_dates = path_dates

        self.root_path = root_path
        self.timezone = timezone
        self.logs = Logs()
        self.order_id = 1
        
        self.parallel = parallel
        self.num_processes = 6

        #[[trading_day_1 {file_name: [trade_1 [buy [price, number_of_contracts], sell [price, number_of_contracts] ] ] , file_name}], [trading_day_2 {}], ]

        self.trades = []
        self.sharpe_ratio = 1
        self.sortino_ratio = 1
        self.total_return = 0

    def initialize(self):
        """
        Method is to be overriden by subclass
        """
        pass
    
    def initialize_after(self):
        """
        Further initialization after the engine is initialized from user method, using variables that the
        user set in the initialize method.
        """
        
        # Create the time
        self.time = BacktestTime(None, None, None, self.resolution)
        
        # Create the portfolio
        self.portfolio = Portfolio(self.cash, self.time)
        
        # Create the schedule
        nyse = mcal.get_calendar('NYSE')
        schedule = nyse.schedule(self.start_date, self.end_date)
        schedule["market_open"] = schedule["market_open"].dt.tz_convert(pytz.timezone(self.timezone))
        schedule["market_close"] = schedule["market_close"].dt.tz_convert(pytz.timezone(self.timezone))

        for day, (open_date, close_date) in schedule.iterrows():
            self.schedule.append([open_date, close_date])
            
    def add_security(self, security_name):
        self.security_names.append(security_name)

    def get_time(self):
        return self.time.time
    
    def get_date(self):
        return self.time.time.date()

    def get_open_time(self):
        return self.time.open_time

    def get_close_time(self):
        return self.time.close_time

    def get_time_elapsed(self):
        return self.time.time_elapsed

    def get_underlying(self, time=None):
        if time is None:
            time = self.time
        
        if self.start_date and self.end_date:
            underlying_assets = OrderedDict()
            
            for open_date, close_date in self.schedule:
                for security_name in self.security_names:
                    underlying_path = f"client-2378-luke-eq-taq/{open_date.year}/{open_date.strftime('%Y%m%d')}/{security_name[0]}/Candles.{security_name}.csv"
                    underlying_path = os.path.join(self.root_path, underlying_path)
                    
                    underlying_assets[(open_date, security_name)] = UnderlyingAsset(security_name, underlying_path, open_date, time)

            return underlying_assets    
        
    def get_chains(self, underlying_assets, time=None):
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
        
        if time is None:
            time = self.time
            
        if self.start_date and self.end_date:
            option_chains = OrderedDict()

            for open_date, close_date in self.schedule:
                for security_name in self.security_names:
                    # All the expirations within the day
                    data_path = f"us-options-tanq/us-options-tanq-{open_date.year}/{open_date.strftime('%Y%m%d')}/{security_name[0]}/{security_name}/*"
                    data_path = os.path.join(self.root_path, data_path)
                    
                    expirations = glob.glob(data_path)
                    underlying_asset = underlying_assets[(open_date, security_name)]

                    option_chains[(open_date, security_name)] = DailyOptionChain(security_name, expirations, underlying_asset, open_date, time, self.resolution)

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
    
    def run_day(self, open_date, close_date):
        time = BacktestTime(None, None, None, self.resolution)
        
        if not self.parallel: # if it is parallel, then there may be multiple times running at once
            self.time = time # sets the time of the engine to the time of the day

        underlying_assets = self.get_underlying(time)
        options_chains = self.get_chains(underlying_assets, time)

        # Iterates through each day in the schedule
        open_date_convert = datetime(open_date.year, open_date.month, open_date.day, 9, 30, 1)
        
        time.set_time(pytz.timezone('America/New_York').localize(open_date_convert)) # converts to eastern time
        time.set_open_time(open_date) # sets the open time of the day
        time.set_close_time(close_date) # sets the close time of the day
        time.reset_time_elapsed() # resets seconds elapsed to 0

        data = Slice() # creates a new data slice for the day

        for security_name in self.security_names:
            # Add the underlying asset and options chain to the data slice
            underlying_asset = underlying_assets[(open_date, security_name)]
            data.add_underlying(underlying_asset)
            
            chain = options_chains[(open_date, security_name)]
            data.add_chain(chain)

        # Iterate through each second in the day
        while time.get_time() <= close_date:
            self.on_data(data, time)
            time.increment()
            
        # Remove the data from the previous day
        for security_name in self.security_names:
            underlying_assets.pop((open_date, security_name))
            options_chains.pop((open_date, security_name))

    def back_test(self):
        self.initialize_defaults() # initializes fields
        self.initialize() # user defined
        self.initialize_after() # finished initialization with user defined variables

        # Start time of the backtest
        start_time = execution_time.time()
        
        if self.parallel:
            with multiprocessing.Pool(processes=self.num_processes) as pool:
                results = []
                output = {}

                for open_date, close_date in self.schedule:
                    result = pool.apply_async(run_process, args=(self, open_date, close_date))
                    results.append((open_date, result))

                # Store the results
                for open_date, result in results:
                    output[open_date] = result.get()

                pool.close()
                pool.join()
                
                self.on_end()

                print("Execution Time: ", execution_time.time() - start_time)
                
                return output
        else:                    
            for open_date, close_date in self.schedule:
                self.run_day(open_date, close_date)
                
        # Call the on_end method
        self.on_end()

        print("Execution Time: ", execution_time.time() - start_time)

    def __str__(self):
        return f"Engine({self.security_names}, {self.cash}, {self.start_date}, {self.end_date}, {self.root_path})"

    def on_data(self, data: Slice, time: BacktestTime):
        """
        Method is to be overriden by subclass. This method is called every second of the backtest 
        and is used to pass the data to the algorithm

        Args:
            data (Slice): data slice of the csv data
        """
        pass

    def on_end(self):
        """
        Method is to be overriden by subclass. This method is called at the end of the backtest
        and can be used to calculate statistics or analyze final variables
        """
        pass
