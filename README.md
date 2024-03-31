# Backtester

This is a backtester for trading strategies. The backtester is written in Python so that it can be easily integrated with other Python libraries. 

Examples can be found in the `examples` directory.

## Installation

Install the required packages with the following command:

```bash
pip install -r requirements.txt
```

## Usage

To create a backtest, you need to create a new class that inherits the `Engine` class. 

```python
from backtester import Engine, Resolution, Slice, BacktestTime
from datetime import date

class MyStrategy(Engine):
    def initialize(self):
        self.add_security("SPY")

        self.cash = 10**5 # Initial cash

        self.start_date = date(2022, 12, 5) # Start date of the backtest
        self.end_date = date(2022, 12, 10) # End date of the backtest

        self.root_path = "/srv/sqc/data/" # Path to the data
        self.resolution = Resolution.Minute # Resolution of the data

        self.custom_var = 0 # Add custom variables here

    def on_data(self, data: Slice, time: BacktestTime):
        # Add your trading strategy here
        chain = data.get_chain("SPY") # Get the chain of the security

        underlying_price = chain.underlying.get_price() # Get the price of the underlying security

        contracts = chain.get_contracts() # Get all contracts
        
        self.custom_var += 1 # Update custom variables here

if __name__ == "__main__":
    backtest = MyStrategy()
    backtest.back_test()
```