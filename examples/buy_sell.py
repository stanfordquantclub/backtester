from datetime import date, time, datetime, timedelta
import time as execution_time
import sys
sys.path.append("../")

from backtester import Engine, Resolution, BacktestTime, Slice, Options
from datetime import date

class MyBacktest(Engine):
    def initialize(self):
        self.add_security("SPY")

        self.cash = 10**5 # Initial cash

        self.start_date = date(2022, 12, 5) # Start date of the backtest
        self.end_date = date(2022, 12, 6) # End date of the backtest

        self.root_path = "/srv/sqc/data/" # Path to the data
        self.resolution = Resolution.Minute # Resolution of the data

        self.custom_var = [] # Add custom variables here

    def on_data(self, data: Slice, time: BacktestTime):
        # Add your trading strategy here
        chain = data.get_chain("SPY") # Get the option chain for SPY

        # Buy calls 15 increments after open (in this case, an increment is a minute)
        if time.get_time_elapsed() == 15:
            print("Open time:", time.get_open_time())
            # Filter contracts to only have contracts with one strike above and below
            chain.set_expiration_strike_filter(min_strike=-1, max_strike=1) 

            contracts = chain.get_contracts() # Get the contracts (called after the filter is set)
            
            # Buy calls
            print("Buying calls")
            for contract in contracts:
                if contract.get_contract_type() == Options.CALL:
                    print("Underlying price:", chain.underlying.get_price())
                    print(f"Strike: {contract.get_strike()} Bid: {contract.get_bid_max_price()} Ask: {contract.get_ask_min_price()}")

                    self.buy(contract, 5) # Buy 5 call contracts
                    
                    print("Cash remaining:", self.get_cash())
                    print()
                    
        # Sell calls 15 increments before close
        if time.get_time_to_close() == 15:
            contracts = chain.get_contracts()
            
            # Get the assets in the portfolio
            asset_names = list(self.portfolio.get_assets().keys())

            # Sell calls
            print("Selling calls")
            for contract in asset_names:
                print("Underlying price:", chain.underlying.get_price())
                print(f"Strike: {contract.get_strike()} Bid: {contract.get_bid_max_price()} Ask: {contract.get_ask_min_price()}")

                self.sell(contract, 5)
                
                # Remove the contract from the custom variable
                print("Cash remaining:", self.get_cash())
                print()
                
            print()
                
if __name__ == "__main__":
    model = MyBacktest() # Create an instance of the model
    model.back_test() # Run the backtest
