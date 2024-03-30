from datetime import date, time, datetime, timedelta
import time as execution_time
import sys
sys.path.append("../")

from backtester import Engine, Resolution, BacktestTime, Slice

class ParallelModel(Engine):
    def initialize(self):
        self.add_security("SPY")
         
        self.start_date = date(2022, 12, 5) # The start date of the backtest
        self.end_date = date(2022, 12, 10) # The end date of the backtest
        
        self.root_path = "/srv/sqc/data/" # Where the data is stored
        self.cash = 10**6
        self.resolution = Resolution.Minute # or Resolution.Second

        self.parallel = True # or True (will run on multiple cores and call on_data in parallel for different days)
        self.num_processes = 6 # Number of processes to run in parallel
        
    def on_data(self, data: Slice, time: BacktestTime):
        chain = data.get_chain("SPY") # Get the option chain for SPY
        
        # Store the price of SPY every 30 increments (in this case, an increment is a minute)
        if time.get_time_elapsed() % 30 == 0:
            formatted_time = time.get_time().strftime("%H:%M:%S")
            self.output[formatted_time] = chain.underlying.get_price()
    
if __name__ == "__main__":
    model = ParallelModel() # Create an instance of the model
    output = model.back_test() # Run the backtest

    # Print the output
    for day in output:
        print('Day:', day)
        print(output[day])
        print()
