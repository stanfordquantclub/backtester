import pandas as pd
from tqdm import tqdm
import os

def create_candles(file_path, output_path, start_time=93000000, end_time=160000000):
    """
    Bid-ask price min and max not including Side == T
    
    Trade Volume only including Side == T
    Bid Volume only including Side == B
    Ask Volume only including Side == A
    """    
    
    candles = []
    df = pd.read_csv(file_path)
    
    candle_has_data = False
    current_time = start_time + 1000
    start_index = 0
            
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
                    
                    # TODO: clean data from spoofing - check empty values
                    
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
                    
                    candle.extend([quantity_bid_min, quantity_bid_max, quantity_ask_min, quantity_ask_max])
                    candle.extend([bid_min, bid_max, ask_min, ask_max])
                    
                    candles.append(candle)
                    candle_has_data = False
                
                if (current_time/1000) % 100 == 59:
                    current_time += 41000
                else:
                    current_time += 1000
                    
                if row["Timestamp"] < current_time:
                    if not candle_has_data:
                        start_index = index
                        candle_has_data = True
                
    df = pd.DataFrame(candles, columns=['Date', 'ExpirationDate', 'Timestamp', 'VolumeTrade', 'QuantityBidMin', 'QuantityBidMax', 'QuantityAskMin', 'QuantityAskMax', 'BidMin', 'BidMax', 'AskMin', 'AskMax'])
    df.to_csv(os.path.join(output_path, "Candles." + os.path.basename(file_path)), encoding='utf-8', index=False)