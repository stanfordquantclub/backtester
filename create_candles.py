import pandas as pd
from tqdm import tqdm
import os
import numpy as np

def create_candles(file_path, output_path, start_time=93000000, end_time=160000000):
    """
    Description:
        Bid-ask price min and max not including Side == T
        Trade Volume only including Side == T
        Bid Volume only including Side == B
        Ask Volume only including Side == A
    
    Args:
        file_path (str): path to the file to create candles from
        output_path (str): path to the output directory - file will be name Candles.<file_name>.csv
        start_time (int): start time of the candles in milliseconds
        end_time (int): end time of the candles in milliseconds
    """    
    
    candles = []
    df = pd.read_csv(file_path)
    
    candle_has_data = False
    current_time = start_time + 1000
    start_index = 0
            
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        if row["Timestamp"] >= start_time and row["Timestamp"] <= end_time + 1000:
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
                
                if (current_time/1000) % 100 == 59:
                    current_time += 41000
                else:
                    current_time += 1000
                    
                # Increment to the next hour
                if (current_time/100000) % 100 == 60:
                    current_time += 4000000
                    
                if row["Timestamp"] < current_time:
                    if not candle_has_data:
                        start_index = index
                        candle_has_data = True
                
    df = pd.DataFrame(candles, columns=['Date', 'ExpirationDate', 'Timestamp', 'VolumeTrade', 'QuantityBidMin', 'QuantityBidMax', 'QuantityAskMin', 'QuantityAskMax', 'BidMin', 'BidMax', 'AskMin', 'AskMax'])
    df.to_csv(os.path.join(output_path, "Candles." + os.path.basename(file_path)), encoding='utf-8', index=False)
