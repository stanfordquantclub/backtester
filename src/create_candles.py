import pandas as pd
from tqdm import tqdm
import os
import numpy as np
from datetime import date, time, datetime, timedelta
import pandas_market_calendars as mcal
import pytz
import multiprocessing
import glob

def create_candles_day(asset: str, day_path: str, output_path: str, timezone:str="US/Eastern", processes=1):
    """
    Creates the candles for every contract within a day
    
    Args:
        asset (str): name of the asset
        day_path (str): path to the day
        output_path (str): path to the output
        timezone (str): timezone to use for the candles
    """
    
    def create_candles_day_paths(contract_paths, output_path, open_time, close_time):
        for contract_path in contract_paths:
            create_candles(
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
        process = multiprocessing.Process(target=create_candles_day_paths, args=(contract_paths[process_index], output_path, open_time, close_time))
 
        process.start()

def create_candles(file_path, output_path, start_time=time(9, 30, 0), end_time=time(16, 0, 0)):
    """
    Description:
        Bid-ask price min and max not including Side == T
        Trade Volume only including Side == T
        Bid Volume only including Side == B
        Ask Volume only including Side == A
    
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
    df["TimestampSec"] = df["Timestamp"] // 1000
    df = df[(df["Timestamp"] >= start_time) & (df["Timestamp"] < end_time)]
    total_seconds = int((end_datetime - start_datetime).total_seconds())
    
    CLOCK_HOURS = np.array([int((start_datetime + timedelta(seconds=x)).time().strftime("%H%M%S")) for x in range(0, total_seconds)])

    df_min_price =  (df.loc[df.groupby([df['Side'], df['TimestampSec']])['Price'].idxmin()]
                            [['TimestampSec','Side','Price','Quantity']]
                        .set_index(['Side', 'TimestampSec'])
                        .reindex(pd.MultiIndex.from_product([['A','B'], CLOCK_HOURS]))
                        .fillna(method='ffill')
                        .unstack(level=0)
                        .pipe(lambda d: (setattr(d, 'columns', [' '.join(col).strip() for col in d.columns.values]), d)[1])
                        .rename(columns={"Price A": "PriceAskMin", "Price B": "PriceBidMin", "Quantity A": "QuantityAskMin", "Quantity B": "QuantityBidMin"}))
    
    df_max_price =  (df.loc[df.groupby([df['Side'], df['TimestampSec']])['Price'].idxmax()]
                            [['TimestampSec','Side','Price','Quantity']]
                        .set_index(['Side', 'TimestampSec'])
                        .reindex(pd.MultiIndex.from_product([['A','B'], CLOCK_HOURS]))
                        .fillna(method='ffill')
                        .unstack(level=0)
                        .pipe(lambda d: (setattr(d, 'columns', [' '.join(col).strip() for col in d.columns.values]), d)[1])
                        .rename(columns={"Price A": "PriceAskMax", "Price B": "PriceBidMax", "Quantity A": "QuantityAskMax", "Quantity B": "QuantityBidMax"}))
    
    df_all = pd.merge(df_min_price,df_max_price, left_index=True, right_index=True)
    
    df_action_T = df[df['Action'] == 'T']
    df_volume = (df_action_T.groupby(df_action_T['TimestampSec'])['Quantity']
                            .sum()
                            .to_frame()
                            .reindex(CLOCK_HOURS)
                            .fillna(method='ffill')
                            .rename(columns={"Quantity": "Volume"}))
    
    df_all = pd.merge(df_all, df_volume, left_index=True, right_index=True)

    df_all.to_csv(os.path.join(output_path, "Candles." + os.path.basename(file_path)), encoding='utf-8', index_label='TimestampSec')
