from datetime import timedelta, datetime

class BacktestTime:
    """
    Manages the time of the backtest with datetime objects
    """

    def __init__(self, new_time:datetime, open_time:datetime, close_time:datetime) -> None:
        self.time = new_time
        self.seconds_elapsed = 0
        self.open_time = open_time
        self.close_time = close_time

    def set_time(self, new_time:datetime):
        self.time = new_time

    def set_open_time(self, open_time:datetime):
        self.open_time = open_time

    def set_close_time(self, close_time:datetime):
        self.close_time = close_time

    def increment(self):
        self.time += timedelta(seconds=1)
        self.seconds_elapsed += 1

    def get_time(self):
        return self.time
    
    def get_open_time(self):
        return self.open_time
    
    def get_close_time(self):
        return self.close_time

    def get_seconds_elapsed(self):
        return self.seconds_elapsed

    def reset_seconds_elapsed(self):
        self.seconds_elapsed = 0
