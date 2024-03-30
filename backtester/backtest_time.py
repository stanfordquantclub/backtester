from datetime import timedelta, datetime

from backtester.resolution import *

class BacktestTime:
    """
    Manages the time of the backtest with datetime objects
    """

    def __init__(self, new_time:datetime, open_time:datetime, close_time:datetime, resolution) -> None:
        self.time = new_time
        self.time_elapsed = 0
        self.open_time = open_time
        self.close_time = close_time
        self.resolution = resolution

    def set_time(self, new_time:datetime):
        self.time = new_time

    def set_open_time(self, open_time:datetime):
        self.open_time = open_time

    def set_close_time(self, close_time:datetime):
        self.close_time = close_time

    def increment(self):
        if self.resolution == Resolution.Minute:
            self.time += timedelta(minutes=1)
        else:
            self.time += timedelta(seconds=1)
            
        self.time_elapsed += 1

    def get_time(self):
        return self.time
    
    def get_open_time(self):
        return self.open_time
    
    def get_close_time(self):
        return self.close_time

    def get_time_elapsed(self):
        return self.time_elapsed

    def reset_time_elapsed(self):
        self.time_elapsed = 0
    
    def __str__(self):
        return f"BacktestTime({self.time}, {self.open_time}, {self.close_time})"
