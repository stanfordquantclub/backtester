import pandas_market_calendars as mcal
from datetime import date, datetime, time, timedelta
import pytz
import glob
import pandas as pd
from itertools import islice
from collections import OrderedDict
import os
from enum import Enum

class Options:
    CALL = 0
    PUT = 1

class Slice:
    """
    This class formats row data from the csv. Used by the on_data method in 
    Engine to pass data to the strategy.
    """
    def __init__(self) -> None:
        self.chains = {}
        
    def add_chain(self, asset_name, chain):
        self.chains[asset_name] = chain
        
    def get_chain(self, asset_name):
        return self.chains[asset_name]
        
class OptionContract:
    def __init__(self, path, time) -> None:
        self.path = path
        self.time = time
        
        properties = os.path.basename(path).split(".")
        self.asset = properties[1]
        self.type = Options.CALL if properties[2][0] == "C" else Options.PUT
        self.strike = int(properties[2][1:])
        self.expiration = datetime.strptime(properties[3], '%Y%m%d').strftime('%m/%d/%Y')

    def getAskPrice(self):
        line = self.time.seconds_elapsed + 1
        with open(self.path) as f_input:
            for row in islice(f_input, line, line + 1):
                return row
    
class DailyOptionChain:
    def __init__(self, asset:str, paths: str, trade_date:date, time:date) -> None:
        self.asset = asset
        self.paths = paths # list of expirations paths
        self.trade_date = trade_date
        self.contracts = []
        self.time = time
        
    def load_contracts(self):
        for expiration_path in self.paths:
            contract_paths = glob.glob(expiration_path + "/Candles*.csv")
            
            for contract_path in contract_paths:
                contract = OptionContract(contract_path, self.time)
                self.contracts.append(contract)
        
    def get_contracts(self):
        if len(self.contracts) == 0:
            self.load_contracts()
        return self.contracts
    
class BacktestTime:
    def __init__(self, new_time:datetime) -> None:
        self.time = new_time
        self.seconds_elapsed = 0
        
    def set_time(self, new_time:datetime):
        self.time = new_time

    def increment(self):
        self.time += timedelta(seconds=1)
        self.seconds_elapsed += 1

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

    def initialize(self):
        """
        Method is to be overriden by subclass
        """
        print("Initialize Engine")
        pass

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
        
        # print(options_chains)
        
        for open_date, close_date in self.schedule:
            open_date_convert = datetime(open_date.year, open_date.month, open_date.day, 9, 30, 0, 0)
            self.time.set_time(pytz.timezone('America/New_York').localize(open_date_convert)) # converts to eastern time

            chains = options_chains[open_date]
            data = Slice()
            
            for chain in chains:
                data.add_chain(chain.asset, chain)
        
            while self.time.time <= close_date:
                self.on_data(data)
                self.time.increment()
                
        # for day in options_chains:
        #     self.time = day
        #     chains = options_chains[day]
            
        #     data = Slice()
            
        #     for chain in chains:
        #         data.add_chain(chain.asset, chain)
                
        #     self.on_data(data)
                
        # for paths in options_chains:
        #     self.time = 
        #     df = pd.read_csv(paths)
            
        #     for (idx, row) in df.iterrows():
        #         data_slice = Slice(row.index, row)
        #         self.on_data(data_slice)
