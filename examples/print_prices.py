from datetime import date, time, datetime, timedelta
import time as execution_time
import sys
sys.path.append("../")

from backtester import Engine, Resolution, BacktestTime, Slice

class CustomModel(Engine):
    def initialize(self):
        self.add_security("SPY")
         
        self.start_date = date(2022, 12, 5) # The start date of the backtest
        self.end_date = date(2022, 12, 15) # The end date of the backtest
        
        self.root_path = "/srv/sqc/data/" # Where the data is stored
        self.cash = 10**6
        self.resolution = Resolution.Minute # or Resolution.Second

        self.parallel = False # or True (will run on multiple cores and call on_data in parallel for different days)
        
    def on_data(self, data: Slice, time: BacktestTime):
        chain = data.get_chain("SPY") # Get the option chain for SPY
        print(time.get_time(), chain.underlying.get_price()) # Print the time and the price of the underlying
        
        chain.set_expiration_strike_filter(min_strike=-3, max_strike=3) # Filter the contracts to only include strikes between -3 and 3
        contracts = chain.get_contracts() # Get the contracts
        contracts.sort(key=lambda x: x.get_strike()) # Sort the contracts by strike
        
        # Print the contract type, strike, bid price, and ask price
        for contract in contracts:
            print(contract.get_contract_type(), contract.get_strike(), contract.get_bid_max_price(), contract.get_ask_min_price())

if __name__ == "__main__":
    model = CustomModel() # Create an instance of the model
    model.back_test() # Run the backtest
