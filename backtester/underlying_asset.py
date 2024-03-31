from datetime import date, datetime, time, timedelta
import pandas as pd
import sys

from backtester.backtest_time import BacktestTime
from backtester.resolution import Resolution

class UnderlyingAsset:
    def __init__(self, asset, path, trade_date:date, time:BacktestTime, resolution) -> None:
        self.asset = asset
        self.path = path       
        self.trade_date = trade_date
        self.time = time
        self.df = None
        self.resolution = resolution
        
    def load_df(self):
        if self.df is None:
            self.df = pd.read_csv(self.path)
            
    def get_price(self, time_elapsed=None):
        if self.df is None:
            self.load_df()
            
        if time_elapsed is None:
            time_elapsed = self.time.time_elapsed

        if self.resolution == Resolution.Minute:
            time_elapsed = 60 * (time_elapsed + 1) - 1 # Minute is forward looking, so 1st minute is 0-59, 2nd minute is 60-119, etc.

        return self.df.iloc[time_elapsed]["Price"]

    def __sizeof__(self):
        size = sys.getsizeof(self.asset)
        size += sys.getsizeof(self.path)
        size += sys.getsizeof(self.trade_date)
        size += sys.getsizeof(self.time)
        size += sys.getsizeof(self.df)
        size += sys.getsizeof(self.resolution)
        size += self.df.memory_usage().sum()
        
        return int(size)
    