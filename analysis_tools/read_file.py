from pandas import *
import numpy as np

def read_file(file_path):
    return read_csv(file_path)

def volume(data):
    return data['VolumeTrade'].tolist()

def total_volume(data):
    return sum(volume(data))

def quantity_bid_min(data):
    return data['QuantityBidMin'].tolist()

def quantity_bid_max(data):
    return data['QuantityBidMax'].tolist()

def quantity_ask_max(data):
    return data['QuantityAskMax'].tolist()

def bid_min(data):
    return data['BidMin'].tolist()

def bid_max(data):
    return data['BidMax'].tolist()

def ask_min(data):
    return data['AskMin'].tolist()

def ask_max(data):
    return data['AskMax'].tolist()
