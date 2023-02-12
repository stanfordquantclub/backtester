from create_candles import create_candles
from datetime import date
from engine import Engine

# create_candles(
#   'Data/SPY.P390.20230109.csv',
#   output_path="Data/",
#   start_time=93000000, 
#   end_time=154500000
# )

start_date = date(2022, 12, 1)
end_date = date(2022, 12, 18)
# print(start_date.strftime("%Y%m%d"))

test_engine = Engine(
    security_name='SPY',
    start_cash=10**6,
    start_date=start_date,
    end_date=end_date, 
    root_path="/mnt/z/srv/sqc/data/us-options-tanq"
)

test_engine.get_data()
