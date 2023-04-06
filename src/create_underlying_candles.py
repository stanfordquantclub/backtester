import pandas as pd
from tqdm import tqdm
import os
import numpy as np
from datetime import date, time, datetime, timedelta
import pandas_market_calendars as mcal
import pytz
import multiprocessing
import glob

def create_underlying_candles_day(asset: str, day_path: str, output_path: str, timezone:str="US/Eastern", processes=1):
    """
    Creates the candles for every contract within a day
    
    Args:
        asset (str): name of the asset
        day_path (str): path to the day
        output_path (str): path to the output
        timezone (str): timezone to use for the candles
    """
    
    def create_underlying_candles_day_paths(contract_paths, output_path, open_time, close_time):
        for contract_path in contract_paths:
            create_underlying_candles(
                contract_path, 
                output_path=output_path,
                start_time=open_time, 
                end_time=close_time
            )

    nyse = mcal.get_calendar('NYSE')
    
    index = day_path.split("/").index("us-options-tanq")
    day = day_path.split("/")[index+2]
    schedule = nyse.schedule(day, day)
    
    schedule["market_open"] = schedule["market_open"].dt.tz_convert(pytz.timezone(timezone))
    schedule["market_close"] = schedule["market_close"].dt.tz_convert(pytz.timezone(timezone))
    
    open_time = schedule["market_open"].iloc[0].time()
    close_time = schedule["market_close"].iloc[0].time()
    
    contract_paths = glob.glob(f"{day_path}/{asset}*.csv")
    contract_paths = np.array_split(contract_paths, processes)
    
    for process_index in range(processes):
        process = multiprocessing.Process(target=create_underlying_candles_day_paths, args=(contract_paths[process_index], output_path, open_time, close_time))
 
        process.start()

def create_underlying_candles(file_path, output_path, start_time=time(9, 30, 0), end_time=time(16, 0, 0)):
    """
    Args:
        file_path (str): path to the file to create candles from
        output_path (str): path to the output directory - file will be name Candles.<file_name>.csv
        start_time (datetime.time): start time of the candles in milliseconds
        end_time (datetime.time): end time of the candles in milliseconds
    """    
    
    df = pd.read_csv(file_path)

    # Convert to milliseconds
    start_datetime = datetime.combine(date.today(), start_time) + timedelta(seconds=1)
    start_time = int(start_time.strftime("%H%M%S")) * 1000

    # Add 1 second to end time to include the last second
    end_datetime = datetime.combine(date.today(), end_time) + timedelta(seconds=1)
    end_time = int(end_datetime.strftime("%H%M%S")) * 1000

    # FILTER OUT ITEMS FROM PRE-MARKET AND POST-MARKET
    df["TimestampSec"] = pd.to_numeric(df["Timestamp"].str.slice(stop=8).str.replace(
    df = df[(df["TimestampSec"] >= start_time * 1000) & (df["TimestampSec"] < end_time * 1000)]
    total_seconds = int((end_datetime - start_datetime).total_seconds())
    
    CLOCK_HOURS = np.array([int((start_datetime + timedelta(seconds=x)).time().strftime("%H%M%S")) for x in range(0, total_seconds)])

    df_median_price =  (df.groupby(df['TimestampSec'])['Price'].median()
                        .reindex(pd.Index(CLOCK_HOURS))
                        .fillna(method='ffill'))

    df_median_price.to_csv(os.path.join(output_path, "Candles." + os.path.basename(file_path)), encoding='utf-8', index_label='TimestampSec')
