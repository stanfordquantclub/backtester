from datetime import date, time, datetime, timedelta
import time as execution_time
import sys

sys.path.append("../")
from src.engine import Engine
from src.resolution import *
from src.data_slice import Slice
from src.backtest_time import BacktestTime
from src.portfolio import Portfolio

class CustomModel(Engine):
    def initialize(self):
        self.add_security("SPY")
         
        self.start_date = date(2022, 12, 5)
        self.end_date = date(2022, 12, 15)
        
        self.root_path = "/srv/sqc/data/"
        self.cash = 10**6
        
        self.parallel = False
        
    def on_data(self, data: Slice, time: BacktestTime):
        chain = data.get_chain("SPY")
        print(time.get_time(), chain.underlying.get_price())
        
        chain.set_expiration_strike_filter(min_strike=-3, max_strike=3)
        contracts = chain.get_contracts()
        contracts.sort(key=lambda x: x.get_strike())
        
        for contract in contracts:
            print(contract.get_contract_type(), contract.get_strike(), contract.get_bid_max_price(), contract.get_ask_min_price())

if __name__ == "__main__":
    model = CustomModel()
    model.back_test()
