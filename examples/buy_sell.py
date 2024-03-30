from datetime import date, time, datetime, timedelta
import time as execution_time
import sys
sys.path.append("../")

from backtester import *
from datetime import date

# Create a new backtest object
class MyBacktest(Engine):
    def initialize(self):
        self.add_security("SPY")

        self.cash = 10**5 # Initial cash

        self.start_date = date(2022, 12, 5) # Start date of the backtest
        self.end_date = date(2022, 12, 5) # End date of the backtest

        self.root_path = "/srv/sqc/data/" # Path to the data
        self.resolution = Resolution.Minute # Resolution of the data

        self.custom_var = 0 # Add custom variables here

    def on_data(self, data: Slice, time: BacktestTime):
        # Add your trading strategy here
        current_time = time.get_time() # Get the current time of the backtest

        if time.get_time_elapsed() == 15:
            self.custom_var = 0
            # self.buy
        
if __name__ == "__main__":
    model = MyBacktest() # Create an instance of the model
    model.back_test() # Run the backtest