"""
In this example, we will demonstrate how to run a backtest in parallel. This is only useful when 
you want to treat each day independently, meaning that there is no shared data between days (i.e. 
the cash and assets are reset every day).

In each day, there is an 'output' dictionary that stores whatever you want to keep track of. In this
example, we store the price of SPY every 30 increments (in this case, an increment is a minute).
"""

from datetime import date, time, datetime, timedelta
import time as execution_time
import sys
sys.path.append("../")

from backtester import Engine, Resolution, BacktestTime, Slice

class ParallelModel(Engine):
    def initialize(self):
        self.add_security("SPY")
         
        self.start_date = date(2022, 12, 5) # The start date of the backtest
        self.end_date = date(2022, 12, 15) # The end date of the backtest
        
        self.root_path = "/srv/sqc/data/" # Where the data is stored
        self.cash = 10**6
        self.resolution = Resolution.Minute # or Resolution.Second

        self.parallel = True # or True (will run on multiple cores and call on_data in parallel for different days)
        self.num_processes = 3 # Number of processes to run in parallel
        
        self.custom_var = 0
        
    def on_data(self, data: Slice, time: BacktestTime):
        chain = data.get_chain("SPY") # Get the option chain for SPY
        
        # Store the price of SPY every 30 increments (in this case, an increment is a minute)
        if time.get_time_elapsed() % 30 == 0:
            self.custom_var += 1
            
            print("Day:", time.get_time(), self.custom_var)
            
            formatted_time = time.get_time().strftime("%H:%M:%S")
            self.output[formatted_time] = chain.underlying.get_price()
    
if __name__ == "__main__":
    model = ParallelModel() # Create an instance of the model
    output = model.back_test() # Run the backtest

    # Print the output
    print("\nOutput:\n")
    
    for day in output:
        print('Day:', day)
        print(output[day])
        print()
