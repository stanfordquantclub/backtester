from datetime import date, datetime, time, timedelta
from src.backtest_time import BacktestTime
import pandas as pd

class UnderlyingAsset:
    def __init__(self, asset, path, trade_date:date, time:BacktestTime) -> None:
        self.asset = asset
        self.path = path       
        self.trade_date = trade_date
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
