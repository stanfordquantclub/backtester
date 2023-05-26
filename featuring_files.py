import pandas as pd
import numpy as np

def price_delta(file, column, delta):
    orig_list = file[column].tolist()
    delta_list = [round(orig_list[x + delta] - orig_list[x], 2) for x in range(len(orig_list) - delta)]

    for x in range(delta):
        delta_list.append(0)
    
    return delta_list

def price_delta_as_percent(file, column, delta):
    orig_list = file[column].tolist()
    delta_list = [round((orig_list[x + delta] - orig_list[x])/(orig_list[x] + 0.01), 2) for x in range(len(orig_list) - delta)]

    for x in range(delta):
        delta_list.append(0)
    
    return delta_list

def min_subtract_max(file, column, delta):
    orig_list = file[column].tolist()
    min_max_diff = [round(max(orig_list[x:x+delta]) - min(orig_list[x:x+delta]), 2) for x in range(len(orig_list) - delta)]

    for x in range(delta):
        min_max_diff.append(0)

    return min_max_diff

def min_subtrtact_max_as_percentage(file, column, delta):
    orig_list = file[column].tolist()
    min_max_diff = [round((max(orig_list[x:x+delta]) - min(orig_list[x:x+delta])/(orig_list[x] + 0.01)), 2) for x in range(len(orig_list) - delta)]

    for x in range(delta):
        min_max_diff.append(0)

    return min_max_diff

directory = "/Users/lukepark/sshfs_mount/srv/sqc/volatility_exploration/"
all_files_path = directory + "all_file_names.csv"

all_files = pd.read_csv(all_files_path)["all_files"]

path_to_options = "/Users/lukepark/sshfs_mount/srv/sqc/data/us-options-tanq/us-options-tanq-2022/"

def feature_data(all_paths_list):
    for index in range(len(all_paths_list)):
        file_name = all_paths_list[index]
        file_date = file_name[-12:-4]
        full_path = path_to_options + file_date + "/S/SPY/" + file_name
        file = pd.read_csv(full_path)

        ask_min = file["PriceAskMin"].tolist()
        ask_max = file["PriceAskMax"].tolist()
        bid_min = file["PriceBidMin"].tolist()
        bid_max = file["PriceBidMax"].tolist()


        file["Spread"] = [round(ask_min[x] - bid_max[x], 2) for x in range(len(ask_min))]
        file["Spread_As_Percentage"] = [round((ask_min[x] - bid_max[x])/(ask_min[x] + 0.01), 2) for x in range(len(ask_min))]
        file["Delta_1_Ask"] = price_delta(file, "PriceAskMin", 60)
        file["Delta_1_Ask_as_Percent"] = price_delta_as_percent(file, "PriceAskMin", 60)
        file["Min_Max_3600_Ask"] = min_subtract_max(file, "PriceAskMin", 3600)
        file["Min_Max_3600_Ask_as_Percent"] = min_subtrtact_max_as_percentage(file, "PriceAskMin", 3600)
        file["Delta_1_Volume"] = price_delta(file, "Volume", 5)
        file["Min_Max_3600_Volume"] = min_subtract_max(file, "Volume", 3600)
        file["Min_Max_60_Ask"] = min_subtract_max(file, "PriceAskMin", 60)

        exit_path = "/Users/lukepark/sshfs_mount/srv/sqc/volatility_exploration/featured_files/" + file_name[-17:]
        file.to_csv(exit_path)

feature_data(all_files)




