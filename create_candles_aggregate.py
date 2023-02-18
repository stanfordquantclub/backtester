import pandas as pd
import glob
from src.create_candles import create_candles

def create_candles_day(day_paths: str, output_path: str):
    """
    Creates the candles for every contract within a day
    """
    
    for day_path in day_paths:
        print(day_path)
        create_candles(day_path, output_path=output_path)

day_paths = glob.glob("/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221201/S/SPY/SPY.20221201/*.csv")

create_candles_day(
    day_paths=day_paths,
    output_path="/mnt/z/srv/sqc/data/us-options-tanq/us-options-tanq-2022/20221201/S/SPY/SPY.20221201/"
)