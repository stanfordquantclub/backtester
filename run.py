from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.utils import Slice
from src.create_candles import *
import glob

create_candles(
  'Data/SPY.C439.20221201.csv',
  output_path="Data/",
  start_time=time(9, 30, 0), 
  end_time=time(16, 0, 0)
)

# day_paths = glob.glob("/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221201/S/SPY/SPY.20221201/SPY*.csv")

# create_candles_day(
#     day_paths=day_paths,
#     output_path="/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221201/S/SPY/SPY.20221201/"
# )

# class CustomModel(Engine):
#     def initialize(self):
#         self.security_name = "SPY"
        
#         self.start_date = date(2022, 12, 1)
#         self.end_date = date(2022, 12, 18)
        
#         self.root_path = "/mnt/z/srv/sqc/data/us-options-tanq"
#         self.start_cash = 10**6
        
#         print(self.start_date.strftime("%Y%m%d"))
#         print("Custom Initialize Engine")
#         pass
    
#     def on_data(self, data: Slice):
#         print("Custom Date")
#         pass

# model = CustomModel()
# model.back_test()
