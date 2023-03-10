import pandas as pd
from tqdm import tqdm
import os
import numpy as np
from datetime import date, time, datetime, timedelta

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

    candle_has_data = False
    candles = []
    start_index = 0
    
    # Convert to milliseconds
    start_time = int(start_time.strftime("%H%M%S")) * 1000
    current_time = start_time

    # Add 1 second to end time to include the last second
    end_time = (datetime.combine(date.today(), end_time) + timedelta(seconds=1)).time()
    end_time = int(end_time.strftime("%H%M%S")) * 1000

    # FILTER OUT ITEMS FROM PRE-MARKET AND POST-MARKET
    df = df[(df["Timestamp"] >= start_time) & (df["Timestamp"] <= end_time)].reset_index()

    df["TimestampSec"] = df["Timestamp"] // 1000

    df_min_price =  (df.iloc[df.groupby([df['Side'], df['TimestampSec']])['Price'].idxmin()]
                            [['TimestampSec','Side','Price','Quantity']]
                        .set_index(['Side', 'TimestampSec'])
                        .reindex(pd.MultiIndex.from_product([['A','B'], np.arange(93000,160001)]))
                        .fillna(method='ffill')
                        .rename(columns={"Price"}))
    
    df_max_price =  (df.iloc[df.groupby([df['Side'], df['TimestampSec']])['Price'].idxmax()]
                            [['TimestampSec','Side','Price','Quantity']]
                        .set_index(['Side', 'TimestampSec'])
                        .reindex(pd.MultiIndex.from_product([['A','B'], np.arange(93000,160001)]))
                        .fillna(method='ffill'))
    

    print(df_min_price)

    # df = pd.DataFrame(candles, columns=['Date', 'ExpirationDate', 'Timestamp', 'VolumeTrade', 'QuantityBidMin', 'QuantityBidMax', 'QuantityAskMin', 'QuantityAskMax', 'BidMin', 'BidMax', 'AskMin', 'AskMax'])
    # df.to_csv(os.path.join(output_path, "Candles." + os.path.basename(file_path)), encoding='utf-8', index=False)
