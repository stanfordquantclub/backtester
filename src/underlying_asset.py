from datetime import date, datetime, time, timedelta
from src.backtest_time import BacktestTime
from src.resolution import *
import pandas as pd

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
            time_elapsed = 60 * (time_elapsed + 1) # Convert minute index to seconds
            
        return self.df.iloc[time_elapsed]["Price"]
