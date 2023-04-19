import pandas_market_calendars as mcal
from datetime import date, datetime, time, timedelta
import pytz
import glob
import pandas as pd
from itertools import islice
from collections import OrderedDict
import os

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
    def __init__(self, asset, contract_type, strike, expiration, path, time) -> None:
        self.asset = asset
        self.contract_type = contract_type
        self.strike = strike
        self.expiration = expiration
        self.path = path
        self.time = time
        self.df = None

    def load_df(self):
        if self.df is None:
            self.df = pd.read_csv(self.path)

    def get_data_no_df(self):
        line = self.time.seconds_elapsed + 1
        with open(self.path) as f_input:
            for row in islice(f_input, line, line + 1):
                return row
            
    def get_bid_min_price(self, seconds_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if seconds_elapsed is None:
            seconds_elapsed = self.time.seconds_elapsed
            
        return self.df.iloc[seconds_elapsed]["BidMin"]
            
    def get_bid_max_price(self, seconds_elapsed=None):
        if self.df is None:
            self.load_df()

        if seconds_elapsed is None:
            seconds_elapsed = self.time.seconds_elapsed

        return self.df.iloc[seconds_elapsed]["BidMax"]
            
    def get_ask_min_price(self, seconds_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if seconds_elapsed is None:
            seconds_elapsed = self.time.seconds_elapsed
            
        return self.df.iloc[seconds_elapsed]["AskMin"]
    
    def get_ask_max_price(self, seconds_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if seconds_elapsed is None:
            seconds_elapsed = self.time.seconds_elapsed
            
        return self.df.iloc[seconds_elapsed]["AskMax"]
    
    def get_adjusted_ask(self, quantity:int)->None:
        """
        Gets the adjusted ask price (conservative) based on the current time and the next time,
        simulating one second of latency. 

        Args:
            quantity (int): The quantity of contracts to buy.
            
        Returns:
            float: The adjusted ask price.
        """
        
        current_ask_price = self.get_ask_min_price() * 0.75 + self.get_ask_max_price() * 0.25

        if self.time.get_time() == self.time.get_close_time():
            next_ask_price = current_ask_price
        else:
            seconds_elapsed = self.get_seconds_elapsed()
            next_ask_price = self.get_ask_min_price(seconds_elapsed + 1) * 0.75 + self.get_ask_max_price(seconds_elapsed + 1) * 0.25

        price = round(max(current_ask_price, next_ask_price), 2) * quantity

        return price

    def get_adjusted_bid(self, quantity:int)->None:
        """
        Gets the adjusted bid price (conservative) based on the current time and the next time,
        simulating one second of latency. 

        Args:
            quantity (int): The quantity of contracts to buy.
            
        Returns:
            float: The adjusted bid price.
        """
        
        current_bid_price = self.get_bid_max_price() * 0.75 + self.get_bid_min_price() * 0.25

        if self.time.get_time() == self.time.get_close_time():
            next_bid_price = current_bid_price
        else:
            seconds_elapsed = self.get_seconds_elapsed()
            next_bid_price = self.get_bid_max_price(seconds_elapsed + 1) * 0.75 + self.get_bid_min_price(seconds_elapsed + 1) * 0.25

        price = round(min(current_bid_price, next_bid_price), 2) * quantity

        return price
    
    def get_date(self):
        return self.time.time.date()

    def get_time(self):
        return self.time.time
    
    def get_hour(self):
        return (self.time)
    
    def get_seconds_elapsed(self):
        return self.time.seconds_elapsed

    def get_name(self):
        mod_path = self.path.split('/')
        mod_path = mod_path[-2] + '/' + mod_path[-1]
        return mod_path
    
class UnderlyingAsset:
    def __init__(self, asset, path, time) -> None:
        self.asset = asset
        self.path = path
        self.time = time
        self.df = None
        
    def load_df(self):
        if self.df is None:
            self.df = pd.read_csv(self.path)
            
    def get_price(self, seconds_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if seconds_elapsed is None:
            seconds_elapsed = self.time.seconds_elapsed
            
        return self.df.iloc[seconds_elapsed]["Price"]
    
class DailyOptionChain:
    def __init__(self, asset:str, paths: str, underlying_path: str, trade_date:date, time:date, options_filter=None) -> None:
        """_summary_

        Args:
            asset (str): _description_
            paths (str): _description_
            trade_date (date): _description_
            time (date): _description_
            options_filter (func, optional): Function header - options_filter(contract: OptionContract) -> bool - returns True if contract should be included in chain, False otherwise. Defaults to None.
        """
        self.asset = asset
        self.paths = paths # list of expirations paths
        self.trade_date = trade_date
        self.contracts = None
        self.time = time
        self.options_filter = options_filter 
        
    def set_filter(self, options_filter):
        self.options_filter = options_filter
        
    def extract_contract_metadata(self, contract_path):
        properties = os.path.basename(contract_path).split(".")
        asset = properties[1]
        contract_type = Options.CALL if properties[2][0] == "C" else Options.PUT
        strike = int(properties[2][1:])
        
        if len(properties) == 6: # handles cases where strike has a decimal (cents)
            strike += int(properties[3]) / 10**len(properties[3])
            del properties[3]
                    
        expiration = datetime.strptime(properties[3], '%Y%m%d').strftime('%m/%d/%Y')
        
        return asset, contract_type, strike, expiration
    
    def load_contracts(self):
        self.contracts = []
        for expiration_path in self.paths:
            contract_paths = glob.glob(expiration_path + "/Candles*.csv")
            
            for contract_path in contract_paths:
                asset, contract_type, strike, expiration = self.extract_contract_metadata(contract_path)
                contract = OptionContract(asset, contract_type, strike, expiration, contract_path, self.time)
            
                if self.options_filter is not None:
                    if not self.options_filter(contract):
                        continue
                    
                self.contracts.append(contract)
        
    def get_contracts(self):
        if self.contracts is None:
            self.load_contracts()
        return self.contracts
    
    def set_filter(self, strike_min, strike_max, expiration_min, expiration_max):
        pass
    