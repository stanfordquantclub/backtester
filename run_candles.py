from src.create_contract_candles import create_contract_candles_paths
from src.create_underlying_candles import create_underlying_candles_paths
from datetime import date, time, datetime, timedelta

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

# paths = glob.glob("/srv/sqc/data/client-2378-luke-eq-taq/2022/*/*")
# underlying_paths = glob.glob("/srv/sqc/data/client-2378-luke-eq-taq/2022/*/*/*.csv.gz")[::-1]
# underlying_paths = []

# for path in paths:
#     if len(glob.glob(path + "/*.csv*")) == 1:
#         underlying_paths.append(glob.glob(path + "/*.csv.gz")[0])

# create_underlying_candles_paths(underlying_paths, processes=2)
        