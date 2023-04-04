from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.create_candles import *
import glob
import time as execution_time
from src.engine import Slice
from src.portfolio import Portfolio

# create_candles(
#   'Data/SPY.C439.20221201.csv',
#   output_path="Data/",
#   start_time=time(9, 30, 0), 
#   end_time=time(16, 0, 0)
# )

# day_path = "/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221202/S/SPY/SPY.20221202"

# create_candles_day(
#     asset="SPY",
#     day_path=day_path,
#     output_path=day_path,
#     processes=2
# )

class CustomModel(Engine):
    def initialize(self):
        self.security_name = "SPY"
        
        self.start_date = date(2022, 12, 1)
        self.end_date = date(2022, 12, 1)
        
        self.root_path = "/Users/lukepark/sshfs_mount/srv/sqc/data/us-options-tanq"
        #self.root_path = "/srv/sqc/data/us-options-tanq"
        self.start_cash = 10**6
        
        return self.start_cash

    def on_data(self, data: Slice):
        chain = data.get_chain("SPY")
        contracts = chain.get_contracts()
        
        contract_0 = contracts[75]
        contract_1 = contracts[70]

        '''        
        if (self.get_seconds_elapsed() != 0 and self.get_seconds_elapsed() % 3600 == 0
            and self.get_seconds_elapsed() % 7200 != 0):
            self.buy(contract_1, 10)
            print(self.portfolio.summary())

        if (self.get_seconds_elapsed() != 0 and self.get_seconds_elapsed() % 7200 == 0):
            self.buy(contract_0, 10)
            print(self.portfolio.summary())
        
        if (self.get_seconds_elapsed() == 23000):
            self.sell(contract_0, 40)
            print(self.portfolio.summary())
        '''

        if (self.get_seconds_elapsed() == 3600):
            self.buy(contract_1, 10)
            self.buy(contract_0, 10)
            self.sell(contract_0, 5)
            print(self.logs.get_ordered())




            

        
        


model = CustomModel()
model.back_test()



