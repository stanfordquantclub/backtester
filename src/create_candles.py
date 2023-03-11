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

    # Convert to milliseconds
    start_time = int(start_time.strftime("%H%M%S")) * 1000

    # Add 1 second to end time to include the last second
    end_time = (datetime.combine(date.today(), end_time) + timedelta(seconds=1)).time()
    end_time = int(end_time.strftime("%H%M%S")) * 1000

    # FILTER OUT ITEMS FROM PRE-MARKET AND POST-MARKET
    df["TimestampSec"] = df["Timestamp"] // 1000
    df = df[(df["Timestamp"] >= start_time) & (df["Timestamp"] < end_time)]


    CLOCK_HOURS = np.arange(93000,160001)

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