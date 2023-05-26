from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.create_contract_candles import create_contract_candles_day
from src.create_contract_candles import create_contract_candles
from src.create_contract_candles import create_contract_candles_paths
from src.create_underlying_candles import create_underlying_candles, create_underlying_candles_paths
import glob
import time as execution_time
from src.data_slice import Slice
from src.portfolio import Portfolio

# create_contract_candles(
# #   'Data/SPY.C439.20221201.csv',
#     '/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20220103/S/SPY/SPY.20220103/SPY.C235.20220103.csv.gz',
#     output_path="Data/",
#     start_time=time(9, 30, 0), 
#     end_time=time(16, 0, 0)
# )

# create_contract_candles_day(
#     asset="SPY",
#     day_path=day_path,
#     output_path=day_path,
#     processes=10
# )

# create_underlying_candles(
#   '/srv/sqc/data/client-2378-luke-eq-taq/2022/20221209/S/SPY.csv',
#   output_path="/srv/sqc/data/client-2378-luke-eq-taq/2022/20221209/S/",
#   start_time=time(9, 30, 0), 
#   end_time=time(16, 0, 0)
# )

# contract_paths = glob.glob("/srv/sqc/data/us-options-tanq/us-options-tanq-2022/*/*/*/*/*.csv.gz")

# create_contract_candles_paths(contract_paths, processes=10)

underlying_paths = glob.glob("/srv/sqc/data/client-2378-luke-eq-taq/2022/*/*/*.csv.gz")
create_underlying_candles_paths(underlying_paths, processes=10)
        
class CustomModel(Engine):
    def initialize(self):
        self.add_security("SPY")
         
        self.start_date = date(2022, 12, 1)
        self.end_date = date(2022, 12, 1)
        
        '''
        1 - Luke's Laptop
        2 - Main desktop
        3 - Irfan's Laptop
        '''

        self.root_path = "/Users/lukepark/sshfs_mount/srv/sqc/data/"
        #self.root_path = "/Users/inafi/sqc/srv/sqc/data/"        
        #self.root_path = "/mnt/z/srv/sqc/data/"
        self.cash = 10**6
        
    def on_data(self, data: Slice):
        chain = data.get_chain("SPY")
        print(chain.underlying.get_price())
        
        chain.set_expiration_strike_filter(min_strike=-1, max_strike=1)
        contracts = chain.get_contracts()
        
        
        # print(chain.options_filter)
        # chain.set_expiration_strike_filter(1, 1)
        # print(chain.options_filter)
        
        # contract_0 = contracts[0]
        # print(self.time.get_time(), contract_0.get_bid_max_price(), contract_0.get_adjusted_ask(2), contract_0.get_adjusted_bid(2))

model = CustomModel()
model.back_test()
