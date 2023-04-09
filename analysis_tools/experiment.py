import indicators as ind
import read_file as rf
from graphs import *

path_0 = "/Users/lukepark/Documents/Sample_data/Candles.SPY.C405.20221201.csv"
path_1 = "/Users/lukepark/Documents/Sample_data/Candles.SPY.P414.20221201.csv"

data_0 = rf.read_file(path_0)
data_1 = rf.read_file(path_1)

def processing(data):
    calls_asks_velocities = ind.vel_list(rf.bid_max(data))
    calls_asks_short_momentum = [0 for num in range(60)] + [ind.weighted_momentum(calls_asks_velocities[0:num], 60) for num in range(60, len(calls_asks_velocities))]
    calls_asks_long_momentum = [0 for num in range(300)] + [ind.weighted_momentum(calls_asks_velocities[0:num], 300) for num in range(300, len(calls_asks_velocities))]
    #calls_asks_impulse_short = [0 for num in range(60)] + [ind.simple_momentum(calls_asks_short_momentum[0:num], 60) for num in range(60, len(calls_asks_short_momentum))]
    #calls_asks_impulse_long = [0 for num in range(60)] + [ind.simple_momentum(calls_asks_long_momentum[0:num], 60) for num in range(60, len(calls_asks_long_momentum))]

    return {"calls_asks_velocities": calls_asks_velocities, "calls_asks_short_momentum": calls_asks_short_momentum, "calls_asks_long_momentum": calls_asks_long_momentum}

processed_data_1 = processing(data_1)
simple_graph(rf.bid_max(data_1)[1200:5400])
simple_graph(processed_data_1["calls_asks_long_momentum"][1200:1800])
simple_graph(processed_data_1["calls_asks_short_momentum"])