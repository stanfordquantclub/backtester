from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.create_candles import *
import glob
import time as execution_time
from src.engine import Slice

# create_contract_candles(
#   'Data/SPY.C439.20221201.csv',
#   output_path="Data/",
#   start_time=time(9, 30, 0), 
#   end_time=time(16, 0, 0)
# )

# day_path = "/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221202/S/SPY/SPY.20221202"

# create_contract_candles_day(
#     asset="SPY",
#     day_path=day_path,
#     output_path=day_path,
#     processes=2
# )

class CustomModel(Engine):
    def initialize(self):
        self.security_name = "SPY"
        
        self.start_date = date(2022, 12, 1)
        self.end_date = date(2022, 12, 2)
        
        self.root_path = "/mnt/z/srv/sqc/data/us-options-tanq"
        self.start_cash = 10**6
        
        print(self.start_date.strftime("%Y%m%d"))
        print("Custom Initialize Engine")
    
    def on_data(self, data: Slice):
        chain = data.get_chain("SPY")
        contracts = chain.get_contracts()
        
        contract = contracts[0]
        
        # row = contract.get_ask_price()
        # row = contract.get_ask_price_df()
        
        # print(contract.get_time(), contract.get_seconds_elapsed(), row["AskMin"])

model = CustomModel()
model.back_test()