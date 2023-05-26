from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.create_contract_candles import create_contract_candles_day
from src.create_contract_candles import create_contract_candles
from src.create_contract_candles import create_contract_candles_paths
from src.create_underlying_candles import create_underlying_candles, create_underlying_candles_paths
from src.logs import*
from src.indicators import *
import glob
import time as execution_time
from src.data_slice import Slice
from src.portfolio import Portfolio
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


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

#contract_paths = glob.glob("/srv/sqc/data/us-options-tanq/us-options-tanq-2022/*/*/*/*/*.csv.gz")
# create_contract_candles_paths(contract_paths, processes=10)

        
class CustomModel(Engine):
    def initialize(self):
        self.add_security("SPY")
         
        self.start_date = date(2022, 4, 1)
        self.end_date = date(2022, 12, 30)
        
        '''
        1 - Luke's Laptop
        2 - Main desktop
        3 - Irfan's Laptop
        '''

        self.root_path = "/Users/lukepark/sshfs_mount/srv/sqc/data/"
        #self.root_path = "/srv/sqc/data/"    
        #self.root_path = "/Users/inafi/sqc/srv/sqc/data/"        
        #self.root_path = "/mnt/z/srv/sqc/data/"
        self.cash = 50000


        self.initialize_delay = 300
        self.start_time = 1800
        self.end_time = 21600
        
        self.num_strikes_below = -5
        self.num_strikes_above = 5
        self.min_expiration = 0
        self.max_expiration = 0
        self.total_strikes = 2 * (self.max_expiration - self.min_expiration + 1) * (self.num_strikes_above - self.num_strikes_below)
        print(f"This is the number of strikes: {self.total_strikes}")

        self.all_contracts = []
        
    def on_data(self, data: Slice):
        time_index = self.get_seconds_elapsed()

        #initialize the entirety of the chain at market open
        if (self.get_seconds_elapsed() == 1):
            self.chain = data.get_chain("SPY")

        #after initial delay, use the underlying price to get all potential strikes to trade
        elif (self.get_seconds_elapsed() == self.initialize_delay):
            self.chain.set_expiration_strike_filter(self.num_strikes_below, self.num_strikes_above, self.min_expiration, self.max_expiration)
            self.contracts_today = self.chain.get_contracts()

            for contract in self.contracts_today:
                self.all_contracts.append(contract.get_name())
            



model = CustomModel()
model.back_test()

df = pd.DataFrame()
df["all_files"] = model.all_contracts
df.to_csv("/Users/lukepark/sshfs_mount/srv/sqc/volatility_exploration/all_file_names.csv")


