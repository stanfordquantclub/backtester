import os
import pandas as pd
import numpy as np
import pickle


class DataLoader():
    def __init__(self, folder_path, buffer_seconds=15*60):
        self.folder_path = folder_path
        self.buffer_seconds = buffer_seconds
        self.file_paths = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    def load_volatility(self):
        '''Number,TimestampSec,PriceAskMin,PriceBidMin,QuantityAskMin,QuantityBidMin,PriceAskMax,PriceBidMax,QuantityAskMax,QuantityBidMax,Volume,Spread,Spread_As_Percentage,Delta_1_Ask, Delta_1_Ask_as_Percent,Min_Max_3600_Ask,Min_Max_3600_Ask_as_Percent,Delta_1_Volume,Min_Max_3600_Volume,Min_Max_60_Ask'''
        '''
        main inputs: Delta_1_Ask_as_Percent, Spread_As_Percentage, QuantityBidMax, QuantityAskMin
        volatility: Min_Max_3600_Ask_as_Percent
        '''
        print("----------- Loading Data ---------------")
        cache_file = './cache/volatity.pkl'
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
                
        inputs = ["QuantityBidMax", "QuantityAskMin", "momentum_60", "momentum_120"]
        labels = "Vol_10min"
        total_inputs = []
        total_labels = []

        for file in self.file_paths:
            df = pd.read_csv(os.path.join(self.folder_path, file))  
            is_valid, df = self.is_valid_filter(df)
            if is_valid:
                input_array = np.array(df[inputs].values)
                label_array = np.array(list(df[labels]))
                if len(total_inputs) == 0 and len(total_labels) == 0:
                    total_inputs = input_array
                    total_labels = label_array
                else:
                    total_inputs = np.concatenate((total_inputs, input_array), axis=0) 
                    total_labels = np.concatenate((total_labels, label_array))
        total_labels = np.abs(total_labels)
        with open(cache_file, 'wb') as f:
            pickle.dump((total_inputs, total_labels), f)

        return total_inputs, total_labels

    def is_valid_filter(self, df):
        # filter out irrelevancy
        df = df.iloc[self.buffer_seconds:]
        df = df.iloc[:-60*60]
        filter_label = "PriceAskMin"
        if df[filter_label].iloc[0] < 1:
            return False, None
        return True, df

