import sys
import glob
import pandas as pd
from itertools import islice
from collections import OrderedDict
import os
import math
import pandas_market_calendars as mcal
from datetime import date, datetime, time, timedelta

from backtester.resolution import *
from backtester.backtest_time import BacktestTime
from backtester.underlying_asset import UnderlyingAsset

class Options:
    CALL = 0
    PUT = 1
        
class OptionContract:
    def __init__(self, asset:str, contract_type:Options, strike:int, expiration: date, path:str, time: BacktestTime) -> None:
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
            
    def get_contract_type(self):
        return self.contract_type
            
    def get_strike(self):
        return self.strike
    
    def get_expiration(self):
        return self.expiration

    def get_data_no_df(self):
        line = self.time.time_elapsed + 1
        with open(self.path) as f_input:
            for row in islice(f_input, line, line + 1):
                return row
            
    def get_bid_min_price(self, time_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if time_elapsed is None:
            time_elapsed = self.time.time_elapsed
            
        return self.df.iloc[time_elapsed]["PriceBidMin"]
            
    def get_bid_max_price(self, time_elapsed=None):
        if self.df is None:
            self.load_df()

        if time_elapsed is None:
            time_elapsed = self.time.time_elapsed

        return self.df.iloc[time_elapsed]["PriceBidMax"]
            
    def get_ask_min_price(self, time_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if time_elapsed is None:
            time_elapsed = self.time.time_elapsed
            
        return self.df.iloc[time_elapsed]["PriceAskMin"]
    
    def get_ask_max_price(self, time_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if time_elapsed is None:
            time_elapsed = self.time.time_elapsed
            
        return self.df.iloc[time_elapsed]["PriceAskMax"]
    
    def get_adjusted_ask(self, quantity:int=1)->None:
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
            time_elapsed = self.get_time_elapsed()
            next_ask_price = self.get_ask_min_price(time_elapsed + 1) * 0.75 + self.get_ask_max_price(time_elapsed + 1) * 0.25

        price = round(max(current_ask_price, next_ask_price), 2) * quantity

        return price * 100 # 100 shares per contract

    def get_adjusted_bid(self, quantity:int=1)->None:
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
            time_elapsed = self.get_time_elapsed()
            next_bid_price = self.get_bid_max_price(time_elapsed + 1) * 0.75 + self.get_bid_min_price(time_elapsed + 1) * 0.25

        price = round(min(current_bid_price, next_bid_price), 2) * quantity

        return price * 100 # 100 shares per contract
    
    def get_date(self):
        return self.time.time.date()

    def get_time(self):
        return self.time.time
    
    def get_hour(self):
        return (self.time)
    
    def get_time_elapsed(self):
        return self.time.time_elapsed

    def get_name(self):
        mod_path = self.path.split('/')
        mod_path = mod_path[-2] + '/' + mod_path[-1]
        return mod_path
    
    def __sizeof__(self):
        size = sys.getsizeof(self.asset)
        size += sys.getsizeof(self.contract_type)
        size += sys.getsizeof(self.strike)
        size += sys.getsizeof(self.expiration)
        size += sys.getsizeof(self.path)
        size += sys.getsizeof(self.time)
        
        if self.df is not None:
            size += sys.getsizeof(self.df)
            size += self.df.memory_usage().sum()

        return int(size)
    
class DailyOptionChain:
    def __init__(self, asset:str, paths: str, underlying: UnderlyingAsset, trade_date:date, time:BacktestTime, resolution, options_filter=None) -> None:
        """_summary_

        Args:
            asset (str): _description_
            paths (str): _description_
            trade_date (date): _description_
            time (BacktestTime): _description_
            options_filter (func, optional): Function header - options_filter(contract: OptionContract) -> bool - returns True if contract should be included in chain, False otherwise. Defaults to None.
        """
        
        self.asset = asset
        self.paths = paths # list of expirations paths
        self.underlying = underlying
        self.trade_date = trade_date
        self.contracts = None
        self.time = time
        self.resolution = resolution
        self.options_filter = options_filter 
        
    def set_filter(self, options_filter):
        self.options_filter = options_filter
        
    def set_expiration_strike_filter(self, min_strike:int=None, max_strike:int=None, min_expiration:int=None, max_expiration:int=None):
        """
        Set filters based on strike and expiration.
        
        Args:
            min_strike (int): The minimum strike distance from the underlying price (inclusive)
            max_strike (int): The maximum strike distance from the underlying price (inclusive)
            min_expiration (int): The minimum number of days until expiration (inclusive)
            max_expiration (int): The maximum number of days until expiration (inclusive)
        """
        def contract_filter(contract):
            if min_strike is not None and self.strike_distance(contract.strike, 1) < min_strike:
                return False
            
            if max_strike is not None and self.strike_distance(contract.strike, 1) > max_strike:
                return False
            
            if min_expiration is not None and (contract.get_expiration().date() - self.time.get_time().date()).days < min_expiration:
                return False
            
            if max_expiration is not None and (contract.get_expiration().date() - self.time.get_time().date()).days > max_expiration:
                return False
            
            return True
            
        self.set_filter(contract_filter)
    
    def strike_distance(self, contract_strike, strike_width)->int:
        """
        Get's the strike distance of the given strike number from the underlying price
        """
        
        distance = (contract_strike - self.underlying.get_price()) / strike_width

        if distance < 0:
            distance = math.floor(distance)
        else:
            distance = math.ceil(distance)

        return distance

    def get_underlying_price(self):
        return self.underlying.get_price()

    def extract_contract_metadata(self, contract_path):
        properties = os.path.basename(contract_path).split(".")
        asset = properties[1]
        contract_type = Options.CALL if properties[2][0] == "C" else Options.PUT
        strike = int(properties[2][1:])
        
        if len(properties) == 6: # handles cases where strike has a decimal (cents)
            strike += int(properties[3]) / 10**len(properties[3])
            del properties[3]
                    
        expiration = datetime.strptime(properties[3], '%Y%m%d')
        
        return asset, contract_type, strike, expiration
    
    def load_contracts(self):
        self.contracts = []
        for expiration_path in self.paths:
            if self.resolution == Resolution.Minute:
                contract_paths = glob.glob(os.path.join(expiration_path + "/Candles_minutes.*.csv"))
            else:
                contract_paths = glob.glob(os.path.join(expiration_path + "/Candles.*.csv"))
            
            for contract_path in contract_paths:
                asset, contract_type, strike, expiration = self.extract_contract_metadata(contract_path)
                contract = OptionContract(asset, contract_type, strike, expiration, contract_path, self.time)
            
                self.contracts.append(contract)
        
    def get_contracts(self):
        if self.contracts is None:
            self.load_contracts()
        
        if self.options_filter is not None:
            contracts = [contract for contract in self.contracts if self.options_filter(contract)]
            return contracts
            
        return self.contracts
    
    def __sizeof__(self):
        # Recursively get the size of all the contracts
        size = sys.getsizeof(self.asset)
        size += sys.getsizeof(self.paths)
        size += sys.getsizeof(self.underlying)
        size += sys.getsizeof(self.trade_date)
        size += sys.getsizeof(self.time)
        size += sys.getsizeof(self.resolution)
        
        for contract in self.contracts:
            size += sys.getsizeof(contract)
            
        return size
