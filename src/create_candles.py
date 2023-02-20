import pandas as pd
from tqdm import tqdm
import os
import numpy as np
from datetime import date, time, datetime, timedelta
import pandas_market_calendars as mcal

def create_candles_day(day_paths: str, output_path: str):
    """
    Creates the candles for every contract within a day
    """

    nyse = mcal.get_calendar('NYSE')
    
    schedule = nyse.schedule(self.start_date, self.end_date)
            
    for day_path in day_paths:
        print(day_path)
        create_candles(day_path, output_path=output_path)

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
    start_time_increment = (datetime.combine(date.today(), start_time) + timedelta(seconds=1)).time() # one second ahead
    start_time = int(start_time.strftime("%H%M%S")) * 1000
    current_time = int(start_time_increment.strftime("%H%M%S")) * 1000
    
    # Add 1 second to end time to include the last second
    end_time = (datetime.combine(date.today(), end_time) + timedelta(seconds=1)).time()
    end_time = int(end_time.strftime("%H%M%S")) * 1000
            
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        if row["Timestamp"] >= start_time and row["Timestamp"] <= end_time:
            if row["Timestamp"] < current_time:
                if not candle_has_data:
                    start_index = index
                    candle_has_data = True
            else:
                if candle_has_data:
                    candle_data = df.loc[start_index:index-1]
                    candle = [row["Date"], row["ExpirationDate"], current_time]

                    # Sum up the trade volume
                    candle.append(candle_data[candle_data["Action"] == "T"]["Quantity"].sum())
                    
                    # Select only bid data and get min
                    bid_min = candle_data[candle_data["Side"] == "B"]["Price"].min()
                    # Get the volume at the min bid price
                    quantity_bid_min = candle_data[(candle_data["Side"] == "B") & (candle_data["Price"] == bid_min)]["Quantity"].min()
                    bid_max = candle_data[candle_data["Side"] == "B"]["Price"].max()
                    quantity_bid_max = candle_data[(candle_data["Side"] == "B") & (candle_data["Price"] == bid_max)]["Quantity"].max()
                    
                    ask_min = candle_data[candle_data["Side"] == "A"]["Price"].min()
                    quantity_ask_min = candle_data[(candle_data["Side"] == "A") & (candle_data["Price"] == ask_min)]["Quantity"].min()
                    ask_max = candle_data[candle_data["Side"] == "A"]["Price"].max()
                    quantity_ask_max = candle_data[(candle_data["Side"] == "A") & (candle_data["Price"] == ask_max)]["Quantity"].max()
                    
                    metrics = [quantity_bid_min, quantity_bid_max, quantity_ask_min, quantity_ask_max, bid_min, bid_max, ask_min, ask_max]
                    
                    for metric in metrics:
                        if np.isnan(metric):
                            if len(candles) == 0: 
                                # If there are no candles yet, set the metric to 0
                                metric = 0
                            else:
                                # If there are candles, set the metric to the last candle's metric
                                metric = candles[-1][len(candle)]
                            
                        candle.append(metric)
                    
                    candles.append(candle)
                    candle_has_data = False
                else:
                    if len(candles):
                        candles.append(candles[-1].copy())
                        candles[-1][2] = current_time
                
                # Increment to the next minute
                if (current_time/1000) % 100 == 59:
                    current_time += 41000
                    
                    # Increment to the next hour
                    if (current_time/100000) % 100 == 60:
                        current_time += 4000000
                else:
                    current_time += 1000
                    
                if row["Timestamp"] < current_time:
                    if not candle_has_data:
                        start_index = index
                        candle_has_data = True
                        
    if current_time != end_time:
        end_time = 
        for i in range(current_time, end_time, 1000):
            if i < end_time:
                candles.append(candles[-1].copy())
                candles[-1][2] = i
            else:
                break
                
    df = pd.DataFrame(candles, columns=['Date', 'ExpirationDate', 'Timestamp', 'VolumeTrade', 'QuantityBidMin', 'QuantityBidMax', 'QuantityAskMin', 'QuantityAskMax', 'BidMin', 'BidMax', 'AskMin', 'AskMax'])
    df.to_csv(os.path.join(output_path, "Candles." + os.path.basename(file_path)), encoding='utf-8', index=False)
