from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.create_candles import *
import glob
import time as execution_time

# create_candles(
#   'Data/SPY.C439.20221201.csv',
#   output_path="Data/",
#   start_time=time(9, 30, 0), 
#   end_time=time(16, 0, 0)
# )

day_path = "/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221201/S/SPY/SPY.20221201"

create_candles_day(
    asset="SPY",
    day_path=day_path,
    output_path="/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221201/S/SPY/SPY.20221201/"
)

class CustomModel(Engine):
    def initialize(self):
        self.security_name = "SPY"
        
        self.start_date = date(2022, 12, 1)
        self.end_date = date(2022, 12, 18)
        
        self.root_path = "/mnt/z/srv/sqc/data/us-options-tanq"
        self.start_cash = 10**6
        
        print(self.start_date.strftime("%Y%m%d"))
        print("Custom Initialize Engine")
        pass
    
    def on_data(self, data: Slice):
        chain = data.get_chain("SPY")
        contracts = chain.get_contracts()
        
        contract = contracts[0]
        
        # open_time = time(9, 30, 0)
        
        # print(contract_time, open_time, contract_time.time() - open_time)
        t1 = execution_time.time()
        # row = contract.get_ask_price()
        # t1 = execution_time.time() - t1
        
        t2 = execution_time.time()
        row = contract.get_ask_price_df()
        t2 = execution_time.time() - t2

        print(contract.get_time(), contract.get_seconds_elapsed(), t1, t2, row["AskMin"])
        
        # print(self.time.time)
        # for contract in contracts:
        #     print(contract.asset, contract.type, contract.strike)

# model = CustomModel()
# model.back_test()
