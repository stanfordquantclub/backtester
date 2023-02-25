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
    def __init__(self, path, time) -> None:
        self.path = path
        self.time = time
        self.df = None
        
        properties = os.path.basename(path).split(".")
        self.asset = properties[1]
        self.type = Options.CALL if properties[2][0] == "C" else Options.PUT
        self.strike = int(properties[2][1:])
        
        if len(properties) == 6: # handles cases where strike has a decimal (cents)
            self.strike += int(properties[3]) / 10**len(properties[3])
            del properties[3]
                    
        self.expiration = datetime.strptime(properties[3], '%Y%m%d').strftime('%m/%d/%Y')

    def load_df(self):
        if self.df is None:
            self.df = pd.read_csv(self.path)

    def get_ask_price(self):
        line = self.time.seconds_elapsed + 1
        with open(self.path) as f_input:
            for row in islice(f_input, line, line + 1):
                return row
            
    def get_ask_price_df(self):
        if self.df is None:
            self.load_df()
        return self.df.iloc[self.time.seconds_elapsed]
    
    def get_time(self):
        return self.time.time
    
    def get_seconds_elapsed(self):
        return self.time.seconds_elapsed
    
class DailyOptionChain:
    def __init__(self, asset:str, paths: str, trade_date:date, time:date) -> None:
        self.asset = asset
        self.paths = paths # list of expirations paths
        self.trade_date = trade_date
        self.contracts = None
        self.time = time
        
    def load_contracts(self):
        self.contracts = []
        for expiration_path in self.paths:
            contract_paths = glob.glob(expiration_path + "/Candles*.csv")
            
            for contract_path in contract_paths:
                contract = OptionContract(contract_path, self.time)
                self.contracts.append(contract)
        
    def get_contracts(self):
        if self.contracts is None:
            self.load_contracts()
        return self.contracts
    
    def set_filter(self, strike_min, strike_max, expiration_min, expiration_max):
        pass
    
