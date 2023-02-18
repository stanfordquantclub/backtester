from datetime import date, time, datetime, timedelta
from src.engine import Engine
from src.utils import Slice
from src.create_candles import create_candles

start_time = time(9, 30, 0)
end_time = time(16, 0, 0)

# create_candles(
#   'Data/SPY.P390.20230109.csv',
#   output_path="Data/",
#   start_time=start_time, 
#   end_time=end_time
# )

class CustomEngine(Engine):
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
        print("Custom Date")
        pass

test_engine = Engine()
custom_engine = CustomEngine()

test_engine.run()
custom_engine.run()
